#!/bin/bash

red='\033[1;31m'
green='\033[1;32m'
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

check_xui_ver() {
    # 检查文件是否存在
    if [ ! -f "/usr/local/x-ui/x-ui.sh" ]; then
        echo "请先安装X-UI"
        exit 1
    fi
    
    # 检查文件中是否包含特定字符串，不区分大小写
    if grep -qi "MHSanaei/3x-ui" "/usr/local/x-ui/x-ui.sh"; then
        echo "3"  # 如果包含，返回版本号为3
    elif grep -qi "FranzKafkaYu/x-ui" "/usr/local/x-ui/x-ui.sh"; then
        echo "1"  # 如果不包含，返回版本号为1
    else
        echo "0"  # 如果不包含，返回版本号为0
    fi
}



make_sublinks() {
# 选择 创建订阅文件的python脚本的文件

    version=$(check_xui_ver)
    if [ "$version" = "3" ] ; then
        echo "/usr/local/x-ui/plugs/make_sublinks3.py" 
        
    elif [ "$version" = "1" ] ; then
        echo "/usr/local/x-ui/plugs/make_sublinks1.py"  
        
    elif [ "$version" = "0" ] ; then
        echo "/usr/local/x-ui/plugs/make_sublinks1.py"
    fi
}


before_show_menu() {
    echo && echo -n -e "  ${yellow}Press ENTER Key to return  ${plain}"
    echo && echo -n -e "  ${yellow}按回车返回主菜单: ${plain}" && read temp
    show_menu
}


# crontab -l | grep -q 'make_sublinks.py'  # 通过crontab 命令判断
build_remove_subscription_server() {
    if docker ps -a --format '{{.Names}}' | grep -q 'xuisubsrv'; then
        LOGI "  是否删除订阅服务器 ? "
        read -p "Do you want to remove the subscription server? (y/n): " choice
        if [ "$choice" = "y" ]; then
            disable_subscription_links
        fi
    else
        LOGI "  是否搭建订阅服务器 ? "
        read -p "Do you want to build a subscription server? (y/n): " choice
        if [ "$choice" = "y" ]; then
            enable_subscription_links
        fi
    fi
}


enable_subscription_links() {

    #echo -e "${yellow}请确认开始搭建订阅服务器: ${plain}"
    #read -p "输入y继续,其他退出[y/n]": config_confirm
    py_make_sublinks=$(make_sublinks)
    #if [[ x"${config_confirm}" == x"y" || x"${config_confirm}" == x"Y" ]]; then
    
        clear
        LOGI "  开始搭建订阅服务器..."
        check_install && python3 /usr/local/x-ui/plugs/subserver.py
        if [ $? -eq 0 ]; then
            echo -e "${red}没有订阅服务器域名,未搭建订阅服务器! ${plain}"
            return
        fi
        python3 "$py_make_sublinks" 
        if [ $? -eq 0 ]; then
            echo -e "${red}没有X-UI服务器信息,未搭建订阅服务器! ${plain}" 
            return
        fi
        
        crontab -l | grep -v "make_sublinks" | crontab -
        crontab -l >/tmp/crontabTask.tmp
        echo -e "*/8 * * * * python3 \"$py_make_sublinks\" " >>/tmp/crontabTask.tmp
        crontab /tmp/crontabTask.tmp
        rm /tmp/crontabTask.tmp
        
        read -p "  ↑ 订阅链接.  按回车继续  :" num
        
    #else
    #echo -e "${red}已取消搭建订阅服务器...${plain}"
    #fi


}

disable_subscription_links() {
    clear
    echo -e "${red}请确认开始删除订阅服务器: ${plain}"
    read -p "输入y继续,其他退出[y/n]": config_confirm
    if [[ x"${config_confirm}" == x"y" || x"${config_confirm}" == x"Y" ]]; then
        clear
        LOGE "  开始删除订阅服务器..."
        

    # if [[ -f /etc/x-ui/x-ui.db ]]; then
    #     python3 /usr/local/x-ui/plugs/xuiplug_show_usage_uninstall.py
    # fi
    #rm  -rf /usr/local/x-ui/plugs/xuiplug_show_usage*
    
    docker stop  `docker ps -a | grep xuisubsrv | awk '{print $1}'`
    docker rm  `docker ps -a | grep xuisubsrv | awk '{print $1}'`
        
    crontab -l | grep -v "make_sublinks" | crontab -

        if [[ $? -ne 0 ]]; then
            LOGE "  卸载 订阅源生成 插件失败.."
        else
            LOGI "  卸载 订阅源生成 插件成功 !!"
            LOGI "  Successfully removed !!"
        fi
    
    else
    echo -e "${red}已取消操作...${plain}"
    fi

    sleep 1

}

