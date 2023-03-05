import configparser
import datetime
import time
import os
import main
import re

xui_srv_configfile ='/usr/local/x-ui/plugs/config/xuiplugconf.ini'
if not os.path.exists(xui_srv_configfile):
    print('设置文件丢失,请运行以下命令重新下载安装!')
    print("bash <(curl -Ls https://github.com/shieldfree/scriptforxui/raw/main/scriptforxui.sh)")
    exit()
xui_srv_config = configparser.ConfigParser()
xui_srv_config.read(xui_srv_configfile)

currenttime = datetime.datetime.now()
today_date =  currenttime.today().strftime('%Y-%m-%d')

def load_config(xui_srv_configfile):
    xui_srv_config.read(xui_srv_configfile)

def save_config():
    # save the configeration file
    with open(xui_srv_configfile, 'w') as file:
        xui_srv_config.write(file)
    # load_config(xui_srv_configfile)

def gen_new_server_no():
    server_list= get_server_no_list()
    
    new_no = len(server_list) + 1
    # if len(server_list) >0:
    #     for i in server_list:
    #         if int(i) > int(new_no):
    #             new_no =i
    #     new_no = str(int(new_no) + 1)
    # # print(new_no)
    return new_no

def input_info(msg):
    temp = ''
    while not temp:
        temp = input(msg)
        if len(temp) == 0:
            # temp = ''
            print('请重新输入!! ')
    return temp


def contain_non_alpha_chars(string):
    if not string.isalpha():
        pattern = re.compile('[!a-zA-Z]')
        if pattern.search(string):
            return True
    return False

def input_tag(msg):
    temp = ''
    while not temp:
        temp = input(msg)
        if len(temp.strip()) == 0 :
            temp = ''
            print('错误请重新输入!! ')
        elif   len(temp.strip()) > 8:
            temp =''
            print('请重新输入!! ')
        elif ' ' in temp:
            print('不能包含空格')
        elif contain_non_alpha_chars(temp):
            temp = ''
            print('tag只能包含英文字母')
            continue
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
    server_sec = 'XUISERVER' + str(server_no)
    if xui_srv_config.has_section(server_sec):
        domain = xui_srv_config.get(server_sec,'domain')
        username = xui_srv_config.get(server_sec,'username')
        password = xui_srv_config.get(server_sec,'password')
        tag = xui_srv_config.get(server_sec,'tag')
        return domain,username,password,tag
    # else:
    #     print(f'无server{server_no} 信息')
    #     return '','',''

def get_server_no_list():
    #生成 服务器序号 list, 文本
    section_list = xui_srv_config.sections()
    server_list = []
    for  sec in section_list:
        if 'XUISERVER' in sec:
            server_list.append(int(sec.replace('XUISERVER','')))
    return server_list

def get_servers():
    servers = []
    server_sec_no_list = get_server_no_list()
    for server_no in server_sec_no_list:
        domain,username,password,tag = get_server_info(server_no)
        servers.append([domain,username,password,tag])
    return servers

def show_all_servers():
    server_list = get_server_no_list()
    print('\n\n\n当前服务器信息如下:\n')
    print('=' * 80)
    for server_no in server_list:
        domain,username,password,tag = get_server_info(server_no)
        print(f'Server{server_no:>1}|  Tag:{tag:<8}\n | domain: {domain:<20}|\n| User:{username:<6}| Pw:{password:<10}')
        print('-' * 80)

def add_server(new_no):
    if new_no > 9:
        print('服务器太多了。。加不了!')
        return
    msg = '请确认是否开始添加新的X-UI服务器用于生成订阅链接 (Y/n)? :'
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

    msg = '请输入服务器名称:'
    print('--服务器标签是为区分,不能重复,建议英文字符2-8个!--')
    tag = input_tag(msg)

    print('要添加的服务器信息如下: ')
    print(f'''
        域名：  {domain}
        用户名：{username}
        密码：  {password}
        标签：  {tag}
    ''')
    msg = '请确认是否添加 (Y/n)? :'
    yesno = input_yesno(msg)
    if yesno =='y' or yesno == '':
        server_sec = 'XUISERVER' + str(new_no)
        xui_srv_config.add_section(server_sec)
        xui_srv_config.set(server_sec, 'domain', domain)
        xui_srv_config.set(server_sec, 'username', username)
        xui_srv_config.set(server_sec, 'password', password)
        xui_srv_config.set(server_sec, 'tag', tag)
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
    if server_no == '' or not server_no.isnumeric():
        return
    if int(server_no) in server_no_list:
        server_sec = 'XUISERVER' + server_no
        domain, username, password,tag = get_server_info(server_no)
        print(f'\n当前域名: {domain}')
        temp_domain =input('输入新的域名(不修改直接回车):')
        if temp_domain != '':
            domain =temp_domain
            print(f'变更后的域名: {domain}')

        print(f'\n当前用户名: {username}')
        temp_username =input('输入新的用户名(不修改直接回车):')
        if temp_username != '':
            username =temp_username
            print(f'变更后的用户名: {username}')

        print(f'\n当前密码: {password}')
        temp_password =input('输入新的密码(不修改直接回车):')
        if temp_password != '':
            password =temp_password
            print(f'变更后的密码: {password}')

        print(f'\n当前Tag: {tag}')
        print('--服务器名称是为便于管理,不能重复,英文字符2-8个!--')
        temp_tag =input('输入新的服务器名称:')
        if temp_tag != '':
            tag = temp_tag
            # tag = input_tag(msg)
            print(f'变更后的Tag: {tag}')

        xui_srv_config.set(server_sec, 'domain', domain) 
        xui_srv_config.set(server_sec, 'username', username) 
        xui_srv_config.set(server_sec, 'password', password) 
        xui_srv_config.set(server_sec, 'tag', tag) 
        # config.set(server_sec, 'tag', domain.split('.')[0] + server_no) 
        save_config()
        print('\n完成修改!')
    else: 
        print('输入有误!')

