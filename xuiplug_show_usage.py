#!/usr/bin/env python3
#

#Crontab  添加命令
# */10 * * * * flock -n /tmp/xui_usage.lock python3 /usr/local/x-ui/plugs/xuiplug_show_usage.py >> /var/log/xui_usage.log 2>&1


import sqlite3
import sys
import os
import time
import json
import configparser
from datetime import datetime
import requests

CONFIG_FILE = "/usr/local/x-ui/plugs/config/xuiplugconf.ini"

# ===== 读取配置 =====
cfg = configparser.ConfigParser()
cfg.read(CONFIG_FILE)

conf = cfg["XUIUSAGE"]

ENABLED = conf.getboolean("enabled", True)
DEFAULT_DB = conf.get("default_db_path", "/etc/x-ui/x-ui.db")

SHOW_REMAIN = conf.getboolean("show_remaining_when_limited", True)
THRESHOLD = conf.getint("mb_to_gb_threshold", 1024)
DECIMALS = conf.getint("gb_decimal_places", 2)

TG_ENABLE = conf.getboolean("telegram_daily_enable", False)
TG_TIME = conf.get("telegram_daily_time", "09:00")
TG_USE_DB = conf.getboolean("telegram_use_db_config", True)
TG_TITLE = conf.get("telegram_summary_title", "XUI Usage")

TG_TOKEN_OVERRIDE = conf.get("telegram_bot_token", "").strip()
TG_CHAT_OVERRIDE = conf.get("telegram_chat_id", "").strip()

STATE_FILE = conf.get("state_file", "/var/tmp/xui_usage_state.json")

# ===== 工具函数 =====
def format_size(mb):
    if mb >= THRESHOLD:
        return f"{mb/1024:.{DECIMALS}f}GB"
    return f"{int(mb)}MB"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

# ===== Telegram =====
def get_telegram_config(cursor):
    if not TG_USE_DB:
        return TG_TOKEN_OVERRIDE, TG_CHAT_OVERRIDE

    rows = cursor.execute("SELECT key, value FROM settings").fetchall()
    data = {k: v for k, v in rows}

    token = TG_TOKEN_OVERRIDE or data.get("tgBotToken")
    chat = TG_CHAT_OVERRIDE or data.get("tgBotChatId")

    return token, chat

def send_telegram(token, chat_id, text):
    if not token or not chat_id:
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)
        return True
    except:
        return False

# ===== 主逻辑 =====
def main():
    if not ENABLED:
        return

    db_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DB
    if not os.path.exists(db_path):
        print(f"DB not found: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    inbounds = cursor.execute(
        "SELECT id, remark, up, down, total FROM inbounds"
    ).fetchall()

    summary_lines = []
    updated = 0

    for id_, remark, up, down, total in inbounds:
        remark = remark or ""
        used_mb = (up + down) / 1024 / 1024
        used = format_size(used_mb)

        base = remark.split("_◔")[0]
        base = base.split("_")[0]  # 防止旧时间残留
        timestamp = datetime.now().strftime("%d%H%M")

        if total != 0:
            total_mb = total / 1024 / 1024
            remain_mb = max(total_mb - used_mb, 0)
            remain = format_size(remain_mb)

            new_remark = f"{base}_{timestamp}_◔{used}◕{remain}"
        else:
            new_remark = f"{base}_{timestamp}_◔{used}"

        summary_lines.append(new_remark)

        if remark != new_remark:
            cursor.execute(
                "UPDATE inbounds SET remark=? WHERE id=?",
                (new_remark, id_)
            )
            updated += 1

    conn.commit()

    # ===== Telegram 每日发送 =====
    if TG_ENABLE:
        state = load_state()
        today = datetime.now().strftime("%Y-%m-%d")
        now_time = datetime.now().strftime("%H:%M")

        if today != state.get("last_send_date") and now_time >= TG_TIME:
            token, chat = get_telegram_config(cursor)

            message = TG_TITLE + "\n\n" + "\n".join(summary_lines)

            if send_telegram(token, chat, message):
                state["last_send_date"] = today
                save_state(state)
                print("Telegram sent")

    print(f"{datetime.now()} OK updated={updated}")

if __name__ == "__main__":
    main()
