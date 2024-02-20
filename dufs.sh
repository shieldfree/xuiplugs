#!/bin/bash

red='\033[1;31m'
green='\033[1;32m'
yellow='\033[0;33m'
plain='\033[0m'





# 检查参数数量
if [ $# -ne 2 ]; then
    echo "Usage: $0 <minutes> <folder>"
    exit 1
fi

# 删除原有的 crontab中 删除容器 dufs220的失效命令。
crontab -l > /tmp/crontab_tmp
sed -i '/dufs220/d' /tmp/crontab_tmp
crontab /tmp/crontab_tmp
rm /tmp/crontab_tmp

if docker ps -a --format '{{.Names}}' | grep -q "dufs220"; then
    docker stop dufs220
    sleep 2
fi



# 提取参数
minutes="$1"
folder="$2"

# 计算时间
current_time=$(date +%s)
target_time=$((current_time + minutes * 60))
target_time_str=$(date -d "@$target_time" +"%M %H %d %m *")

# 当前目录启动 启动dufs服务

docker run -d -v "$(pwd)/$folder:/data" -p 5000:5000 --rm --name dufs220 -it sigoden/dufs /data -A -a lg123:lg123@/:rw

# 添加命令到 crontab
(crontab -l ; echo "$target_time_str docker stop dufs220") | crontab -
echo "Scheduled to remove container dufs220  at $(date -d "@$target_time")"



public_ip=$(curl ifconfig.me)
echo -e "${green}You can share the files via link below within ${plain}"
echo -e "${green}http://$public_ip:5000${plain}"
echo -e "${red}Username/Password: lg123${plain}"

