#!/usr/bin/python3


# input your servers and subscription information below first

servers = [
# servers 
    ["xui.yourdomain1.xxx","root" ,"password", "sega"], # domain, username, password, nickname
    ["xui.yourdomain2.xxx","root" ,"password", "kinder"]  
    ]



subscription_list =[
#  
# format  'filename', nickname +Id,
['allinoneformonitoring.txt'                     ],
['subscribefilename1.txt', 'sega31', 'sega2'      ],
['subscribefilename2.txt', 'kinder1', 'kinder2'  ],
['subscribefilename3.txt', 'kinder3', 'kinder4'  ],
['subscribefilename4.txt', 'sega5', 'kinder5'    ]

]



# import time
# import sys
import sqlite3
import base64
import os
import json
import platform
import shutil
# import subprocess
import pkg_resources

required = {'docker','paramiko','scp'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed
if missing:
    # os.system('pip3 install sqlite3')
    os.system('pip3 install docker')
    os.system('pip3 install paramiko')
    os.system('pip3 install scp')
    # os.system('pip3 install json')

from scp import SCPClient
import paramiko
import docker



dbfilepath = './temp/x-ui/x-ui_db/'
linkfilepath = './temp/x-ui/x-ui_links/'
htmlroot = '/usr/x-ui/html/'     #website root folder
port = 18080
engin_name = 'xuisubnginx'
yourdomain = 'test.tacdc.top'



linuxplatf = platform.version()

if not os.path.isdir(htmlroot):
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

    if 'Centos' in linuxplatf:
        print('-- updating --')
        os.system('yum update -y')
        print('-- upgrading --')
        os.system('yum upgrade -y')
        os.system('yum install docker.io -y')


def build_docker_container():
    docker_client = docker.from_env()
    try:
        container = docker_client.containers.get(engin_name)
    except docker.errors.NotFound as exc: 
        # if the container not exist build new oen
        print(f'-- buld docker container name:{engin_name} site root: {htmlroot} --')
        os.system(f'docker run -d -p {port}:80  -v {htmlroot}:/usr/share/nginx/html \
            --name {engin_name} --restart=always nginx')
    else:
        print(f'start docker container : {engin_name}')
        # if the container  exist, delete it and rebuild it (update)
        # os.system(f'docker stop {engin_name}')
        # os.system(f'docker rm {engin_name}')
        # os.system(f'docker run -d -p {port}:80  -v {htmlroot}:/usr/share/nginx/html \
        #     --name {engin_name} --restart=always nginx')

        # or just restart it
        os.system(f'docker restart {engin_name}')



def make_default_homepage():
    print('-- bulding default webpage file --')            
    with open(htmlroot +'index.html','w') as defaultpage:
        lines = [
        '<!DOCTYPE html> \n',
        '<html> \n',
        '<head>\n',
        '<title>Error</title>\n',
        '<style>\n',
        'html { color-scheme: light dark; }\n',
        'body { width: 35em; margin: 0 auto;\n',
        'font-family: Tahoma, Verdana, Arial, sans-serif; }\n',
        '</style>\n',
        '</head>\n',
        '<body>\n',
        '<h1>An error occurred.</h1>\n',
        '<p>Sorry, the page is currently unavailable.<br/>\n',
        'Please try again later.</p>\n',
        '<p>If you are the system administrator of this resource then you should check\n',
        'the error log for details.</p>\n',
        '<p><em>Faithfully yours, nginx.</em></p>\n',
        '</body>\n',
        '</html>\n'
        ]
        defaultpage.writelines(lines)

    print(f'http://{yourdomain}:{port}/index.html')



def createSSHClient(server, port, user, password):
    # 建立 ssh链接的函数
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client


def download_xui_db_file():
    # 下载 x-ui 的数据库文件
    for server in servers:
        if not os.path.isdir(dbfilepath + server[0]):
            os.makedirs(dbfilepath + server[0])
        dbfile = dbfilepath + server[0] + "/x-ui.db"

        ssh = createSSHClient(server[0], 22, server[1], server[2])
        scp = SCPClient(ssh.get_transport())  
        scp.get('/etc/x-ui/x-ui.db',dbfile)
        print(f" save db file of {server[0]} to  : {dbfile}" )
        ssh.close()
    return 


def make_id_list(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    # conn.row_factory = lambda cursor, row:[row[0], row[5]] # 特定的列加入到列表
    c.row_factory = lambda cursor, row:row[0]   # 特定的列加入到列表
    sql = 'select * from inbounds ;'
    ids_list = c.execute(sql).fetchall()
    conn.close()
    return ids_list


def get_inbound_link(db,id):

    sql = 'select id,user_id,up,down,total,remark,enable,expiry_time,autoreset,ip_alert\
        ,listen,port,protocol,settings,stream_settings,tag,sniffing,ip_limit from inbounds where id ={};'.format(id)
    conn = sqlite3.connect(db)
    c = conn.cursor()
    slqresult = c.execute(sql).fetchall()
    inboundinfo = list(slqresult[0])
    conn.close()
    protocol = inboundinfo[12]
    v = 2
    ps = inboundinfo[5]

    add = inboundinfo[14].split('"serverName": "')[1].split('"')[0]
    if add =='': 
        print(f'id# {id} :   serverName info is empty!! ')
        return

    port = inboundinfo[11]

    if protocol == 'trojan':  userid =  inboundinfo[13].split('"password": "')[1].split('"')[0]
    else :  userid = inboundinfo[13].split('"id": "')[1].split('"')[0]

    if protocol == 'vmess':
        alterid = inboundinfo[13].split('"alterId": ')[1].split(' ')[0]
    else : alterid = 0

    network = inboundinfo[14].split('"network": "')[-1].split('"')[0]
    type1 = 'None'

    host = inboundinfo[14].split('"host": "')[-1].split('"')[0]
    if len(host) <= 5 : host = ''

    if network == 'ws':
        path = inboundinfo[14].split('"path": "')[1].split('"')[0]
    else:  path = '/' 

    tls =  inboundinfo[14].split('"security": "')[1].split('"')[0]

    sniffing = ""
    alpn =  inboundinfo[14].split('"alpn": ')[1].split(']')[0].replace('\n','').replace('[','').replace(' ','').replace('"','')



    if protocol == 'vmess':
        link_text = '{'+ f'"v": "2",  "ps": "{ps}",  "add": "{add}",  "port": "{port}",  "id": "{userid}", \
                "aid": "{alterid}",  "net": "{network}",  "type": "{type1}",  "host": "{host}",  "path": "{path}",  "tls": "{tls}"' +'}'
        encoded_link_text = link_text.encode("utf-8")
        sublink = 'vmess://' + str(base64.b64encode(encoded_link_text)).split("'")[1]
    elif protocol == 'vless' :
        sublink = 'vless://' + f'{userid}@{add}:{port}?type={network}&headerType=none&host={host}&security={tls}&path={path}&sni={add}&flow=#{ps}'
    elif protocol == 'trojan' :
        sublink = 'trojan://' + f'{userid}@{add}:{port}?type={network}&security={tls}&path={path}&headerType=none#{ps}'
    else:
        print(" unsupported protocol")

    # print(sublink)

    return sublink


def get_inbound_link_by_json(db,id):
    # another way to get inbounds setting and link
    sql = 'select id,user_id,up,down,total,remark,enable,expiry_time,autoreset,ip_alert,ip_limit,listen,port\
        ,protocol,settings,stream_settings,tag,sniffing from inbounds where id ={};'.format(id)
    conn = sqlite3.connect(db)
    c = conn.cursor()
    slqresult = c.execute(sql).fetchall()
    inboundinfo = list(slqresult[0])
    conn.close()
    id =  inboundinfo[0]
    user_id =inboundinfo[1]
    up = inboundinfo[2]
    down = inboundinfo[3]
    total =inboundinfo[4]
    remark = inboundinfo[5]
    enable =inboundinfo[6]
    expiry_time = inboundinfo[7]
    autoreset = inboundinfo[8]
    ip_alert = inboundinfo[9]
    ip_limit = inboundinfo[10]
    listen = inboundinfo[11]
    port = inboundinfo[12]
    protocol = inboundinfo[13]
    settings = inboundinfo[14]
    settings_json = json.loads(settings)
    if protocol =='trojan': clients_id = settings_json["clients"][0]["password"]
    else: clients_id = settings_json["clients"][0]["id"]

    clients_email = settings_json["clients"][0]["email"]

    if protocol == 'vless':  
        clients_flow = settings_json["clients"][0]["flow"] 
        decryption = settings_json["decryption"]
        fallbacks = settings_json["fallbacks"]
    elif protocol == 'vmess': 
        clients_alterId = settings_json["clients"][0]["alterId"]
        disableInsecureEncryption = settings_json["disableInsecureEncryption"]

    stream_settings = inboundinfo[15]
    stream_settings_json = json.loads(stream_settings)
    network = stream_settings_json["network"] # network_type
    security = stream_settings_json["security"]
    tlsSettings = stream_settings_json["tlsSettings"]
    serverName = stream_settings_json["tlsSettings"]["serverName"]
    minVersion = stream_settings_json["tlsSettings"]["minVersion"]
    maxVersion = stream_settings_json["tlsSettings"]["maxVersion"]
    cipherSuites = stream_settings_json["tlsSettings"]["cipherSuites"]
    certificates = stream_settings_json["tlsSettings"]["certificates"]
    certificateFile = stream_settings_json["tlsSettings"]["certificates"][0]["certificateFile"]
    keyFile = stream_settings_json["tlsSettings"]["certificates"][0]["keyFile"]
    alpn = stream_settings_json["tlsSettings"]["alpn"]
    path = '/' # set default 
    header_type = 'None' # set default 
    if network == 'tcp':
        tcpSettings = stream_settings_json["tcpSettings"]
        header = stream_settings_json["tcpSettings"]["header"]
        header_type = stream_settings_json["tcpSettings"]["header"]["type"]
        acceptProxyProtocol = stream_settings_json["tcpSettings"]["acceptProxyProtocol"]

    elif network == 'ws':
        wsSettings = stream_settings_json["wsSettings"]
        path = stream_settings_json["wsSettings"]["path"]
        headers = stream_settings_json["wsSettings"]["headers"]    
        acceptProxyProtocol =  stream_settings_json["wsSettings"]["acceptProxyProtocol"]



    tag = inboundinfo[16]
    sniffing = inboundinfo[17]
    sniffing_json = json.loads(sniffing)
    enabled = sniffing_json["enabled"]
    destOverride = sniffing_json["destOverride"]



    # print(settings_json)



    if protocol == 'vmess':
        link_text = '{'+ f'"v": "2",  "ps": "{remark}",  "add": "{serverName}",  "port": "{port}",  "id": "{clients_id}", \
                "aid": "{clients_alterId}",  "net": "{network}",  "type": "{header_type}",  "host": "{serverName}",  "path": "{path}",  "tls": "{security}"' +'}'
        encoded_link_text = link_text.encode("utf-8")
        sublink = 'vmess://' + str(base64.b64encode(encoded_link_text)).split("'")[1]
        # print(sublink)

    elif protocol == 'vless' :
        sublink = 'vless://' + f'{clients_id}@{serverName}:{port}?type={network}&headerType=none&host={serverName}&security={security}&path={path}&sni={serverName}&flow=#{remark}'

    elif protocol == 'trojan' :
        sublink = 'trojan://' + f'{clients_id}@{serverName}:{port}?type={network}&security={security}&path={path}&headerType=none#{remark}'

    else:
        print(" unsupported protocol")

    # print(sublink)

    return sublink



def save_inbounds_to_eachfile():
    linkdict = {}
    for server in servers:
        db = dbfilepath + server[0] + "/x-ui.db"
        if not os.path.isdir(linkfilepath + server[0]):
            os.makedirs(linkfilepath + server[0])
        ids = make_id_list(db)
        for id in ids:
            link = get_inbound_link(db,id)
            dictkey = server[3] + str(id)
            linkdict[dictkey]= link

    return linkdict


def make_sub_file(subscription,linkdict):
    if not os.path.isdir(htmlroot ):
        os.makedirs(htmlroot )

    #首个监控用的全节点集合
    for sub in subscription[0:1]:
        tempsubstr = ''
        for value in linkdict.values():
            tempsubstr = tempsubstr + value + '\n'
        encoded_tempsubstr = str(base64.b64encode(tempsubstr.encode("utf-8"))).split("'")[1]
        with open(htmlroot + sub[0],'w') as f:
                f.write(encoded_tempsubstr)
                print(f' succesfully saved subscription file to {htmlroot}{sub[0]} ')

    # 订阅节点
    for sub in subscription[1:]:
        tempsubstr = ''

        for inboun in sub[1:]:
            if linkdict.get(inboun):
                tempsubstr = tempsubstr + linkdict.get(inboun) + '\n'
            else: print(f'There is no inbound named {inboun}')
        encoded_tempsubstr = str(base64.b64encode(tempsubstr.encode("utf-8"))).split("'")[1]
        with open(htmlroot + sub[0],'w') as f:
                f.write(encoded_tempsubstr)
                # print(f' succesfully saved subscription file to {htmlroot}{sub[0]} ')

        print(f'http://{yourdomain}:{port}/{sub[0]}')



#执行3： 各id 分别保存， 返回字典
if not shutil.which('docker'):
    install_docker()
    build_docker_container()
    make_default_homepage()
else:
    build_docker_container()
    make_default_homepage()

download_xui_db_file()  #download x-ui.db file to local temp folder
linkdict = save_inbounds_to_eachfile() # save inbounds info to a list with name: nickname+Id
make_sub_file(subscription_list,linkdict) # save subscription file to website folder
print(f'http://{yourdomain}:{port}/{subscription_list[0][0]}')

