#!/usr/bin/python3
import os
import docker
import configparser
import platform
import config_xuilist as confxuisrv
import sys
import subprocess

linuxplatf = platform.version()

#读取设置文件
configfile ='/usr/local/x-ui/plugs/config/xuiplugconf.ini'
subserver_sec = 'SUBSCRIPTIONSERVER'

if  os.path.exists(configfile):
    config = configparser.ConfigParser()
    config.read(configfile)


htmlroot = config.get(subserver_sec,'station_root')
serverport = config.get(subserver_sec,'serverport')
engin_name = 'xuisubsrv' + config.get(subserver_sec,'engin_name') 
subserver_domain = config.get(subserver_sec,'subserver_domain')
os.system(f'echo "configfile:"')
os.system(f'cat {configfile}')


if subserver_domain =='app.myserver.com':
    print('订阅服务器域名是默认值,请先设置订阅服务器的域名!!\n 进入菜单:<4. 订阅/X-UI服务器管理(Subscription/X-UI Server Management)> ==> <5.域名端口设置(domain)>')
    
    msg = '是否现在设置订阅服务器的域名和端口(y/n) :'
    confirmyn = input(msg)
    if confirmyn == 'y' :
         subprocess.run(['python3', 'config_xuilist.py', 'server_mng_menu'], capture_output=True, text=True)
        
    else:
        sys.exit(0)
if config.get('XUISERVER1','domain') == 'app.myserver.com':
    print('请先添加xui服务器的信息,以读取入站信息\n 进入菜单:<4. 订阅/X-UI服务器管理(Subscription/X-UI Server Management)> ==> <2. 添加(Add)>')
    
    msg = '是否现在添加x-ui 服务器(y/n) :'
    confirmyn = input(msg)
    
    if confirmyn == 'y' :
        result = subprocess.run(['python3', 'config_xuilist.py', 'server_mng_menu'], capture_output=True, text=True)

    else:
        sys.exit(0)
        

if os.path.isdir('/root/'):
    print(f'-- making folder to {htmlroot} --')
    os.system(f'mkdir -p {htmlroot}')

def install_docker():
    print('-- installing docker --')
    if 'Ubuntu' in linuxplatf: 
        print('-- updating --')
        os.system("echo -ne '\n' | apt update")
        print('-- upgrading --')
        # os.system("echo -ne '\n \n \n' | apt-get upgrade")
        os.system('apt install docker.io -y')
        os.system('docker pull nginx')

    if 'Centos' in linuxplatf:
        print('-- updating --')
        os.system('yum update -y')
        print('-- upgrading --')
        os.system('yum upgrade -y')
        os.system('yum install docker.io -y')
        os.system('docker pull nginx')

def build_docker_container():
    
    docker_client = docker.from_env()
    try:
        container = docker_client.containers.get(engin_name)
    except docker.errors.NotFound as exc: 
        # if the container not exist build new one
        print(f'-- building docker container name:{engin_name} site root: {htmlroot} --')
        os.system(r"docker stop `docker ps -a | grep xuisubsrv | awk '{print $1}'`")
        os.system(r"docker rm `docker ps -a | grep xuisubsrv | awk '{print $1}'`")
        os.system(f'docker run -d -p {serverport}:80  -v {htmlroot}:/usr/share/nginx/html \
            --name {engin_name} --restart=always nginx')
    else:
        print(f'start docker container : {engin_name}')
        os.system(r"docker stop `docker ps -a | grep xuisubsrv | awk '{print $1}'`")
        os.system(r"docker rm `docker ps -a | grep xuisubsrv | awk '{print $1}'`")
        os.system(f'docker run -d -p {serverport}:80  -v {htmlroot}:/usr/share/nginx/html \
            --name {engin_name} --restart=always nginx')

if __name__ == '__main__':
    install_docker()
    build_docker_container()
