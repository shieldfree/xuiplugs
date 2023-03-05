import config_xuilist
def main():
    while True:
        # show_all_servers()
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
            # time.sleep(1)
            continue
            print('test')
        elif option_no == '0':
            config_xuilist.main()
        elif option_no == '1':
            pass

        elif option_no == '9':
            exit()
        # time.sleep(1)

if __name__ == '__main__':
    main()