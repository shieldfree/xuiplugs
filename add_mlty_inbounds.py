import sqlite3
import json
import uuid
import random
import string
import re




def get_inbounds_fields_list(db,fielddname):
    # fields 是数据库中字段名称，str格式如 'id' 或 'port'
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.row_factory = lambda cursor, row:row[0]   # 特定的列加入到列表
    sql = f'select {fielddname} from inbounds ;'
    ids_list = c.execute(sql).fetchall()
    conn.close()
    return ids_list


def input_domain():
    pass
    while True:
        domain = input('请输入当前x-ui服务器域名:')
        pattern = "^[a-zA-Z0-9\-\.]+$"
        if re.match(pattern, domain):
            yesno = input(f'输入的域名为: {domain}, 确认请输入 y :')
            if yesno == 'y' or yesno == 'Y':
                return domain


def input_qty_of_inbounds(msg):
    while True:
        qty = input(msg)
        pattern = "^\d+$"
        if re.match(pattern, qty):
            if qty == '0':
                exit()
            return int(qty)
                # exit()



def gen_new_port_num(port_list,port_step):
    #生成新的端口号, 查找最大的端口号+ port_step生成
    # 但是如果生成的端口号大于65000, 则重新随机生成,
    # 检查与现有port_list不重复时返回新端口号.
    if len(port_list) == 0:
        # 第一个inbound的 端口号
        start_port =10000
    else:
        start_port = max(port_list) 

    while True:
        new_port = start_port +port_step +random.randint(1,10) #端口号最大的+port_step  方式生成

        if new_port > 65000:
            new_port = random.randint(10000,65000) # 超过65000 重新生成随机端口号
        if new_port not in port_list:
            # print( start_port)
            # print(new_port)
            # port_list.append(new_port)
            return new_port
        # start_port += port_step



def generate_random_str(length):
    letters = string.ascii_letters
    temp_str = ''
    for i in range(length):
        rand_letter = random.choice(letters)
        temp_str += rand_letter
    return temp_str