enable_disable_port_changer() {
    if crontab -l | grep -q 'port_changer.py'; then
        LOGI "  是否停止 定时更改端口 ? "
        read -p "port_changer is already running. Do you want to remove it? (y/n): " choice
        if [ "$choice" = "y" ]; then
            disable_port_changer
        fi
    else
        LOGI " 是否启用 定时更改端口 ? "
        read -p " Do you want to Enable port_changer ? (y/n): " choice
        if [ "$choice" = "y" ]; then
            enable_port_changer
        fi
    fi
}

enable_port_changer() {
    clear
    LOGI "  正在安装 portchanger 插件..."
    # mkdir -p /usr/local/x-ui/plugs/
    # cp ./port_changer.py  /usr/local/x-ui/plugs/xuiplug_show_usage.py
    # cp ./xuiplug_show_usage_uninstall.py  /usr/local/x-ui/plugs/xuiplug_show_usage_uninstall.py
    # python3 /usr/local/x-ui/plugs/xuiplug_show_usage.py 

    crontab -l | grep -v "port_changer" | crontab -

    crontab -l >/tmp/crontabTask.tmp
    echo "26 2 * * * cd /usr/local/x-ui/plugs && python3 port_changer.py " >>/tmp/crontabTask.tmp
    crontab /tmp/crontabTask.tmp
    rm /tmp/crontabTask.tmp

    sleep 1
    LOGI "  成功安装 port_changer 插件 !!"
    LOGI "  Successfully installed !"
}

disable_port_changer() {
    clear
    LOGI "  正在卸载 port_changer 插件..."
    LOGI "  Unnstalling..."
    sleep 2

    # if [[ -f /etc/x-ui/x-ui.db ]]; then
    #     python3 /usr/local/x-ui/plugs/xuiplug_show_usage_uninstall.py
    # fi
    #rm  -rf /usr/local/x-ui/plugs/xuiplug_show_usage*

    crontab -l | grep -v "port_changer" | crontab -
    if [[ $? -ne 0 ]]; then
        LOGE "  卸载 port_changer 插件失败.."
    else
        LOGI "  卸载 port_changer 插件成功 !!"
        LOGI "  Successfully removed !!"
    fi
    sleep 1
}


enable_disable_data_usage_display() {
    if crontab -l | grep -q 'xuiplug_show_usage.py'; then
        LOGI "  是否关闭 节点用量显示 ? "
        read -p "Do you want to Disable Client_data_usase_display ? (y/n): " choice
        if [ "$choice" = "y" ]; then
            disable_data_usage_display
        fi
    else
        LOGI " 是否启用 节点用量显示 ? "
        read -p " Do you want to Enable Client_data_usase_display ? (y/n): " choice
        if [ "$choice" = "y" ]; then
            enable_data_usage_display
        fi
    fi
}


enable_data_usage_display() {
    clear
    LOGI "  正在安装 数据流量 插件(Installing)..."
    mkdir -p /usr/local/x-ui/plugs/
    # cp ./xuiplug_show_usage.py  /usr/local/x-ui/plugs/xuiplug_show_usage.py
    # cp ./xuiplug_show_usage_uninstall.py  /usr/local/x-ui/plugs/xuiplug_show_usage_uninstall.py
    python3 /usr/local/x-ui/plugs/xuiplug_show_usage.py 

    crontab -l | grep -v "xuiplug_show_usage" | crontab -

    crontab -l >/tmp/crontabTask.tmp
    echo "*/10 * * * * python3 /usr/local/x-ui/plugs/xuiplug_show_usage.py " >>/tmp/crontabTask.tmp
    crontab /tmp/crontabTask.tmp
    rm /tmp/crontabTask.tmp

    sleep 1
    LOGI "  安装数据流量插件成功 !!"
    LOGI "  Successfully installed !"
    sleep 1
}

disable_data_usage_display() {
    clear
    LOGI "  正在卸载 数据流量 插件(Unnstalling)..."
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
    sleep 1
}




create_inbounds_batch() {
# 批量创建节点
    version=$(check_xui_ver)
    if [ "$version" = "3" ] ; then
        echo -e "当前X-UI 版本为: ${green}MHsanaei/3x-ui${plain} "  
        python3 /usr/local/x-ui/plugs/create_inbounds_batch3.py
        
    elif [ "$version" = "1" ] ; then
        echo -e "当前X-UI 版本为: ${green}FranzKafkaYu/x-ui${plain} "  
        python3 /usr/local/x-ui/plugs/create_inbounds_batch1.py
        
    elif [ "$version" = "0" ] ; then
        echo -e "${red}无法识别版本!!${plain}"
        python3 /usr/local/x-ui/plugs/create_inbounds_batch1.py
    fi
}


