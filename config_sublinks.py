import configparser
import datetime
import time
import os
import main

sublink_configfile ='/usr/local/x-ui/plugs/config/subscription.ini'
# sublink_configfile = './config/subscription.ini' # 本机调试用
if not os.path.exists(sublink_configfile):
    print('设置文件丢失,请运行以下命令重新下载安装!')
    print("bash <(curl -Ls https://github.com/shieldfree/scriptforxui/raw/main/scriptforxui.sh)")
    exit()
sublink_config = configparser.ConfigParser()
sublink_config.read(sublink_configfile)

currenttime = datetime.datetime.now()
today_date =  currenttime.today().strftime('%Y-%m-%d')


def save_config():
    # save the configeration file
    with open(sublink_configfile, 'w') as file:
        sublink_config.write(file)

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

def print_sublink_info(sublink_no, filename,inbounds,remark,use_yesno):
    print(f'sublink{sublink_no:>2} | Filename: {filename:<25}| Use Y/N:{use_yesno} | remark:{remark:<16} |\n\t  | Inbounds:{inbounds:<63} |')
    print('-' * 85)

def get_sublink_info(sublink_no):
    sublink_sec = 'SUBSCRIPTION' + str(sublink_no)
    if sublink_config.has_section(sublink_sec):
        filename = sublink_config.get(sublink_sec,'filename')
        use_yesno = sublink_config.get(sublink_sec,'use_yesno')
        remark = sublink_config.get(sublink_sec,'remark')
        inbounds = sublink_config.get(sublink_sec,'inbounds')
        return [filename,use_yesno,remark,inbounds]
    # else:
    #     print(f'无server{sublink_no} 信息')
    #     return '','',''

def get_sublink_no_list():
    #生成 服务器序号 list, 文本
    section_list = sublink_config.sections()
    sublink_list = []
    for  sec in section_list:
        if 'SUBSCRIPTION' in sec:
            sublink_list.append(int(sec.replace('SUBSCRIPTION','')))
    return sublink_list

def get_subscription_list():
    sublink = []
    sublink_no_list = get_sublink_no_list()
    for sublink_no in sublink_no_list:
        filename,use_yesno,remark,inbounds = get_sublink_info(sublink_no)
        if use_yesno =='y':
            temp_sublink = [filename,use_yesno,remark]
            temp_inbounds = inbounds.strip().split(' ')
            for inbound in temp_inbounds:
                if ' ' not in inbound and inbound:
                    temp_sublink.append(inbound)
            sublink.append(temp_sublink)
    return sublink

def show_all_sublinks():
    sublink_no_list = get_sublink_no_list()
    print('\n\n\n当前订阅节点明细:\n')
    print('=' * 85)
    for sublink_no in sublink_no_list:
        temp_data = get_sublink_info(sublink_no)
        filename = temp_data[0]
        inbounds = temp_data[1]
        remark =temp_data[2]
        use_yesno = temp_data[3]
        # print(f'sublink{sublink_no:>2} | Filename: {filename:<20}| Use Y/N:{use_yesno} | remark:{remark:<16} |\n\t  | Inbounds:{inbounds:<60} |')
        print_sublink_info(sublink_no, filename,inbounds,remark,use_yesno)
        

def add_new_sublink(new_no):
    if int(new_no) > 30:
        print('订阅链接是不是太多了。。加不了!')
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
    print('要添加的订阅链接信息如下: \n')
    print('-' * 85)
    # print(f'sublink{new_no:>2} | filename: {filename:<20}| Use Y/N:{use_yesno} | remark:{remark:<16} |\n\t  |Inbounds:{inbounds:<60} |')
    print_sublink_info(new_no, filename,inbounds,remark,use_yesno)
    msg = '请确认是否添加节点 (Y/n)? :'
    yesno = input_yesno(msg)
    if yesno =='y' or yesno == '':
        sublink_sec = 'SUBSCRIPTION' + str(new_no)
        sublink_config.add_section(sublink_sec)
        sublink_config.set(sublink_sec, 'filename', filename)
        sublink_config.set(sublink_sec, 'inbounds', inbounds)
        sublink_config.set(sublink_sec, 'remark', remark)
        sublink_config.set(sublink_sec, 'use_yesno', use_yesno)
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
    sublink_no = int(input('选择要修改的的订阅链接序号:'))
    if sublink_no in sublink_no_list:
        server_sec = 'SUBSCRIPTION' + str(sublink_no)
        temp_data = get_sublink_info(sublink_no)
        filename = temp_data[0]
        inbounds = temp_data[1]
        remark =temp_data[2]
        use_yesno = temp_data[3]

        print(f'\n开始修改: | sublink{sublink_no:>2} | remark:{remark:<16}|\n')
        # print(f'sublink{sublink_no:>2} | Filename: {filename:<20}| Use Y/N:{use_yesno} | remark:{remark:<16} |\n\t  | Inbounds:{inbounds:<60} |')
        print_sublink_info(sublink_no, filename,inbounds,remark,use_yesno)
        print()

        print(f'\n当前文件名: {filename}')
        temp_filename =input('输入新的文件名(不修改直接回车):')
        if temp_filename.strip() != '':
            filename =temp_filename
            print(f'变更后的文件名: {filename}')

        print(f'\n当前remark: {remark}')
        temp_remark =input('变更remark(不修改直接回车):')
        if temp_remark != '':
            remark =temp_remark
            print(f'变更后的remark: {remark}')

        print(f'\n当前使用状态: {use_yesno}')
        msg = '使用状态y/n(不修改直接回车):'
        temp_use_yesno = input_yesno(msg)
        if temp_use_yesno != '':
            use_yesno =temp_use_yesno
            print(f'变更后的使用状态: {use_yesno}')

        print(f'\n当前inbounds 明细: {inbounds}')
        temp_inbounds =input('输入当前inbounds,空格分开(不修改直接回车):')
        if temp_inbounds != '':
            inbounds =temp_inbounds
            print(f'变更后的inbounds 明细:\n\t {inbounds}')

        sublink_config.set(server_sec, 'filename', filename) 
        sublink_config.set(server_sec, 'remark', remark) 
        sublink_config.set(server_sec, 'use_yesno', use_yesno) 
        sublink_config.set(server_sec, 'inbounds', inbounds) 
        # config.set(server_sec, 'tag', domain.split('.')[0] + server_no) 
        save_config()
        print('完成修改!')
    else: 
        print('输入有误!')

