#!/bin/bash

SRC_DB="./x-ui.db"
DEFAULT_DIRECT_DB="/etc/x-ui/x-ui.db"
DEFAULT_DOCKER_DB="/opt/3x-ui/db/x-ui.db"
WORK_DB="/tmp/x-ui-work-$(date +%F-%H%M%S).db"

TARGET_DB="$DEFAULT_DIRECT_DB"
CONTAINER_NAME=""

echo "======================================"
echo "  3x-ui 安装检查 + 数据库迁移 + 域名更新"
echo "======================================"
echo

if [ "$(id -u)" -ne 0 ]; then
    echo "错误：请使用 root 用户运行。"
    exit 1
fi

if [ ! -f "$SRC_DB" ]; then
    echo "错误：当前目录没有 x-ui.db"
    exit 1
fi

install_sqlite_if_needed() {
    if ! command -v sqlite3 >/dev/null 2>&1; then
        echo "正在安装 sqlite3..."
        apt update && apt install sqlite3 curl -y
    fi
}

find_xui_container() {
    if command -v docker >/dev/null 2>&1; then
        docker ps -a --format '{{.Names}}' 2>/dev/null | grep -Ei '(x-ui|xui)' | head -n 1
    fi
}

is_xui_installed() {
    command -v x-ui >/dev/null 2>&1 && return 0

    if [ -n "$(find_xui_container)" ]; then
        return 0
    fi

    [ -f "$DEFAULT_DIRECT_DB" ] && return 0
    [ -f "$DEFAULT_DOCKER_DB" ] && return 0

    return 1
}

detect_target_db() {
    CONTAINER_NAME="$(find_xui_container)"

    if [ -n "$CONTAINER_NAME" ]; then
        if [ -f "$DEFAULT_DOCKER_DB" ]; then
            TARGET_DB="$DEFAULT_DOCKER_DB"
        elif [ -f "$DEFAULT_DIRECT_DB" ]; then
            TARGET_DB="$DEFAULT_DIRECT_DB"
        fi
    elif [ -f "$DEFAULT_DIRECT_DB" ]; then
        TARGET_DB="$DEFAULT_DIRECT_DB"
    elif [ -f "$DEFAULT_DOCKER_DB" ]; then
        TARGET_DB="$DEFAULT_DOCKER_DB"
    fi
}

