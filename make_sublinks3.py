
#!/usr/bin/python3

import sqlite3
import base64
import shutil
import paramiko
from scp import SCPClient
import os
import json
import platform
import configparser
import config_xuilist as confxuisrv
import config_sublinks as confsublink
from urllib.parse import quote
# import time

xui_srv_configfile = confxuisrv.xui_srv_configfile
xui_srv_config = configparser.ConfigParser()
xui_srv_config.read(xui_srv_configfile)

sublink_configfile = confsublink.sublink_configfile
sublink_config = configparser.ConfigParser()
sublink_config.read(sublink_configfile)



#XUI服务器list
servers = confxuisrv.get_servers()
#订阅链接list
subscription_list = confsublink.get_subscription_list()
#网站根目录
station = xui_srv_config.get('SUBSCRIPTIONSERVER', 'station_root')
# 订阅链接的存放地址
sublinks_path = xui_srv_config.get('SUBSCRIPTIONSERVER', 'sublinkfilepath')  
# 临时文件夹
temp_file_path = '/usr/local/x-ui/plugs/temp/'
#远程的xui 数据库文件复制到本地目录
dbfilepath = temp_file_path + 'x-ui_db/'
# 订阅服务器所在的域名
yourdomain = confxuisrv.xui_srv_config.get('SUBSCRIPTIONSERVER','subserver_domain')
# 提供订阅的服务器端口
sport = confxuisrv.xui_srv_config.get('SUBSCRIPTIONSERVER','serverport')

os.makedirs(station, exist_ok=True)



def createSSHClient(server, port, user, password):
    # 建立 ssh链接的函数
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client

def download_xui_db_file(servers):
    # 下载 x-ui 的数据库文件
    for server in servers:
        if not os.path.isdir(dbfilepath + server[0]):
            os.makedirs(dbfilepath + server[0])
        dbfile = dbfilepath + server[0] + "/x-ui.db"

        ssh = createSSHClient(server[0], 22, server[1], server[2])
        scp = SCPClient(ssh.get_transport())  
        scp.get('/etc/x-ui/x-ui.db',dbfile)
        print(f"成功从{server[0]}下载数据库文件保存到: {dbfile}" )
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



