# # import configparser
# # import config_xuilist as cx

# # xui_srv_configfile ='/usr/local/x-ui/plugs/config/xuiplugconf.ini'


# # xui_srv_config = configparser.ConfigParser()
# # xui_srv_config.read(xui_srv_configfile)



# subscription_list =[

# ['00-00-allmonitor.TXT'                                        ],
# ['01-02-hydroxides.TXT', 'sega1', 'sega2', 'kinder1', 'kinder2'],
# ['03-03-eshareagen.TXT', 'sega3', 'sega4', 'kinder3', 'kinder4'],
# ['04-09-us-router.TXT', 'sega5', 'sega6', 'sega7', 'sega8', 'sega9', 'kinder5', 'kinder6', 'kinder7', 'kinder8', 'kinder9'],
# ['10-11-molecular.TXT', 'sega10', 'sega11', 'kinder10', 'kinder11'],
# ['12-13-patriotic.TXT', 'sega12', 'sega13', 'kinder12', 'kinder13'],
# ['14-15-equation.TXT', 'sega14', 'sega15', 'kinder14', 'kinder15'],
# ['16-17-kovalence.TXT', 'sega16', 'sega17', 'kinder16', 'kinder17'],
# ['18-18-kongdd.TXT', 'sega18'                                     ],
# ['19-20-crisis.TXT', 'sega19', 'sega20', 'kinder19', 'kinder20'],
# ['21-22-park66.TXT', 'sega18', 'sega21', 'sega22', 'sega23', 'sega24', 'kinder21', 'kinder22']
# ]

# inbounds ='sega1  sega2 sega3 '
# sublink =[]
# # temp_sublink =[]
# temp_inbounds = inbounds.strip().split(' ')
# temp_sublink = ['filename','use_yesno','remark']


# for inbound in temp_inbounds:
#     if ' ' not in inbound and inbound:
#         temp_sublink.append(inbound)
# sublink.append(temp_sublink)
# sublink.append(temp_sublink)

# print(sublink)

a = input()
if a == '1':
    print('1')
    exit()
elif a == '2':
    print('2')

print('f')