def remove_server():
    server_no_list = get_server_no_list()
    show_all_servers()
    server_no = input('请输入要删除的服务器序号 :')
    if server_no == '' or not server_no.isnumeric():
        return
    if int(server_no) in server_no_list:
        msg = f'请确认是否删除 {server_no}号 服务器(y/N)'
        yesno = input_yesno(msg)
        if yesno =='y':
            server_sec = 'XUISERVER' + server_no    #输入的 server_no 是int类型
            xui_srv_config.remove_section(server_sec)
            save_config()
            sorting_servers()
            # show_all_servers
        else:
            print('取消删除')
            # show_all_servers
    else:

        print('序号输入错误！')
        time.sleep(0.5)
        show_all_servers()


def sorting_servers():
    # 每次有删减,重新 从1号开始排序
    # msg = '确认是否进行排序(y/N)'
    # yesno = input_yesno(msg)
    # if yesno == 'y':
        server_no_list = sorted(get_server_no_list())
        for i,server_no in enumerate(server_no_list):
            # if server_no != str(i+1):
            new_server_sec = 'XUISERVER' + str(i+1)     #从1 开始排序
            old_server_sec = 'XUISERVER' + str(server_no)
            domain, username, password,tag = get_server_info(server_no)
            xui_srv_config.remove_section(old_server_sec)

            xui_srv_config.add_section(new_server_sec)
            xui_srv_config.set(new_server_sec, 'domain', domain) 
            xui_srv_config.set(new_server_sec, 'username', username) 
            xui_srv_config.set(new_server_sec, 'password', password) 
            xui_srv_config.set(new_server_sec, 'tag', tag) 
                # save_config()
            # elif server_no == str(i+1):
            #     domain, username, password = get_server_info(server_no)
            #     server_sec = 'XUISERVER' + server_no
            #     xui_srv_config.remove_section(server_sec)
            #     xui_srv_config.add_section(server_sec)
            #     xui_srv_config.set(server_sec, 'domain', domain)
            #     xui_srv_config.set(server_sec, 'username', username)
            #     xui_srv_config.set(server_sec, 'password', password)
            #     xui_srv_config.set(server_sec, 'tag', tag)
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
        ===订阅服务器==
        4. 域名
        5. 端口

    '''

    # while  True :
        # show_all_servers()
        # print(menu)
    option_no = input(msg)

    return option_no

def sub_server_mng():
    sub_srv_domain = xui_srv_config.get('SUBSCRIPTIONSERVER','subserver_domain')
    serverport = xui_srv_config.get('SUBSCRIPTIONSERVER','serverport')
    print(f'当前服务器域名为: {sub_srv_domain}, 端口为: {serverport}')

    print(f'\n变更域名: {sub_srv_domain}')
    temp_sub_srv_domain =input('输入新的域名(不修改直接回车):')
    if temp_sub_srv_domain != '':
        sub_srv_domain =temp_sub_srv_domain
        print(f'\n变更后的域名: {sub_srv_domain}')

    print(f'\n变更端口: {serverport}')
    temp_serverport =input('输入新的域名(不修改直接回车):')
    if temp_serverport != '':
        serverport =temp_serverport 
        print(f'\n变更后的端口: {serverport}')

    xui_srv_config.set('SUBSCRIPTIONSERVER','subserver_domain', sub_srv_domain)
    xui_srv_config.set('SUBSCRIPTIONSERVER','serverport',serverport)
    print('\n 保存完毕！ 变更后的信息：')
    print(f'\n当前服务器域名为: {sub_srv_domain}, 端口为: {serverport}')
    save_config()


def server_mng_menu():
    while True:
        show_all_servers()
        menu = '''
            ===X-UI服务器===
            1. 添加(Add)
            2. 修改(Edit)
            3. 删除(Delete)

            ===订阅服务器==

            4. 域名设置(domain)
            ===============
            9. 返回(Exit)
        
        '''
        print(menu)


        msg = '请输入操作菜单序号:'
        option_no = input(msg)
        if option_no == '' or not option_no.isnumeric():
            continue
        if option_no not in [ '1','2', '3', '4', '9']:
            print('\n输入有误请重新输入!! ')
            time.sleep(1)
            continue

        # elif option_no == '0':
        #     # show_all_servers()
        #     main.main_menu()
        elif option_no == '1':
            new_no = gen_new_server_no()
            add_server(new_no)

        elif option_no == '2':
            edit_server_info()

        elif option_no == '3':
            remove_server()

        elif option_no == '4':
            sub_server_mng()

        elif option_no == '9':
            exit()
        # time.sleep(1)






if __name__ == '__main__':

    server_mng_menu()