def get_inbound_link_by_json(db,id):
    # ,autorese,ip_alert,ip_limit
    sql = 'select id,user_id,up,down,total,remark,enable, expiry_time, listen,port\
        ,protocol,settings,stream_settings,tag,sniffing from inbounds where id ={};'.format(id)
    conn = sqlite3.connect(db)
    c = conn.cursor()
    slqresult = c.execute(sql).fetchall()
    inboundinfo = list(slqresult[0])
    conn.close()
    # print (inboundinfo)
    # return inboundinfo

    id =  inboundinfo[0]
    user_id =inboundinfo[1]
    up = inboundinfo[2]
    down = inboundinfo[3]
    total =inboundinfo[4]
    remark = inboundinfo[5]
    enable =inboundinfo[6]
    expiry_time = inboundinfo[7]
    # autoreset = inboundinfo[8]
    # ip_alert = inboundinfo[9]
    # ip_limit = inboundinfo[10]
    listen = inboundinfo[8]
    port = inboundinfo[9]
    protocol = inboundinfo[10]
    ''' settings
    {
    "clients": [
        {
        "id": "8b820943-1131-491a-abfb-7b4346e83ad8",
        "email": "xCvi.love@xray.com",
        "flow": ""
        }
    ],
    "decryption": "none",
    "fallbacks": []
    }'''
    settings = inboundinfo[11]
    settings_json = json.loads(settings)
    if protocol =='trojan': clients_id = settings_json["clients"][0]["password"]
    else: clients_id = settings_json["clients"][0]["id"]
    
    clients_email = settings_json["clients"][0]["email"]

    if protocol == 'vless':  
        clients_flow = settings_json["clients"][0]["flow"] 
        decryption = settings_json["decryption"]
        fallbacks = settings_json["fallbacks"]
    elif protocol == 'vmess': 
        # clients_alterId = settings_json["clients"][0]["alterId"]
        disableInsecureEncryption = settings_json["disableInsecureEncryption"]

    ''' stream_settings
    {
    "network": "tcp",
    "security": "tls",
    "tlsSettings": {
        "serverName": "sega.gitoff.one",
        "minVersion": "1.2",
        "maxVersion": "1.3",
        "cipherSuites": "",
        "certificates": [
        {
            "certificateFile": "/root/cert/fullchain.cer",
            "keyFile": "/root/cert/sega.gitoff.one.key"
        }
        ],

        "alpn": [
        "h2",
        "http/1.1"
        ]
    },
    "tcpSettings": {
        "header": {
        "type": "none"
        },
        "acceptProxyProtocol": false
    }'''
    stream_settings = inboundinfo[12]
    stream_settings_json = json.loads(stream_settings)
    network = stream_settings_json["network"] # network_type
    security = stream_settings_json["security"]

    if security == 'tls':
        # tls settings
        tlsSettings = stream_settings_json["tlsSettings"]
        serverName = stream_settings_json["tlsSettings"]["serverName"]
        minVersion = stream_settings_json["tlsSettings"]["minVersion"]
        maxVersion = stream_settings_json["tlsSettings"]["maxVersion"]
        cipherSuites = stream_settings_json["tlsSettings"]["cipherSuites"]
        rejectUnknownSni = stream_settings_json["tlsSettings"]["rejectUnknownSni"]
        # certificates = stream_settings_json["tlsSettings"]["certificates"]
        certificateFile = stream_settings_json["tlsSettings"]["certificates"][0]["certificateFile"]
        # keyFile = stream_settings_json["tlsSettings"]["certificates"][0]["keyFile"]
        keyFile = stream_settings_json["tlsSettings"]["certificates"][0]["keyFile"]
        ocspStapling = stream_settings_json["tlsSettings"]["certificates"][0]["ocspStapling"]

        alpn = stream_settings_json["tlsSettings"]["alpn"]  # alpn 的[] 要不要去掉??
        print(alpn)
        allowInsecure = stream_settings_json["tlsSettings"]["settings"]["allowInsecure"]
        fingerprint = stream_settings_json["tlsSettings"]["settings"]["fingerprint"]
    path = '/' # set default 
    header_type = 'None' # set default 
    if network == 'tcp':
        # tcpSettings = stream_settings_json["tcpSettings"]
        acceptProxyProtocol = stream_settings_json["tcpSettings"]["acceptProxyProtocol"]
        # header = stream_settings_json["tcpSettings"]["header"]
        header_type = stream_settings_json["tcpSettings"]["header"]["type"]
        
    elif network == 'ws':
        # wsSettings = stream_settings_json["wsSettings"]
        acceptProxyProtocol =  stream_settings_json["wsSettings"]["acceptProxyProtocol"]
        path = stream_settings_json["wsSettings"]["path"]
        headers = stream_settings_json["wsSettings"]["headers"]    
        


    tag = inboundinfo[13]
    sniffing = inboundinfo[14]
    sniffing_json = json.loads(sniffing)
    enabled = sniffing_json["enabled"]
    destOverride = sniffing_json["destOverride"]

    # print(settings_json)



    if protocol == 'vmess':
        vmess_link = '{'+ f'"v": "2",  "ps": "{remark}",  "add": "{serverName}",  "port": "{port}",  "id": "{clients_id}", \
                "net": "{network}",  "type": "{header_type}",  "tls": "{security}",  "path": "{path}",  "host": "{serverName}",\
                "sni": "{serverName}",  "alpn": "{alpn}"' +'}'
        vmess_link_json = {}
        vmess_link_json['v'] = "2"
        vmess_link_json['ps'] = remark
        vmess_link_json['add'] = serverName
        vmess_link_json['port'] = port
        vmess_link_json['id'] = clients_id
        vmess_link_json['net'] = network
        vmess_link_json['type'] = header_type
        vmess_link_json['tls'] = security
        vmess_link_json['path'] = path
        vmess_link_json['host'] = serverName
        vmess_link_json['sni'] = serverName
        vmess_link_json['alpn'] = alpn
        vmess_link = json.dumps(vmess_link_json)

        encoded_link_text = vmess_link.encode("utf-8")
        sublink = 'vmess://' + str(base64.b64encode(encoded_link_text)).split("'")[1]
        # print(sublink)
        
    elif protocol == 'vless' :
        sublink =  f'{clients_id}@{serverName}:{port}?type={network}&headerType=none&host={serverName}&security={security}&path={path}&sni={serverName}&flow=#{remark}'
        # 3x-ui
        sublink =   f'{clients_id}@{serverName}:{port}?type={network}&security={security}&fp={fingerprint}&alpn={alpn}&headerType={header_type}&sni={serverName}&host={serverName}&path={path}#{remark}'
        sublink = 'vless://' + quote(sublink)
    elif protocol == 'trojan' :
        sublink =  f'{clients_id}@{serverName}:{port}?type={network}&security={security}&path={path}&headerType=none#{remark}'
        # 3x-ui
        sublink =  f'{clients_id}@{serverName}:{port}?type={network}&security={security}&fp=&alpn={alpn}&path={path}&sni={serverName}#{remark}'
        sublink = 'trojan://' +quote(sublink)

    else:
        print(" unsupported protocol")

    # print(sublink)

    return sublink

