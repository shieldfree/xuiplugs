import configparser
import datetime
import time
import os

configfile ='/usr/local/x-ui/plugs/config/subscription.ini'
configfile = './config/subscription.ini'
if not os.path.exists(configfile):
    with open(configfile,'w') as f:
        f.write("")
config = configparser.ConfigParser()
config.read(configfile)

currenttime = datetime.datetime.now()
today_date =  currenttime.today().strftime('%Y-%m-%d')


def save_config():
    # save the configeration file
    with open(configfile, 'w') as file:
        config.write(file)


def gen_new_sublink_no():
    sublink_list= get_sublink_no_list()
    # 是否可以直接用 len（list） 生成， 前提删除的时候随时重新排序
    new_no = '1'
    if len(sublink_list) >0:
        for i in sublink_list:
            if int(i) > int(new_no):
                new_no =i
        new_no = str(int(new_no) + 1)
    # print(new_no)
    return new_no

def input_info(msg):
    temp = ''
    while not temp:
        temp = input(msg)
        if len(temp) == 0:
            # temp = ''
            print('请重新输入!! ')
    return temp

def input_yesno(msg):
    temp = ''
    while  temp not in ['y','n']:
        temp = input(msg)
        if temp in ['Y','y','yes','YES']:
            temp = 'y'
            return temp
        elif temp in ['N','n','NO','no']:
            temp = 'n'
            return temp
        elif temp == '':
            return temp
        print('请重新输入!! ')
    return temp

def get_sublink_info(sublink_no):
    sublink_sec = 'SUBSCRIPTION' + str(sublink_no)
    if config.has_section(sublink_sec):
        filename = config.get(sublink_sec,'filename')
        inbounds = config.get(sublink_sec,'inbounds')
        remark = config.get(sublink_sec,'remark')
        use_yesno = config.get(sublink_sec,'use_yesno')
        return [filename,inbounds,remark,use_yesno]
    # else:
    #     print(f'无server{sublink_no} 信息')
    #     return '','',''

def get_sublink_no_list():
    #生成 服务器序号 list, 文本
    section_list = config.sections()
    sublink_list = []
    for  sec in section_list:
        if 'SUBSCRIPTION' in sec:
            sublink_list.append(sec.replace('SUBSCRIPTION',''))
    return sublink_list

def show_all_sublinks():
    sublink_no_list = get_sublink_no_list()
    print('\n\n\n当前服务器信息如下:\n')
    print('=' * 80)
    for sublink_no in sublink_no_list:
        temp_data = get_sublink_info(sublink_no)
        filename = temp_data[0]
        inbounds = temp_data[1]
        remark =temp_data[2]
        use_yesno = temp_data[3]
        print(f'sublink{sublink_no:>2} | Filename: {filename:<20}| Use Y/N:{use_yesno} | remark:{remark:<6}|\n\t  | Inbounds:{inbounds:<10}')
        print('-' * 80)

def add_new_sublink(new_no):
    if int(new_no) > 30:
        print('订阅链接太多了。。加不了!')
        return
    msg = '请确认是否开始添加新的订阅链接 (Y/n)? :'
    yesno = input_yesno(msg)
    if yesno =='n' :
        print('取消添加订阅链接!')
        show_all_sublinks()
        return
    print(f'开始添加{new_no}号 订阅节点:')
    msg = '请输入文件名:'
    filename = input(msg)

    msg = '请输入订阅节点:'
    inbounds = input(msg)
    msg = '请输入链接备注信息:'
    remark = input(msg)
    # msg = '请输入服务器标签:'
    # tag = input_info(msg)
    use_yesno = 'y'
    print('要添加的订阅链接信息如下: ')
    print(f'''
        sublink{new_no:>2} | filename: {filename:<20}| Use Y/N:{use_yesno} | remark:{remark:<6}|\n\t  |Inbounds:{inbounds:<10}

    ''')
    msg = '请确认是否添加节点 (Y/n)? :'
    yesno = input_yesno(msg)
    if yesno =='y' or yesno == '':
        sublink_sec = 'SUBSCRIPTION' + str(new_no)
        config.add_section(sublink_sec)
        config.set(sublink_sec, 'filename', filename)
        config.set(sublink_sec, 'inbounds', inbounds)
        config.set(sublink_sec, 'remark', remark)
        config.set(sublink_sec, 'use_yesno', use_yesno)
        save_config()
        print('正在保存...')
        time.sleep(1)
        show_all_sublinks()
    elif yesno == 'n':
        print('取消添加订阅链接!')
        show_all_sublinks()
    return

