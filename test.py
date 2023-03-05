import configparser
import config_xuilist

xui_srv_configfile ='/usr/local/x-ui/plugs/config/xuiplugconf.ini'


xui_srv_config = configparser.ConfigParser()
xui_srv_config.read(xui_srv_configfile)


### make_sublinks   BEGIN--

def get_server_no_list():
    #生成 服务器序号 list, 文本
    section_list = xui_srv_config.sections()
    server_list = []
    for  sec in section_list:
        if 'XUISERVER' in sec:
            server_list.append(sec.replace('XUISERVER',''))
    return server_list

def get_server_info(server_no):
    server_sec = 'XUISERVER' + server_no
    if xui_srv_config.has_section(server_sec):
        domain = xui_srv_config.get(server_sec,'domain')
        username = xui_srv_config.get(server_sec,'username')
        password = xui_srv_config.get(server_sec,'password')
        return domain,username,password


def get_servers():
    servers = []
    server_sec_no_list = get_server_no_list()
    for server_no in server_sec_no_list:
        domain,username,password = get_server_info(server_no)
        server_sec = 'XUISERVER' + server_no
        domain = xui_srv_config.get(server_sec,'domain')
        username = xui_srv_config.get(server_sec,'username')
        password = xui_srv_config.get(server_sec,'password')
        servers.append([domain,username,password,domain.split('.')[0]])
    return servers

servers = get_servers()
print(servers)
### make_sublinks   END--