def db_inquiry(db,sql): 
    # 测试用的
    # sql = 'select * from inbounds where id ={};'.format(id) # inbound's ID
    # sql = 'select id,user_id,up,down,total,remark,enable,expiry_time,autoreset,ip_alert,listen,port\
    #     ,protocol,settings,stream_settings,tag,sniffing,ip_limit from inbounds where id ={};'.format(id)
    # conn.row_factory = sqlite3.Row
    conn = sqlite3.connect(db)
    c = conn.cursor()
    slqresult = c.execute(sql).fetchall()
    inboundinfo = list(slqresult[0])
    for i, info in enumerate(inboundinfo):
        print(i, info)

def save_inbounds_all_in_onefile():
    # 旧的版本 单一文件
    linkfilepath = '/usr/local/x-ui/plugs/temp/x-ui_links/'
    for server in servers:
        db = dbfilepath + server[0] + "/x-ui.db"
        if not os.path.isdir(linkfilepath + server[0]):
            os.makedirs(linkfilepath + server[0],exist_ok=True)
        linkfile = linkfilepath + server[0] + f"/{server[0]}.sh"
        ids = make_id_list(db)
        sublinklist = []
        for id in ids:
            sublinklist.append(get_inbound_link_by_json(db,id))
        with open(linkfile,'w') as f:
            for link in sublinklist:
                f.write(link + '\n')
            print(f'{server[0]}的节点链接成功保存到:  {linkfile}')
            # os.remove(server[3])

def save_inbounds_links_to_dictionary():
    # 把生成的链接放入一个字典变量
    linkdict = {}
    for server in servers:
        db = dbfilepath + server[0] + "/x-ui.db"
        # if not os.path.isdir(linkfilepath + server[0]):
        #     os.makedirs(linkfilepath + server[0])
        ids = make_id_list(db)
        for id in ids:
            link = get_inbound_link_by_json(db,id)
            # link = get_inbound_link_by_json(db,id) # another way to get link

            # save links to each file named with nickname + Id
            # linkfile = linkfilepath + server[0] +"/" + server[3] + str(id)
            # with open(linkfile,'w') as f:
            #     f.write(link + '\n')
            # print(f'{server[0]}的{id}号节点链接成功保存到 {linkfile}')    

            # add links to a dictionary
            dictkey = server[3] + str(id)
            linkdict[dictkey]= link
            
            # os.remove(server[3])
    return linkdict

def make_sub_file(subscription,linkdict):
    
    if not os.path.isdir(sublinks_path ):
        os.makedirs(sublinks_path,exist_ok=True)
    os.system(f'rm -f {sublinks_path}/* ')
    #首个监控用的全节点集合
    for sub in subscription[0:1]:
        tempsubstr = ''
        # inboun_all = [x for x in linkdict.keys()]
        for value in linkdict.values():
            tempsubstr = tempsubstr + value + '\n'
        encoded_tempsubstr = str(base64.b64encode(tempsubstr.encode("utf-8"))).split("'")[1]
        with open(sublinks_path + sub[0],'w') as f:
                f.write(encoded_tempsubstr)
                print(f' succesfully saved file to {sublinks_path}{sub[0]} ')


    # 正常订阅节点
    for sub in subscription[1:]:
        tempsubstr = ''
        
        for inboun in sub[3:]:
            if linkdict.get(inboun):
                tempsubstr = tempsubstr + linkdict.get(inboun) + '\n'
            else: print(f'There is no inbound named {inboun}')
        
        encoded_tempsubstr = str(base64.b64encode(tempsubstr.encode("utf-8"))).split("'")[1]
        with open(sublinks_path + sub[0],'w') as f:
                f.write(encoded_tempsubstr)
                print(f' succesfully saved file to {sublinks_path}{sub[0]} ')

        # print(encoded_tempsubstr)
        pass

def make_default_homepage():
    # print('-- bulding default webpage file --')
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

    with open('./index.html','w') as defaultpage:
        defaultpage.writelines(lines)

    # for check if http service is running
    shutil.copyfile('./index.html',  sublinks_path + './index.html')
    shutil.move('./index.html', station + './index.html')





if __name__ == '__main__':

    #下载服务器数据库文件到本地
    download_xui_db_file(servers) 
    # 生成载入inbound link的字典
    linkdict = save_inbounds_links_to_dictionary()
    #生成订阅文件,放入网站目录
    make_sub_file(subscription_list,linkdict)
    make_default_homepage() #生成测试默认页面确认http是否运行用
    # 重启网站nginx服务,载入页面(订阅文件)
    os.system("docker restart `docker ps -a  | grep xuisubsrv | awk '{print $1}'`")
    
    for i, sublink in enumerate(subscription_list):
        uri = sublink[0]
        remark = sublink[2]
        sublinkfolder = sublinks_path.split('station/')[-1]
        if i == 0: print('0号订阅为管理用,包含全部节点')
        print(f'sublink{i:>2} : 备注: {remark}\n 订阅链接: http://{yourdomain}:{sport}/{sublinkfolder}{uri}')