def remove_sublinks():
    sublink_no_list = get_sublink_no_list()
    show_all_sublinks()
    sublink_no = int(input('\n请输入要删除的订阅链接序号 :'))
    if sublink_no in sublink_no_list:
        filename,inbounds,remark,use_yesno = get_sublink_info(sublink_no)
        sublink_sec = 'SUBSCRIPTION' + str(sublink_no)
        filename = sublink_config.get(sublink_sec,'filename')
        inbounds = sublink_config.get(sublink_sec,'inbounds')
        remark = sublink_config.get(sublink_sec,'remark')
        use_yesno = sublink_config.get(sublink_sec,'use_yesno')
        # print(f'sublink{sublink_no:>2} | Filename: {filename:<20}| Use Y/N:{use_yesno} | remark:{remark:<16} |\n\t  | Inbounds:{inbounds:<60} |')
        print('\n'+ '=' * 85)
        print_sublink_info(sublink_no, filename,inbounds,remark,use_yesno)
        msg = f'请确认是否删除 {sublink_no}号 订阅链接(y/N)'

        yesno = input_yesno(msg)
        if yesno =='y':
            server_sec = 'SUBSCRIPTION' + str(sublink_no)
            sublink_config.remove_section(server_sec)
            save_config()
            sorting_sublinks()
            # show_all_servers
        else:
            print('取消删除')
            # show_all_servers
    else:

        print('序号输入错误！')
        time.sleep(1)
        show_all_sublinks()


def sorting_sublinks():
    # 每次有删减,重新 从1号开始排序
    # msg = '确认是否进行排序(y/N)'
    # yesno = input_yesno(msg)
    # if yesno == 'y':
        sublink_no_list = sorted(get_sublink_no_list())
        for i,sublink_no in enumerate(sublink_no_list):
            # if sublink_no != str(i+1):
            new_sublink_sec = 'SUBSCRIPTION' + str(i)
            old_sublink_sec = 'SUBSCRIPTION' + str(sublink_no)
            filename,inbounds,remark,use_yesno = get_sublink_info(sublink_no)
            
            sublink_config.remove_section(old_sublink_sec)

            sublink_config.add_section(new_sublink_sec)
            sublink_config.set(new_sublink_sec, 'filename', filename) 
            sublink_config.set(new_sublink_sec, 'inbounds', inbounds) 
            sublink_config.set(new_sublink_sec, 'remark', remark) 
            sublink_config.set(new_sublink_sec, 'use_yesno', use_yesno) 
                # save_config()
            # elif server_no == str(i+1):
            #     domain, username, password = get_sublink_info(server_no)
            #     server_sec = 'SUBSCRIPTION' + server_no
            #     config.remove_section(server_sec)
            #     config.add_section(server_sec)
            #     config.set(server_sec, 'domain', domain)
            #     config.set(server_sec, 'username', username)
            #     config.set(server_sec, 'password', password)
        save_config()
        print(' \n\n注意:订阅链接 序号重新排序 !!')
        time.sleep(2)
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


def sublink_mng_menu():
    while True:
        show_all_sublinks()
        menu = '''
            ===X-UI订阅链接管理===
            1. 添加(Add)
            2. 修改(Edit)
            3. 删除(Delete)
            ===============
            9. 返回(Exit)
        
        '''
        print(menu)


        msg = '请输入操作菜单序号:'
        option_no = input(msg)
        
        if option_no not in [ '1','2', '3','9']:
            print('输入有误请重新输入!! ')
            time.sleep(1)
            continue

        # elif option_no == '0':
        #     # show_all_sublinks()
        #     main.main_menu()
        elif option_no == '1':
            new_no = gen_new_sublink_no()
            add_new_sublink(new_no)

        elif option_no == '2':
            edit_sublink_info()

        elif option_no == '3':
            remove_sublinks()

        # elif option_no == '4':
        #     sorting_sublinks()

        elif option_no == '9':
            exit()
        time.sleep(1)






if __name__ == '__main__':

    sublink_mng_menu()
    # filename,inbounds,remark,use_yesno = get_sublink_info(1)
    # inbound_temp = inbounds.split(' ')
    # print(inbound_temp)
    
    # sublink_no_list = get_sublink_no_list()
    # print(sublink_no_list)
    # show_all_sublinks()

    # new_no = gen_new_sublink_no()
    # add_new_sublink(new_no)
    
    # edit_sublink_info()
    # msg = '输入使用状态y/n(不修改直接回车):'
    # temp_use_yesno = input_yesno(msg)