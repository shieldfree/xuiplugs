
#!/usr/bin/python3
# 这个脚本配合订阅管理脚本, 定时自动更换端口号
#  

import sqlite3
import datetime
import os
import configparser

# import random
# 读取设置
configfile = './config/xuiplugconf.ini'
config = configparser.ConfigParser()
portchanger_section = 'PORTCHANGER'
config.read(configfile)

def save_config():
    # save the configeration file
    with open(configfile, 'w') as file:
        config.write(file)


#最后一次运行时间（确认当天是否运行过
current_time = datetime.datetime.now()
today_date =  current_time.today().strftime('%Y-%m-%d')
lastupdateddate = config.get(portchanger_section,'updateddate')
datamax = int(config.get(portchanger_section,'datamaximum'))  #(MB)
portstep = int(config.get(portchanger_section,'portstep')) # the step of port number daily changed for
data_usage_reset_date = config.get(portchanger_section,'data_usage_reset_date')
port_change_cycle_day = int(config.get(portchanger_section,'port_change_cycle_day')) # change port per day
current_date_num = current_time.today().strftime('%d')
evenodd_yesno = config.get(portchanger_section,'evenodd_yesno')
datamax_yesno = config.get(portchanger_section,'datamax_yesno')

dayevenodd = current_time.day % port_change_cycle_day
print(f"port changer is running {current_time}")


if os.path.isdir('/etc/x-ui/'):
    dbfile = '/etc/x-ui/x-ui.db'
else: dbfile = './x-ui.db'    #for local test


def gen_remark_date():

    current_time = datetime.datetime.now()

    # hrand = random.randint(1,6) #  make a fake time
    # mrand = random.randint(1,60) # make a fake time
    ddate = "%02d" % current_time.day
    hrand = "%02d" % current_time.hour
    mrand = "%02d" % current_time.minute
    remark_date = f'_{ddate}{hrand}{mrand}'
    return remark_date