install_direct() {
    echo "开始直接安装 3x-ui..."
    bash <(curl -Ls https://raw.githubusercontent.com/mhsanaei/3x-ui/master/install.sh)
    TARGET_DB="$DEFAULT_DIRECT_DB"
}

install_docker() {
    echo "开始 Docker 方式安装 3x-ui..."
    echo

    read -p "请输入 Docker 容器名称（默认 3x-ui）: " DOCKER_CONTAINER_NAME
    if [ -z "$DOCKER_CONTAINER_NAME" ]; then
        DOCKER_CONTAINER_NAME="3x-ui"
    fi

    if ! [[ "$DOCKER_CONTAINER_NAME" =~ ^[A-Za-z0-9_.-]+$ ]]; then
        echo "错误：容器名称格式不合法。"
        exit 1
    fi

    echo "将使用容器名称：$DOCKER_CONTAINER_NAME"
    echo

    if ! command -v docker >/dev/null 2>&1; then
        echo "正在安装 Docker..."
        bash <(curl -sSL https://get.docker.com)
    fi

    mkdir -p /opt/3x-ui/db /opt/3x-ui/cert

    if docker ps -a --format '{{.Names}}' | grep -Fxq "$DOCKER_CONTAINER_NAME"; then
        echo "检测到同名容器已存在，将删除旧容器。"
        docker rm -f "$DOCKER_CONTAINER_NAME"
    fi

    docker run -itd \
      -e XRAY_VMESS_AEAD_FORCED=false \
      -e XUI_ENABLE_FAIL2BAN=true \
      -v /opt/3x-ui/db/:/etc/x-ui/ \
      -v /opt/3x-ui/cert/:/root/cert/ \
      --network=host \
      --restart=unless-stopped \
      --name "$DOCKER_CONTAINER_NAME" \
      ghcr.io/mhsanaei/3x-ui:latest

    TARGET_DB="$DEFAULT_DOCKER_DB"
    CONTAINER_NAME="$DOCKER_CONTAINER_NAME"
}

stop_xui() {
    CONTAINER_NAME="$(find_xui_container)"

    if [ -n "$CONTAINER_NAME" ]; then
        echo "正在停止 Docker 容器：$CONTAINER_NAME"
        docker stop "$CONTAINER_NAME"
    else
        echo "正在停止 x-ui 服务..."
        systemctl stop x-ui 2>/dev/null || true
    fi
}

start_xui() {
    CONTAINER_NAME="$(find_xui_container)"

    if [ -n "$CONTAINER_NAME" ]; then
        echo "正在启动 Docker 容器：$CONTAINER_NAME"
        docker start "$CONTAINER_NAME"
    else
        echo "正在启动 x-ui 服务..."
        systemctl start x-ui 2>/dev/null || x-ui restart
    fi
}

show_ports_notice() {
    echo
    echo "======================================"
    echo "  请开放以下端口"
    echo "======================================"
    echo

    echo "面板 / 订阅相关端口："
    sqlite3 "$TARGET_DB" "
    SELECT key, value FROM settings
    WHERE lower(key) LIKE '%port%' OR lower(key) LIKE '%listen%';
    " 2>/dev/null

    echo
    echo "节点 Inbound 端口："
    sqlite3 "$TARGET_DB" "
    SELECT id, remark, port, protocol
    FROM inbounds
    ORDER BY port;
    " 2>/dev/null

    echo
    echo "请确认这些端口已在以下位置放行："
    echo "1. 云服务器安全组"
    echo "2. Linux 防火墙：ufw / firewalld / iptables"
    echo "3. 如果不用 --network host，还要配置 Docker -p 端口映射"
    echo
    echo "常用检查命令："
    echo "ss -tulnp"
    echo "ufw status"
    echo "iptables -L -n"
    echo
    echo "如果使用 Docker --network host，不需要 -p 映射。"
    echo "但云安全组和系统防火墙仍然要开放端口。"
    echo "======================================"
}

install_sqlite_if_needed

if ! is_xui_installed; then
    echo "系统中未检测到 3x-ui。"
    echo
    echo "请选择操作："
    echo "0) 退出"
    echo "1) 直接安装 3x-ui"
    echo "2) Docker 方式安装 3x-ui"
    echo
    read -p "请输入选项 0 / 1 / 2: " INSTALL_CHOICE

    case "$INSTALL_CHOICE" in
        0)
            echo "已退出。"
            exit 0
            ;;
        1)
            install_direct
            ;;
        2)
            install_docker
            ;;
        *)
            echo "输入无效，退出。"
            exit 1
            ;;
    esac
else
    detect_target_db
fi

echo
echo "目标数据库位置：$TARGET_DB"
echo

echo "正在读取当前目录数据库：$SRC_DB"
echo

echo "数据库中识别到的可能域名："
sqlite3 "$SRC_DB" "
SELECT stream_settings FROM inbounds
UNION ALL
SELECT settings FROM inbounds
UNION ALL
SELECT sniffing FROM inbounds
UNION ALL
SELECT value FROM settings;
" 2>/dev/null | grep -oE '[A-Za-z0-9.-]+\.[A-Za-z]{2,}' | sort -u

echo
read -p "请输入要替换的旧域名: " OLD_DOMAIN
read -p "请输入新的域名: " NEW_DOMAIN

if [ -z "$OLD_DOMAIN" ] || [ -z "$NEW_DOMAIN" ]; then
    echo "错误：新旧域名不能为空。"
    exit 1
fi

if [ "$OLD_DOMAIN" = "$NEW_DOMAIN" ]; then
    echo "错误：新旧域名相同。"
    exit 1
fi

if ! [[ "$OLD_DOMAIN" =~ ^[A-Za-z0-9.-]+$ ]]; then
    echo "错误：旧域名格式不合法。"
    exit 1
fi

if ! [[ "$NEW_DOMAIN" =~ ^[A-Za-z0-9.-]+$ ]]; then
    echo "错误：新域名格式不合法。"
    exit 1
fi

echo
echo "当前目录数据库中的旧域名命中位置："
sqlite3 "$SRC_DB" "
SELECT 'inbounds.stream_settings', COUNT(*) FROM inbounds WHERE stream_settings LIKE '%$OLD_DOMAIN%'
UNION ALL
SELECT 'inbounds.settings', COUNT(*) FROM inbounds WHERE settings LIKE '%$OLD_DOMAIN%'
UNION ALL
SELECT 'inbounds.sniffing', COUNT(*) FROM inbounds WHERE sniffing LIKE '%$OLD_DOMAIN%'
UNION ALL
SELECT 'settings.value', COUNT(*) FROM settings WHERE value LIKE '%$OLD_DOMAIN%';
"

