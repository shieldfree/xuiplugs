#!/bin/bash

red='\033[0;31m'
green='\033[0;32m'
yellow='\033[0;33m'
plain='\033[0m'

function LOGI() {
    echo -e "${green}[INF] $* ${plain}"
}

function LOGE() {
    echo -e "${red}[ERR] $* ${plain}"
}


check_status() {
    if [[ ! -f /etc/systemd/system/x-ui.service ]]; then
        return 2
    fi
    temp=$(systemctl status x-ui | grep Active | awk '{print $3}' | cut -d "(" -f2 | cut -d ")" -f1)
    if [[ x"${temp}" == x"running" ]]; then
        return 0
    else
        return 1
    fi
}

check_install() {
    check_status
    if [[ $? == 2 ]]; then
        echo ""
        LOGE "Please intall X-UI first"
        LOGE "请先安装面板"
        if [[ $# == 0 ]]; then
            before_show_menu
        fi
        return 1
    else
        return 0
    fi
}

before_show_menu() {
    echo && echo -n -e "  ${yellow}Press ENTER Key to return  ${plain}"
    echo && echo -n -e "  ${yellow}按回车返回主菜单: ${plain}" && read temp
    show_menu
}

enable_data_usage() {
    clear
    LOGI "  正在安装插件(Installing)..."
    mkdir -p /usr/local/x-ui/plugs/
    cp ./xuiplug_show_usage.py  /usr/local/x-ui/plugs/xuiplug_show_usage.py
    cp ./xuiplug_show_usage_uninstall.py  /usr/local/x-ui/plugs/xuiplug_show_usage_uninstall.py
    python3 /usr/local/x-ui/plugs/xuiplug_show_usage.py 

    crontab -l | grep -v "xuiplug_show_usage" | crontab -

    crontab -l >/tmp/crontabTask.tmp
    echo "*/10 * * * * python3 /usr/local/x-ui/plugs/xuiplug_show_usage.py " >>/tmp/crontabTask.tmp
    crontab /tmp/crontabTask.tmp
    rm /tmp/crontabTask.tmp

    sleep 1
    LOGI "  安装数据流量插件成功 !!"
    LOGI "  Successfully installed !"
}

disable_data_usage() {
    clear
    LOGI "  正在卸载插件(Unnstalling)..."
    LOGI "  Unnstalling..."
    sleep 2

    if [[ -f /etc/x-ui/x-ui.db ]]; then
        python3 /usr/local/x-ui/plugs/xuiplug_show_usage_uninstall.py
    fi
    #rm  -rf /usr/local/x-ui/plugs/xuiplug_show_usage*

    crontab -l | grep -v "xuiplug_show_usage" | crontab -
    if [[ $? -ne 0 ]]; then
        LOGI "  卸载数据流量插件失败.."
    else
        LOGI "  卸载数据流量插件成功 !!"
        LOGI "  Successfully removed !!"
    fi
}

show_usage() {
    echo "  数据流量显示插件使用方法: "

    echo "------------------------------------------"

    echo "    bash showdatausage               - 显示菜单"

    echo "    bash showdatausage install       - 安装插件"

    echo "    bash showdatausage uninstall     - 卸载插件"

    echo "------------------------------------------"
}






show_menu() {
    echo -e "
  ${green}x-ui 数据流量显示插件${plain}
  
  ${green}安装成功后会在remark显示使用流量${plain}
  ${green}(客户端显示: 须以订阅方式添加节点)${plain}
  ${green}(Add inbounds via subscription )${plain}
  ${green}(instead of directly to client)${plain}
  
    ${green}0.${plain} ${red}退出脚本 (Exit)${plain} 
 ——————————————————————————
    ${green}1.${plain} 安装插件(Install)
    ${green}2.${plain} 卸载插件(Uninstall)
 ——————————————————————————
 "
    echo "  Please input a number [0-2]  "
    echo && read -p "  请输入选择 [0-2]  :" num

    case "${num}" in
    0)
        exit 0
        ;;
    1)
        check_install && enable_data_usage
        sleep 1
        show_menu 
        ;;
    2)
        disable_data_usage
        sleep 2
        show_menu 
        ;;
    *)
        clear
        LOGE "  请输入正确的数字 [0-2] : "
        LOGE "  Please input correct number [0-2]  :"
        sleep 1
        show_menu 
        ;;
    esac
}


if [[ $# > 0 ]]; then
    case $1 in
    "install")
        enable_data_usage
        ;;
    "uninstall")
        disable_data_usage
        ;;


    *)  clear
        #show_usage
        show_menu ;;
    esac
else
    clear
    show_menu
fi
