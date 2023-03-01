
#!/usr/bin/python3
# this is the scripts use for write data using status to remark
# 
# crontab -e 添加一行:   */10 * * * *  python3 xuiplug_data2remark.py


import sqlite3
import datetime
import os
import random


current_time = datetime.datetime.now()
print(f"port changer is running {current_time}")

if os.path.isdir('/etc/x-ui/'):
    dbfile = '/etc/x-ui/x-ui.db'
else: dbfile = './x-ui.db'    #for local test

def gen_remark_date():

    current_time = datetime.datetime.now()

    hrand = random.randint(1,6) # fake time
    mrand = random.randint(1,60)
    hrand = "%02d" % current_time.hour
    mrand = "%02d" % current_time.minute
    ddate = "%02d" % current_time.day
    remark_date = f'_{ddate}{hrand}{mrand}' # make fake time
    return remark_date

def make_id_list(db):
    # get all id save to a list
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.row_factory = lambda cursor, row:row[0]
    sql = 'select * from inbounds ;'
    ids_list = c.execute(sql).fetchall()
    conn.close()
    return ids_list


def db_inquiry(db,id): 

    sql = f'select id,port,up,down,total,remark,tag from inbounds where id ={id};'
    conn = sqlite3.connect(db)
    c = conn.cursor()
    slqresult = c.execute(sql).fetchall()
    conn.close()
    inboundinfo = list(slqresult[0])

    id = inboundinfo[0]
    port = inboundinfo[1]
    up_data = int(inboundinfo[2] / 1000000)
    down_data = int(inboundinfo[3] / 1000000)
    datasum = up_data + down_data
    remark = inboundinfo[5]
    tag = inboundinfo[6]
    # print(f' id: {id},  port : {port}, data: {datasum}, remark : {remark}, tag : {tag}')
    return id, port, datasum,remark

def get_data_usage(db,id): 
    # get data usage 
    sql = f'select id,up,down,total,remark from inbounds where id ={id};'
    conn = sqlite3.connect(db)
    c = conn.cursor()
    slqresult = c.execute(sql).fetchall()
    # conn.close()
    inboundinfo = list(slqresult[0])
    id = inboundinfo[0]
    up_data = int(inboundinfo[1] / 1024 / 1024)
    down_data = int(inboundinfo[2] / 1024 / 1024)
    temp_used_data = up_data + down_data   #MB
    total = int(int(inboundinfo[3]) / 1024 / 1024)
    # remark = inboundinfo[4]
    # if '_' not in remark: remark = remark + '_0'
    # if '◔' not in remark: remark = remark + '_◔ 0MB◕ 0MB'
    # remaindata = int(remark.split('◕')[-1].split('MB')[0])
    if total == 0:
        remaindata = '99999'
    elif total > 0:
        remaindata = total - temp_used_data   # MB
        if remaindata < 0 :  remaindata = 0

    return temp_used_data, remaindata

def write_usage_info_to_remark(db,id,remark):
    sql = 'Update inbounds set remark = ? where id =?;'     #, up = 0, down = 0
    conn = sqlite3.connect(db)
    # conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute(sql,(remark, id))
    conn.commit()
    conn.close()


def reset_remark_data(db,id):
    sql = 'Update inbounds set  remark = ? where id =?;'  #, up = 0, down = 0
    remark_date = gen_remark_date()
    id, port, datasum,remark = db_inquiry(db,id)

    remark = remark.split('_')[0] + remark_date + '_◔0MB ◕0MB'
    conn = sqlite3.connect(db)
    # conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute(sql,(remark, id))
    conn.commit()
    conn.close()





def main_show_usage():
    ids = make_id_list(dbfile)
    for id in ids :
        id,port, datasum,remark = db_inquiry(dbfile,id) 
        if '_' not in remark: remark = remark + '_0'
        if '◔' not in remark: remark = remark + '_◔0MB ◕0MB'
        useddata = remark.split('◔')[-1].split('MB')[0]
        remaindata = remark.split('◕')[-1].split('MB')[0]
        temp_used_data ,remaindata = get_data_usage(dbfile,id)
        # useddata = str(int(useddata) + int(curr_useddata))     

        # print(useddata,remaindata)
        remark = remark.split('_')[0] + gen_remark_date() + f'_◔{temp_used_data}MB'# ◕{remaindata}MB'
        print(remark)


        write_usage_info_to_remark(dbfile,id,remark)


    # if os.path.isdir('/etc/x-ui/'):
    #     print('x-ui restarting... ')
    #     os.system('x-ui restart') 



if __name__ == '__main__':
    main_show_usage()