def edit_sublink_info():
    sublink_no_list = get_sublink_no_list()
    show_all_sublinks()
    sublink_no = ''
    sublink_no = input('选择要编辑的服务器序号')
    if sublink_no in sublink_no_list:
        server_sec = 'SUBSCRIPTION' + sublink_no
        temp_data = get_sublink_info(sublink_no)
        filename = temp_data[0]
        inbounds = temp_data[1]
        remark =temp_data[2]
        use_yesno = temp_data[3]

        print(f'当前文件名: {filename}')
        temp_filename =input('输入新的域名(不修改直接回车):')
        if temp_filename != '':
            filename =temp_filename

        print(f'当前remark: {remark}')
        temp_remark =input('输入新的remark(不修改直接回车):')
        if temp_remark != '':
            remark =temp_remark

        print(f'当前使用状态: {use_yesno}')
        temp_use_yesno =input('输入新的密码(不修改直接回车):')
        if temp_use_yesno != '':
            use_yesno =temp_use_yesno

        print(f'当前inbounds 明细: {inbounds}')
        temp_inbounds =input('输入当前inbounds,以空格分开(不修改直接回车):')
        if temp_inbounds != '':
            use_yesno =temp_inbounds

        config.set(server_sec, 'filename', filename) 
        config.set(server_sec, 'filename', filename) 
        config.set(server_sec, 'use_yesno', use_yesno) 
        config.set(server_sec, 'use_yesno', use_yesno) 
        # config.set(server_sec, 'tag', domain.split('.')[0] + server_no) 
        save_config()
        print('完成修改!')
    else: 
        print('输入有误!')

def remove_server():
    server_no_list = get_sublink_no_list()
    show_all_servers()
    server_no = input('请输入要删除的服务器序号 :')
    if server_no in server_no_list:
        msg = f'请确认是否删除 {server_no}号 服务器(y/N)'
        yesno = input_yesno(msg)
        if yesno =='y':
            server_sec = 'XUISERVER' + server_no
            config.remove_section(server_sec)
            save_config()
            sorting_servers()
            # show_all_servers
        else:
            print('取消删除')
            # show_all_servers
    else:

        print('序号输入错误！')
        time.sleep(1)
        show_all_servers()


def sorting_servers():
    # 每次有删减,重新 从1号开始排序
    # msg = '确认是否进行排序(y/N)'
    # yesno = input_yesno(msg)
    # if yesno == 'y':
        server_no_list = sorted(get_sublink_no_list())
        for i,server_no in enumerate(server_no_list):
            if server_no != str(i+1):
                new_server_sec = 'XUISERVER' + str(i+1)
                old_server_sec = 'XUISERVER' + server_no
                config.add_section(new_server_sec)
                domain, username, password = get_sublink_info(server_no)
                config.set(new_server_sec, 'domain', domain) 
                config.set(new_server_sec, 'username', username) 
                config.set(new_server_sec, 'password', password) 
                config.remove_section(old_server_sec)
                # save_config()
            elif server_no == str(i+1):
                domain, username, password = get_server_info(server_no)
                server_sec = 'XUISERVER' + server_no
                config.remove_section(server_sec)
                config.add_section(server_sec)
                config.set(server_sec, 'domain', domain)
                config.set(server_sec, 'username', username)
                config.set(server_sec, 'password', password)
        save_config()
        print(' 服务器重新排序 !!')
    # else:
    #     print('取消重新排序')

def select_main_option(msg):
    option_no = ''

    menu = '''
        ===X-UI服务器===
        0. 返回
        1. 添加
        2. 修改
        3. 删除
    
    '''

    # while  True :
        # show_all_servers()
        # print(menu)
    option_no = input(msg)

    return option_no


def main():
    while True:
        show_all_sublinks()
        menu = '''
            ===X-UI服务器===
            0. 返回
            1. 添加
            2. 修改
            3. 删除
            4. 重新排序
            ===订阅服务器==
            5.

            ===============
            9. 退出
        
        '''
        print(menu)


        msg = '请输入操作菜单序号:'
        option_no = input(msg)
        
        if option_no not in ['0', '1','2', '3', '4','9']:
            print('输入有误请重新输入!! ')
            time.sleep(1)
            continue
            print('test')
        elif option_no == '0':
            show_all_sublinks()
        elif option_no == '1':
            new_no = gen_new_sublink_no()
            add_new_sublink(new_no)

        elif option_no == '2':
            edit_sublink_info()

        elif option_no == '3':
            remove_server()

        elif option_no == '4':
            sorting_servers()

        elif option_no == '9':
            exit()
        time.sleep(1)






if __name__ == '__main__':

    # main()
    # filename,inbounds,remark,use_yesno = get_sublink_info(1)
    # inbound_temp = inbounds.split(' ')
    # print(inbound_temp)
    
    # sublink_no_list = get_sublink_no_list()
    # print(sublink_no_list)
    # show_all_sublinks()

    # new_no = gen_new_sublink_no()
    # add_new_sublink(new_no)
    
    edit_sublink_info()