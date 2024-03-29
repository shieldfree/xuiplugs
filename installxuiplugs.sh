##!/usr/bin/env bash

red='\033[1;31m'
green='\033[1;32m'
yellow='\033[0;33m'
plain='\033[0m'

cur_dir=$(pwd)

function LOGI() {
    echo -e "${green}[INF] $* ${plain}"
}

# check root
[[ $EUID -ne 0 ]] && echo -e "${red}错误：${plain} 必须使用root用户运行此脚本！\n" && exit 1

# check os
if [[ -f /etc/redhat-release ]]; then
    release="centos"
elif cat /etc/issue | grep -Eqi "debian"; then
    release="debian"
elif cat /etc/issue | grep -Eqi "ubuntu"; then
    release="ubuntu"
elif cat /etc/issue | grep -Eqi "centos|red hat|redhat"; then
    release="centos"
elif cat /proc/version | grep -Eqi "debian"; then
    release="debian"
elif cat /proc/version | grep -Eqi "ubuntu"; then
    release="ubuntu"
elif cat /proc/version | grep -Eqi "centos|red hat|redhat"; then
    release="centos"
else
    echo -e "${red}未检测到系统版本，请联系脚本作者！${plain}\n" && exit 1
fi

arch=$(arch)

if [[ $arch == "x86_64" || $arch == "x64" || $arch == "amd64" ]]; then
    arch="amd64"
elif [[ $arch == "aarch64" || $arch == "arm64" ]]; then
    arch="arm64"
else
    arch="amd64"
    echo -e "${red}检测架构失败，使用默认架构: ${arch}${plain}"
fi

echo "架构: ${arch}"

if [ $(getconf WORD_BIT) != '32' ] && [ $(getconf LONG_BIT) != '64' ]; then
    echo "本软件不支持 32 位系统(x86)，请使用 64 位系统(x86_64)，如果检测有误，请联系作者"
    exit -1
fi

os_version=""

# os version
if [[ -f /etc/os-release ]]; then
    os_version=$(awk -F'[= ."]' '/VERSION_ID/{print $3}' /etc/os-release)
fi
if [[ -z "$os_version" && -f /etc/lsb-release ]]; then
    os_version=$(awk -F'[= ."]+' '/DISTRIB_RELEASE/{print $2}' /etc/lsb-release)
fi

if [[ x"${release}" == x"centos" ]]; then
    if [[ ${os_version} -le 6 ]]; then
        echo -e "${red}请使用 CentOS 7 或更高版本的系统！${plain}\n" && exit 1
    fi
elif [[ x"${release}" == x"ubuntu" ]]; then
    if [[ ${os_version} -lt 16 ]]; then
        echo -e "${red}请使用 Ubuntu 16 或更高版本的系统！${plain}\n" && exit 1
    fi
elif [[ x"${release}" == x"debian" ]]; then
    if [[ ${os_version} -lt 8 ]]; then
        echo -e "${red}请使用 Debian 8 或更高版本的系统！${plain}\n" && exit 1
    fi
fi

install_base() {
    if [[ x"${release}" == x"centos" ]]; then
        yum update -y
        yum install wget curl tar docker.io python3-pip -y
        pip install paramiko scp docker

    else
        apt update -y
        apt install wget curl tar docker.io python3-pip -y
        pip install paramiko scp docker
    fi
}


install_base

if [[ -f /usr/local/x-ui/plugs/config/xuiplugconf.ini ]]; then
    LOGI "  正在备份设置文件。。" 
    cp /usr/local/x-ui/plugs/config/xuiplugconf.ini  /usr/local/x-ui/xuiplugconf.ini
    cp /usr/local/x-ui/plugs/config/subscription.ini  /usr/local/x-ui/subscription.ini
    rm -rf  /usr/local/x-ui/plugs/*
fi
# mkdir -p /usr/local/x-ui/plugs/
rm -rf  ./xuiplugs

git clone https://github.com/shieldfree/xuiplugs

mkdir -p /usr/local/x-ui/plugs/
mv ./xuiplugs/*  /usr/local/x-ui/plugs/
rm -rf xuiplugs

#export PATH="/usr/local/x-ui/plugs:$PATH"

cp /usr/local/x-ui/plugs/xuiplugs.sh  /usr/local/bin/xuiplugs
chmod +x /usr/local/bin/xuiplugs

cp /usr/local/x-ui/plugs/dufs.sh /usr/local/bin/dufs
chmod +x /usr/local/bin/dufs



if [[ -f /usr/local/x-ui/xuiplugconf.ini ]]; then
    mv /usr/local/x-ui/xuiplugconf.ini /usr/local/x-ui/plugs/config/xuiplugconf.ini
    mv  /usr/local/x-ui/subscription.ini /usr/local/x-ui/plugs/config/subscription.ini 
    LOGI "  设置文件已从备份还原。。" 
fi

# wget -N --no-check-certificate -O  /usr/local/x-ui/plugs/showdatausage.sh https://github.com/shieldfree/Scriptforxui/raw/main/showdatausage.sh
# wget -N --no-check-certificate -O  /usr/local/x-ui/plugs/xuiplug_show_usage.py https://github.com/shieldfree/Scriptforxui/raw/main/xuiplug_show_usage.py
# wget -N --no-check-certificate -O  /usr/local/x-ui/plugs/xuiplug_show_usage_uninstall.py https://github.com/shieldfree/Scriptforxui/raw/main/xuiplug_show_usage_uninstall.py

bash /usr/local/x-ui/plugs/xuiplugs.sh

