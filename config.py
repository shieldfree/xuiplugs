import configparser
import datetime
import time
import os

configfile ='/usr/local/x-ui/plugs/config/xuiplugconf.ini'
if not os.path.exists(configfile):
    with open(configfile,'w') as f:
        f.write("")
config = configparser.ConfigParser()
config.read(configfile)

currenttime = datetime.datetime.now()
today_date =  currenttime.today().strftime('%Y-%m-%d')

def load_config(configfile):
    config.read(configfile)

def save_config():
    # save the configeration file
    with open(configfile, 'w') as file:
        config.write(file)
    load_config(configfile)

def gen_new_server_no():
    server_list= get_server_no_list()
    
    new_no = '1'
    if len(server_list) >0:
        for i in server_list:
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

def get_server_info(server_no):
    server_sec = 'XUISERVER' + server_no
    if config.has_section(server_sec):
        domain = config.get(server_sec,'domain')
        username = config.get(server_sec,'username')
        password = config.get(server_sec,'password')
        return domain,username,password
    else:
        print(f'无server{server_no} 信息')
        return '','',''

def get_server_no_list():
    #生成 服务器序号 list, 文本
    section_list = config.sections()
    server_list = []
    for  sec in section_list:
        if 'XUISERVER' in sec:
            server_list.append(sec.replace('XUISERVER',''))
    return server_list

def show_all_servers():
    server_list = get_server_no_list()
    print('\n\n\n当前服务器信息如下:\n')
    print('=' * 80)
    for server_no in server_list:
        domain,username,password = get_server_info(server_no)
        print(f'{server_no}号服务器:  | 域名:{domain:<20} | 用户名:{username:<10} | 密码:{password:<20}')
        print('-' * 80)

def add_server(new_no):
    if int(new_no) > 9:
        print('服务器太多了。。加不了!')
        return
    msg = '请确认是否开始添加新的X-UI服务器 (Y/n)? :'
    yesno = input_yesno(msg)
    if yesno =='n' :
        print('取消添加服务器信息!')
        show_all_servers()
        return
    print(f'开始添加{new_no}号 X-UI服务器:')
    msg = '请输入服务器域名:'
    domain = input_info(msg)
    msg = '请输入服务器登录用户名:'
    username = input_info(msg)
    msg = '请输入服务器登录密码:'
    password = input_info(msg)
    # msg = '请输入服务器标签:'
    # tag = input_info(msg)
    print('要添加的服务器信息如下: ')
    print(f'''
        域名：  {domain}
        用户名：{username}
        密码：  {password}
    ''')
    msg = '请确认是否添加 (Y/n)? :'
    yesno = input_yesno(msg)
    if yesno =='y' or yesno == '':
        server_sec = 'XUISERVER' + new_no
        config.add_section(server_sec)
        config.set(server_sec, 'domain', domain)
        config.set(server_sec, 'username', username)
        config.set(server_sec, 'password', password)
        save_config()
        print('正在保存...')
        time.sleep(1)
        show_all_servers()
    elif yesno == 'n':
        print('取消添加服务器信息!')
        show_all_servers()
    return

def edit_server_info():
    server_no_list = get_server_no_list()
    show_all_servers()
    server_no = ''
    server_no = input('选择要编辑的服务器序号')
    if server_no in server_no_list:
        server_sec = 'XUISERVER' + server_no
        domain, username, password = get_server_info(server_no)
        print(f'当前域名: {domain}')
        temp_domain =input('输入新的域名(不修改直接回车):')
        if temp_domain != '':
            domain =temp_domain

        print(f'当前用户名: {username}')
        temp_username =input('输入新的用户名(不修改直接回车):')
        if temp_username != '':
            username =temp_username

        print(f'当前密码: {password}')
        temp_password =input('输入新的密码(不修改直接回车):')
        if temp_password != '':
            password =temp_password

        config.set(server_sec, 'domain', domain) 
        config.set(server_sec, 'username', username) 
        config.set(server_sec, 'password', password) 
        # config.set(server_sec, 'tag', domain.split('.')[0] + server_no) 
        save_config()
        print('完成修改!')
    else: 
        print('输入有误!')

def remove_server():
    server_no_list = get_server_no_list()
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
        server_no_list = sorted(get_server_no_list())
        for i,server_no in enumerate(server_no_list):
            if server_no != str(i+1):
                new_server_sec = 'XUISERVER' + str(i+1)
                old_server_sec = 'XUISERVER' + server_no
                config.add_section(new_server_sec)
                domain, username, password = get_server_info(server_no)
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
        show_all_servers()
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
            show_all_servers()
        elif option_no == '1':
            new_no = gen_new_server_no()
            add_server(new_no)

        elif option_no == '2':
            edit_server_info()

        elif option_no == '3':
            remove_server()

        elif option_no == '4':
            sorting_servers()

        elif option_no == '9':
            exit()
        time.sleep(1)






if __name__ == '__main__':

    main()
