#!/usr/bin/python3
import os
import docker
import configparser
import platform



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
        print(f'-- buld docker container name:{engin_name} site root: {htmlroot} --')
        os.system(r"docker start `docker ps -a | grep xuisubsrv | awk '{print $1}'`")
        os.system(r"docker rm `docker ps -a | grep xuisubsrv | awk '{print $1}'`")

        os.system(f'docker run -d -p {serverport}:80  -v {htmlroot}:/usr/share/nginx/html \
            --name {engin_name} --restart=always nginx')
    else:
        print(f'start docker container : {engin_name}')

        os.system(f'docker restart {engin_name}')

if __name__ == '__main__':
    install_docker()
    build_docker_container()