echo
echo "请最终确认："
echo "--------------------------------------"
echo "源数据库：$SRC_DB"
echo "临时数据库：$WORK_DB"
echo "目标数据库：$TARGET_DB"
echo "旧域名：$OLD_DOMAIN"
echo "新域名：$NEW_DOMAIN"
echo "--------------------------------------"
echo
read -p "确认无误请输入 y 或 Y，其他任何输入都会退出: " CONFIRM

if [[ "${CONFIRM,,}" != "y" ]]; then
    echo "已取消，未做任何修改。"
    exit 0
fi

echo
echo "正在复制源数据库到临时数据库..."
cp "$SRC_DB" "$WORK_DB"

echo "正在临时数据库中批量替换域名..."
sqlite3 "$WORK_DB" "
UPDATE inbounds
SET stream_settings = REPLACE(stream_settings, '$OLD_DOMAIN', '$NEW_DOMAIN')
WHERE stream_settings LIKE '%$OLD_DOMAIN%';

UPDATE inbounds
SET settings = REPLACE(settings, '$OLD_DOMAIN', '$NEW_DOMAIN')
WHERE settings LIKE '%$OLD_DOMAIN%';

UPDATE inbounds
SET sniffing = REPLACE(sniffing, '$OLD_DOMAIN', '$NEW_DOMAIN')
WHERE sniffing LIKE '%$OLD_DOMAIN%';

UPDATE settings
SET value = REPLACE(value, '$OLD_DOMAIN', '$NEW_DOMAIN')
WHERE value LIKE '%$OLD_DOMAIN%';
"

echo
echo "临时数据库替换后检查："
sqlite3 "$WORK_DB" "
SELECT 'inbounds.stream_settings old_remain', COUNT(*) FROM inbounds WHERE stream_settings LIKE '%$OLD_DOMAIN%'
UNION ALL
SELECT 'inbounds.settings old_remain', COUNT(*) FROM inbounds WHERE settings LIKE '%$OLD_DOMAIN%'
UNION ALL
SELECT 'inbounds.sniffing old_remain', COUNT(*) FROM inbounds WHERE sniffing LIKE '%$OLD_DOMAIN%'
UNION ALL
SELECT 'settings.value old_remain', COUNT(*) FROM settings WHERE value LIKE '%$OLD_DOMAIN%'
UNION ALL
SELECT 'inbounds.stream_settings new_hit', COUNT(*) FROM inbounds WHERE stream_settings LIKE '%$NEW_DOMAIN%'
UNION ALL
SELECT 'inbounds.settings new_hit', COUNT(*) FROM inbounds WHERE settings LIKE '%$NEW_DOMAIN%'
UNION ALL
SELECT 'inbounds.sniffing new_hit', COUNT(*) FROM inbounds WHERE sniffing LIKE '%$NEW_DOMAIN%'
UNION ALL
SELECT 'settings.value new_hit', COUNT(*) FROM settings WHERE value LIKE '%$NEW_DOMAIN%';
"

echo
read -p "临时数据库检查无误，是否继续覆盖正式数据库？输入 y 或 Y 继续: " FINAL_CONFIRM

if [[ "${FINAL_CONFIRM,,}" != "y" ]]; then
    echo "已取消。原始备份文件和正式数据库均未被覆盖。"
    rm -f "$WORK_DB"
    exit 0
fi

echo
stop_xui

echo
echo "正在备份正式数据库..."
if [ -f "$TARGET_DB" ]; then
    BACKUP_DB="$TARGET_DB.bak.$(date +%F-%H%M%S)"
    cp "$TARGET_DB" "$BACKUP_DB"
    echo "正式数据库备份：$BACKUP_DB"
fi

echo "正在覆盖正式数据库..."
mkdir -p "$(dirname "$TARGET_DB")"
cp "$WORK_DB" "$TARGET_DB"

echo
start_xui

rm -f "$WORK_DB"

echo
echo "数据库迁移和域名替换完成。"

CERT_DIR="/root/cert/$NEW_DOMAIN"
if [ ! -f "$CERT_DIR/fullchain.pem" ] || [ ! -f "$CERT_DIR/privkey.pem" ]; then
    echo
    echo "提醒：未检测到新域名证书文件："
    echo "$CERT_DIR/fullchain.pem"
    echo "$CERT_DIR/privkey.pem"
    echo "如使用 Docker 安装，宿主机证书目录通常是：/opt/3x-ui/cert/$NEW_DOMAIN/"
fi

echo
read -p "是否现在运行 x-ui 命令安装 / 申请 Cloudflare 证书？输入 y 或 Y 继续: " CF_CONFIRM