def add_new_inbounds(db,new_id,new_port,remark):
    # port = int(port) + portstep
    # tag = 'inbound-' + str(port)
    id = new_id
    user_id = 1 #同一个节点下的用户序号
    up, down = 0, 0
    t_uuid = str(uuid.uuid4())  # client 设置中的UUID
    total_lmt = 0
    remark= str(id)+remark
    enable = 1
    expiry_time = 0
    autoreset = 0
    ip_alert = 0
    ip_limit =0
    listen = ''
    port = new_port
    protocol = random.choice(['vmess', 'vless', 'trojan'])
    
    # settings sample of vless protocol
    settings_str  = '''{
    "clients": [
        {
        "id": "8b820943-1131-491a-abfb-7b4346e83ad8",
        "email": "xCvi.love@xray.com",
        "flow": "",
        "total": 0,
        "expiryTime": 0} ],
    "decryption": "none",
    "fallbacks": []
    }
    '''
    settings_json =json.loads(settings_str)
    #根据不同的协议， settings项目值填充
    if protocol == 'vmess':
        settings_json['clients'][0]['id'] = t_uuid
        settings_json['clients'][0]['email'] = generate_random_str(4) + '.love@xray.com'
        settings_json['clients'][0]['alterId'] = 0
        del settings_json['clients'][0]['flow']
        settings_json['clients'][0]['total'] = 0
        settings_json['clients'][0]['expiryTime'] = 0
        # settings_json['disableInsecureEncryption'] = 'false'   #总是开启？？
        del settings_json['decryption']
        del settings_json['fallbacks']

    elif protocol ==  'vless':
        settings_json['clients'][0]['id'] = t_uuid
        settings_json['clients'][0]['email'] = generate_random_str(4) + '.love@xray.com'
        settings_json['clients'][0]['flow'] = ''
        settings_json['clients'][0]['fingerprint'] = random.choice(['chrome','firefox','safari','ios','android','edge','360','qq','random','randomized'])
        settings_json['clients'][0]['total'] = 0
        settings_json['clients'][0]['expiryTime'] = 0
        settings_json['decryption'] = 'none'
        settings_json['fallbacks'] = []

    elif protocol == 'trojan':
        settings_json['clients'][0]['password'] = settings_json['clients'][0].pop('id')
        settings_json['clients'][0]['password'] = generate_random_str(10)
        settings_json['clients'][0]['flow'] = 'xtls-rprx-direct'
        settings_json['clients'][0]['total'] = 0
        settings_json['clients'][0]['expiryTime'] = 0
        del settings_json['decryption']
        settings_json['fallbacks'] = []
    
    settings = json.dumps(settings_json,ensure_ascii=False, indent='\t')

    stream_str = '''{
    "network": "tcp",
    "security": "tls",
    "tlsSettings": {
        "serverName": "xui.myserver.com.key",
        "minVersion": "1.2",
        "maxVersion": "1.3",
        "cipherSuites": "",
        "certificates": [{
            "certificateFile": "/root/cert/fullchain.cer",
            "keyFile": "/root/cert/xui.myserver.com.key"
            }],
        "alpn": ["h2","http/1.1"]
        },
    "tcpSettings": {
        "header": {
            "type": "none"
        },
        "acceptProxyProtocol": false}
    }
    '''
    stream_json = json.loads(stream_str)
    stream_json['network'] = random.choice(['tcp', 'ws'])  # tcp, ws
    stream_json['security'] = 'tls'
    stream_json['tlsSettings']['serverName'] = domain
    stream_json['tlsSettings']['certificates'][0]['certificateFile'] = '/root/cert/fullchain.cer'
    stream_json['tlsSettings']['certificates'][0]['keyFile'] = f'/root/cert/{domain}.key'


    if stream_json['network'] == 'tcp':
        stream_json['tcpSettings']['header']['type'] = 'none'
        # stream_json['tcpSettings']['acceptProxyProtocol'] ='false'    #总是开启？？

    elif stream_json['network'] == 'ws':
        stream_json['wsSettings'] = stream_json.pop('tcpSettings')
        stream_json['wsSettings']['path'] = '/'
        stream_json['wsSettings']['headers'] = ''
        # stream_json['wsSettings']['acceptProxyProtocol'] = 'false'    #总是开启？？


    stream_settings = json.dumps(stream_json,ensure_ascii=False, indent='\t')

    tag = 'inbound-' + str(port)
    sniffing_json = json.loads('{  "enabled": true, "destOverride": ["http", "tls"]}')
    sniffing = json.dumps(sniffing_json,ensure_ascii=False, indent='\t')
    sql = f'INSERT INTO  inbounds (id,user_id,up,down,total,remark,enable,expiry_time,autoreset,ip_alert,ip_limit,listen,port, \
                        protocol,settings,stream_settings,tag,sniffing)\
                        VALUES (?,?,?,?,?,   ?,?,?,?,?,  ?,?,?,?,?,  ?,?,?)'
    
    # sql_values = ({id},{user_id},{up},{down},{total_lmt},{remark},{enable},{expiry_time},{autoreset},{ip_alert},{ip_limit},{listen},{port}\
    #                         {protocol},{settings},{stream_settings},{tag},{sniffing})

    # print(settings,stream_settings) #for test

    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute(sql,(id,user_id,up,down,total_lmt,remark,enable,expiry_time,autoreset,ip_alert,ip_limit, \
                    listen,port,protocol,settings,stream_settings,tag,sniffing))
    conn.commit()
    conn.close()
    return 



import time # for test

if __name__ == '__main__':

    dbfile =  '/etc/x-ui/x-ui.db'
    # dbfile =  './x-ui.db'
    id_list = get_inbounds_fields_list(dbfile,'id')
    port_list = get_inbounds_fields_list(dbfile,'port')
    print('\n\n\n==== 注意： 添加完毕后 需要点击 重置流量按钮刷新节点信息 !!! ======\n====   并在系统状态页面重启一次xray!!! ====\n\n\n')
    print('根据输入的域名生成证书路径:')
    print('path to cert:/root/cert/fullchain.cer')
    print('path to key:/root/cert/YOUR_DOMAIN.key')
    domain = input_domain()

    msg = '请输入备注信息(如:usCA) :'
    remark = input(msg)

    msg ='请输入要添加的入站个数(0 退出) :'
    qty = input_qty_of_inbounds(msg)

    msg = '请输入端口间距100-500之间的数, (默认300) :'
    temp_port_step = input(msg)
    if temp_port_step == '':
        port_step = 300
    print('\n\n开始添加节点')
    for i in range(0,qty):
        new_port =gen_new_port_num(port_list,port_step)
        new_id = max(id_list) + 1
        
        print(new_id,new_port)

        add_new_inbounds(dbfile,new_id,new_port, remark)
        id_list.append(new_id)
        port_list.append(new_port)

        time.sleep(0.1)
    print(f'\n\n\n\n=== {qty}个节点添加完毕, 请点击x-ui面板 重置流量按钮!!! \n=== 并在系统状态页面重启一次xray,确认运行状态为running \n\n\n\n')
    input('按回车退出.')
    # gen_new_port_num()
    # print(port_list)
    # print('end')