def make_id_list(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    # conn.row_factory = lambda cursor, row:[row[0], row[5]] # 特定的列加入到列表
    c.row_factory = lambda cursor, row:row[0]   # 特定的列加入到列表
    sql = 'select * from inbounds ;'
    ids_list = c.execute(sql).fetchall()
    conn.close()
    return ids_list

def db_inquiry(db,id): 

    sql = f'select id,port,up,down,total,remark,tag from inbounds where id ={id};'
    conn = sqlite3.connect(db)
    c = conn.cursor()
    slqresult = c.execute(sql).fetchall()
    # conn.close()
    inboundinfo = list(slqresult[0])

    id = inboundinfo[0]
    port = inboundinfo[1]
    up_data = int(inboundinfo[2] / 1024 / 1024)
    down_data = int(inboundinfo[3] / 1024 /1024)
    datasum = up_data + down_data
    remark = inboundinfo[5]
    tag = inboundinfo[6]
    # print(f' id: {id},  port : {port}, data: {datasum}, remark : {remark}, tag : {tag}')
    return id, port, datasum,remark

def db_update_portadd(db,id,port,remark):
    port = int(port) + portstep
    tag = 'inbound-' + str(port)
    sql = 'Update inbounds set port = ?, tag = ? where id =?;'  #, remark = ?, up = 0, down = 0
    remark_date = gen_remark_date()
    # remark = remark.split('_')[0]  +remark.split('_')[-1]#+ remark_date
    conn = sqlite3.connect(db)
    # conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute(sql,(port, tag, id))  # remark,
    conn.commit()
    conn.close()
    # print(f'id: {id} 的端口号变更！ new port: {port}, new tag: {tag}')

def db_update_data_usage_reset(db,id):
    # port = int(port) + portstep
    # tag = 'inbound-' + str(port)
    sql = f'Update inbounds set   up = 0, down = 0 where id ={id};'  #, remark = ?
    # remark_date = gen_remark_date()
    # remark = remark.split('_')[0]  +remark.split('_')[-1]#+ remark_date
    conn = sqlite3.connect(db)
    # conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute(sql)  # remark,
    conn.commit()
    conn.close()
    # print(f'id: {id} 的端口号变更！ new port: {port}, new tag: {tag}')


# # 执行凌晨4点多运行,流量大于datamax的或按单双号更改端口
def care_port_evenodd():
    ids = make_id_list(dbfile)
    for id in ids :
        id,port, datasum,remark = db_inquiry(dbfile,id) 
        if '_' not in remark: remark = remark + '_0'
        if id % port_change_cycle_day == dayevenodd : 
            if remark.split('_')[1] != str(current_time.day) :
                db_update_portadd(dbfile,id,port,remark)
                id,newport, newdatasum,newremark = db_inquiry(dbfile,id)
                print(f'even odd :{id:>2}{port:>8} {datasum:>8}MB {remark:<30} changed to:{newport:>8}{newdatasum:>8}MB {newremark:<30}')
            else:
                id,port, datasum,remark = db_inquiry(dbfile,id)
                print(f'unchanged:{id:>2}{port:>8} {datasum:>8}MB {remark:<30}')                

        # elif  datasum >= datamax :#and remark.split('_')[1] != str(current_time.day) : 
        #     db_update_portadd(dbfile,id,port,remark) 
        #     id, port, datasum,remark = db_inquiry(dbfile,id)
        #     id,newport, newdatasum,newremark = db_inquiry(dbfile,id)
        #     print('maxdata  : ',id, port, datasum,remark, 'changed to:', newport, newdatasum,newremark)

        else: 
            id,newport, newdatasum,newremark = db_inquiry(dbfile,id)
            print(f'unchanged:{id:>2}{newport:>8} {newdatasum:>8}MB {newremark:<30}')
def restart_xui():
    if os.path.isdir('/etc/x-ui/'):
        print('x-ui restarting... ')
        os.system('x-ui restart') 

def care_port_maximiumdata():
    ids = make_id_list(dbfile)
    for id in ids :
        id,port, datasum,remark = db_inquiry(dbfile,id) 
        if '_' not in remark: remark = remark + '_0'
        if '◔' not in remark: continue
        remark_data_usage = int(remark.split('◔')[-1].split('MB')[0])
        if  datasum - remark_data_usage  > datamax :#and remark.split('_')[1] != str(current_time.day) : 
            db_update_data_usage_reset(dbfile,id) 
            id, datasum,port,remark = db_inquiry(dbfile,id)
            id,newport, newdatasum,newremark = db_inquiry(dbfile,id)
            print(f'maxdata  : {id:>2}{port:>8}{datasum:>8}   {remark:<30}, changed to: {newport:>8} {newdatasum:>8} {newremark:<30}')

        else: 
            id,newport, newdatasum,newremark = db_inquiry(dbfile,id)
            print(f'unchanged: {id:>2}{newport:>8}{newdatasum:>8}   {newremark:<30}')

# if current_time.hour == 2:
#     care_port()
def main_port_changer():
    if today_date == lastupdateddate:
        print('今天已经更新过端口！')
    else:
        start_time = current_time.today().strftime('%Y-%m-%d %H:%M:%S')
        config.set(portchanger_section,'start_time',start_time)

        if evenodd_yesno == 'y':
            care_port_evenodd()
            print('单双号规则，端口号变更完毕！')
        if datamax_yesno == 'y':
            care_port_maximiumdata()
            print('流量上限规则，端口号变更完毕！')
        end_time = current_time.today().strftime('%Y-%m-%d %H:%M:%S')
        config.set(portchanger_section,'end_time',end_time)
        config.set(portchanger_section,'updateddate',today_date) # 
        save_config()
        restart_xui()
if int(data_usage_reset_date) == int(current_date_num):
        print('数据清零...')
        ids = make_id_list(dbfile)
        for id in ids:
            db_update_data_usage_reset(dbfile,1)

if __name__ == '__main__':
    main_port_changer()