if [[ "${CF_CONFIRM,,}" = "y" ]]; then
    CONTAINER_NAME="$(find_xui_container)"

    if command -v x-ui >/dev/null 2>&1; then
        x-ui
    elif [ -n "$CONTAINER_NAME" ]; then
        docker exec -it "$CONTAINER_NAME" x-ui
    else
        echo "未找到 x-ui 命令，也未识别到 Docker 容器。"
    fi
else
    echo "已跳过 Cloudflare 证书安装。"
fi

show_ports_notice

echo
echo "完成。"
echo "请根据上面列出的端口，在云服务器安全组中放行后，再测试面板、订阅和节点连接。"
if [ "$OLD_DOMAIN" = "$NEW_DOMAIN" ]; then
    echo "错误：新旧域名相同，无需修改"
    exit 1
fi

echo
echo "请最终确认以下操作："
echo "--------------------------------------"
echo "源数据库：$SRC_DB"
echo "目标数据库：$TARGET_DB"
echo "旧域名：$OLD_DOMAIN"
echo "新域名：$NEW_DOMAIN"
echo
echo "将要执行："
echo "1. 备份当前已安装数据库"
echo "2. 用当前目录 ./x-ui.db 覆盖 /etc/x-ui/x-ui.db"
echo "3. 在覆盖后的数据库中批量替换旧域名为新域名"
echo "4. 重启 3x-ui"
echo "--------------------------------------"
echo

read -p "确认无误请输入 y 或 Y，其他任何输入都会退出: " CONFIRM

if [[ "${CONFIRM,,}" != "y" ]]; then
    echo "已取消，未做任何修改。"
    exit 0
fi

echo
echo "开始执行..."

if [ -f "$TARGET_DB" ]; then
    BACKUP_DB="$TARGET_DB.bak.$(date +%F-%H%M%S)"
    echo "正在备份当前已安装数据库到：$BACKUP_DB"
    cp "$TARGET_DB" "$BACKUP_DB"
else
    echo "提醒：目标数据库 $TARGET_DB 不存在，将直接复制新数据库。"
fi

echo "正在复制当前目录数据库到目标位置..."
cp "$SRC_DB" "$TARGET_DB"

AFTER_COPY_BACKUP="$TARGET_DB.before-domain-update.$(date +%F-%H%M%S)"
echo "正在备份覆盖后的原始数据库到：$AFTER_COPY_BACKUP"
cp "$TARGET_DB" "$AFTER_COPY_BACKUP"

echo "正在批量替换域名..."
sqlite3 "$TARGET_DB" "
UPDATE inbounds
SET stream_settings = REPLACE(stream_settings, '$OLD_DOMAIN', '$NEW_DOMAIN')
WHERE stream_settings LIKE '%$OLD_DOMAIN%';

UPDATE settings
SET value = REPLACE(value, '$OLD_DOMAIN', '$NEW_DOMAIN')
WHERE value LIKE '%$OLD_DOMAIN%';
"

echo
echo "替换后检查："
sqlite3 "$TARGET_DB" "
SELECT 'inbounds.stream_settings old_remain', COUNT(*) FROM inbounds WHERE stream_settings LIKE '%$OLD_DOMAIN%'
UNION ALL
SELECT 'settings.value old_remain', COUNT(*) FROM settings WHERE value LIKE '%$OLD_DOMAIN%'
UNION ALL
SELECT 'inbounds.stream_settings new_hit', COUNT(*) FROM inbounds WHERE stream_settings LIKE '%$NEW_DOMAIN%'
UNION ALL
SELECT 'settings.value new_hit', COUNT(*) FROM settings WHERE value LIKE '%$NEW_DOMAIN%';
"

echo
echo "替换后的 settings 证书相关配置："
sqlite3 "$TARGET_DB" "
SELECT key, value FROM settings WHERE value LIKE '%$NEW_DOMAIN%';
"

echo
echo "正在重启 3x-ui..."

if docker ps --format '{{.Names}}' 2>/dev/null | grep -q '^3x-ui$'; then
    docker restart 3x-ui
else
    x-ui restart
fi

echo
read -p "是否现在运行 x-ui 命令安装 / 申请 Cloudflare 证书？输入 y 或 Y 继续，其他输入跳过: " CF_CONFIRM

if [[ "${CF_CONFIRM,,}" = "y" ]]; then
    echo
    echo "即将进入 x-ui 命令菜单。"
    echo "请在菜单中选择 SSL / Cloudflare 证书相关功能。"
    x-ui
else
    echo "已跳过 Cloudflare 证书安装。"
fi

echo
echo "完成。"