#  创建subconverter 的 Docker 容器
build_subconvsrv_container() {
    if docker ps -a --format '{{.Names}}' | grep -q 'subconvsrv'; then
        LOGE "  订阅转换服务器(Subconverter)已经创建过了,是否删除重建?"
        read -p "请确认 (y/n): " choice
        if [ "$choice" = "y" ]; then
            # 停止并删除容器
            docker stop subconvsrv1
            docker rm subconvsrv1
            LOGE "  订阅转换服务器(Subconverter)已经删除完毕 !!"
            LOGE "  The subconvsrv container has been stopped and deleted !!"

        else
            echo -e "${red}取消创建操作.${plain}"
            #exit 1
        fi
    fi
    
    read -p "请输入用于订阅服务的本地端口号: " p25500

    docker run -d --restart=always --name subconvsrv1 -p ${p25500}:25500 tindy2013/subconverter:latest
    echo -e "${green}http${red}s${green}://LOCALHOST:${p25500}/sub?target=clash&url=https%3A%2F%2F${plain}"
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
  ${green}           X-UI 助手${plain}
  
  ${green}创建订阅服务器，自动切换节点端口，显示用量${plain}
  ${green}管理服务器和节点，安装NPM代理服务器，clash订阅转换 ${plain}
  
    ${green}0.${plain} ${red}退出脚本 (Exit)${plain} 
 —————————————————————————————————————————————————————————————————
    ${green} 1.${plain} 搭建/删除${green}订阅服务器${plain}(Build/Remove Subscription Server)
    ${green} 2.${plain} 启用/删除定时${green}切换节点端口${plain}(Enable/Disable Inbound Port Changer)
    ${green} 3.${plain} 启用/删除客户端${green}用量显示${plain}(Enable/Disable Client Usage Display)
    ${green} 4.${plain} 订阅/X-UI服务器管理(Subscription/X-UI Server Management)
    ${green} 5.${plain} 订阅链接管理(Manage Subscription Links)
    ${green} 6.${plain} ${green}批量添加${plain}节点(Create Multiple Inbounds)
    ${green} 7.${plain} 安装${red}NPM${plain}代理服务器(Install NginX Proxy Manager)
    ${green} 8.${plain} 创建订阅转换服务器（Build ${red}Subconverter${plain} Server)
    ${green} 9.${plain} inbound_config文件编辑
    ${green}10.${plain} X-UI服务器信息编辑
 —————————————————————————————————————————————————————————————————
 "
    echo "  Please input a number [0-10]  "
    echo && read -p "  请输入选择 [0-10]  :" num

    case "${num}" in
    0)
        exit 0
        ;;
    1)
        # 搭建/删除订阅服务器(Build/Remove subscription server)
        check_install && build_remove_subscription_server
        #enable_subscription_links
        show_menu 
        ;;
    2)
        #启用/删除定时切换节点端口(Enable/Disable inbound port changer)
        check_install && enable_disable_port_changer

        show_menu 
        ;;
    3)
        #启用/删除客户端用量显示(Enable/Disable Client Usage Display)
        check_install && enable_disable_data_usage_display
        show_menu 
        ;;
    4)
        # 服务器信息管理(X-UI server management)
        python3 /usr/local/x-ui/plugs/config_xuilist.py
        sleep 1
        show_menu 
        ;;
    5)
        # 订阅节点信息管理(Manage subscription links)
        python3 /usr/local/x-ui/plugs/config_sublinks.py
        sleep 1
        show_menu 
        ;;
    6)
        # 批量添加节点(Create multiple inbounds)
        #python3 /usr/local/x-ui/plugs/create_inbounds_batch1.py
        create_inbounds_batch
        sleep 2
        show_menu 
        ;;
    7)
        # 安装NPM 代理服务器
        docker run -d --restart=always --name npmsrv215 -p 80:80 -p 443:443 -p 81:81  -v ./data:/data -v ./letsencrypt:/etc/letsencrypt cylim76/npm:latest
        sleep 2
        show_menu 
        ;;
    8)
        build_subconvsrv_container
        sleep 2
        show_menu 
        ;;
    9)
        # 节点管理
        vi /usr/local/x-ui/plugs/config/subscription.ini
        sleep 2
        show_menu 
        ;;
    10)
        # xui服务器管理
        vi /usr/local/x-ui/plugs/config/xuiplugconf.ini
        sleep 2
        show_menu 
        ;;
    *)
        clear
        LOGE "  请输入正确的数字 [0-10] : "
        LOGE "  Please input correct number [0-10]  :"
        sleep 1
        show_menu 
        ;;
    esac
}


# 运行脚本的时候直接带 命令参数的代码
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
