import config_xuilist
import config_sublinks
def main_menu():
    while True:
        # show_all_servers()
        menu = '''
            ===X-UI面板插件管理===
            1. X-UI 服务器管理
            2. 订阅节点管理
            3. 
            4. ---


            ===============
            9. 退出
        
        '''
        print(menu)


        msg = '请输入操作菜单序号:'
        option_no = input(msg)
        
        if option_no not in ['0', '1','2', '3', '4','9']:
            print('输入有误请重新输入!! ')
            # time.sleep(1)
            continue
            print('test')
        elif option_no == '1':
            config_xuilist.server_mng_menu()
        elif option_no == '2':
            config_sublinks.sublink_mng_menu()
            pass

        elif option_no == '9':
            exit()
        # time.sleep(1)

if __name__ == '__main__':
    main_menu()