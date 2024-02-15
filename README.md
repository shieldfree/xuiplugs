# Funny X-UI plugs
##  快速使用


<details>
-  <summary><b> 点击查看快速使用说明</b></summary> 

 - 用一键安装命令进行安装
```
bash <(curl -Ls https://github.com/shieldfree/scriptforxui/raw/main/scriptforxui.sh)

```
运行界面如下

```
    0. 退出脚本 (Exit) 
 ——————————————————————————————————————————————————
    1. 搭建订阅服务器(Build subscription server)
    2. 删除订阅服务器(Delete subscription server)
    3. 安装端口++插件(Install port changer)
    4. 卸载端口++插件(Remove port changer)
    5. 安装客户端显示用量(Show Usage data)
    6. 卸载客户端显示用量(Remove Usage data)
    7. 订阅节点信息管理(Manage subscription links)
    8. 服务器信息管理(X-UI server manage)
    9. 批量添加节点(Add multiple inbounds)
    10. 其他参数设置(Other parameter setting)
 ——————————————————————————————————————————————————
  Please input a number [0-9]  

```

 1. 进入 <8. 服务器信息管理> 填写当前服务器的域名和订阅服务用的http端口。
 1. 进入 <8. 服务器信息管理> 菜单添加X-UI 所在的服务器信息，
输入服务器的域名，linux系统的用户名和密码(不是面板的)，以及服务器的名称(英文字母)， 安装在xui面板所在的服务器也需要输入, 
    - 输入的用户名 需要有权限能够访问 /etc目录下面板数据库
    - 如 xxxx.myserver.com   root   pass1234   candy
 1. 进入 <7.订阅节点信息管理> 菜单，添加订阅链接
    - 每个链接的 需要输入一个文件名(数字字母组合的10个字符以上)
    - inbound项目 是给当前订阅链接要添加的节点， 由xui服务器的名称+入站节点的ID组成， 
    - 假设 上面添加的命名为 candy的服务器有入站 1，2，3，4，5 ...
    - 就在inbound 填写  candy1  candy2 candy3 ...  中间空格区分
    - 该订阅链接就可以订阅这三个节点 
 1. 运行 <1. 搭建订阅服务器> 创建静态网站,运行完后屏幕显示订阅链接地址，如果看不到，
    - 订阅地址为 http://当前服务器域名:18080/sublinks/文件名，大概下面这个样子
    - http://xxxx.myserver.com:18080/sublinks/test98e9e8ijgf
    - http://xxxx.myserver.com:18080/sublinks/test3-kdiflvid
 1. 上面订阅地址如果需要转换成CLASH订阅链接
    - 安装docker命令， 下载2013tindy/subconverter镜像，生成容器以运行服务，命令如下：
    - docker run -d --restart=always -p 55555:25500 tindy2013/subconverter:latest
    - clash订阅地址为 https://xxxx.myserver.com:55555/sub?target=clash&url=<YOURSUBSCRIBELINK>
    - 如： https://xxxx.myserver.com:55555/sub?target=clash&url=http%3A%2F%2Fxxxx.myserver.com%3A18080%2Fsublinks%2Ftest3-kdiflvid
    - url 需要 URL Encoding 可以到这里转换☞：https://www.urlencoder.org/
    - 
 1. 目前Ubuntu机器上测试过可以运行。centos 还没试过
 
</details>  

## 菜单选项 
- [1. 搭建订阅服务器](#搭建订阅服务器)  
- [2. 删除订阅服务器](#删除订阅服务器)  


<details>
-  <summary><b> 点击查看使用说明</b></summary> 


##
## 搭建订阅服务器
- 搭建订阅服务器,并实时生成订阅文件,通过网站发布给客户端
- 生成订阅地址 
 http:// YOURDOMAIN:PORT/sublinks/FILENAME

 ###  - 待解决问题
 - 订阅节点的管理方案- 数据库?  
 - 网站服务 ssl 证书配置
 - 端口号改为随机生成

## 删除订阅服务器
- 关闭并删除订阅网站服务器

## 安装 定时自动更改端口插件
- 每天定时更改端口
- 超过流量更改端口
 ###  - 待解决问题
 - 更改规则设置菜单还没有(只能手动修改配置文件)

## 删除定时自动更改端口插件
- 删除插件

## 安装使用流量显示插件
- 定时读取用量信息,在备注栏显示

## 删除使用流量显示插件
- 删除插件

## 插件参数设置
- 没写完
## xui服务器列表管理
- 添加删除用于生成订阅链接的xui服务器
- 
## 批量添加节点
- 使用批量添加功能添加后需要在X-UI面板点击一次**流量重置** 否则添加的节点不能正常工作(水平有限..)

## 申请 SSL证书
- 没写完
## 密钥文件路径一键填写
- 没写完

- X-UI panel
  

  
  

  

  
</details>  

-   一键安装
 

```
bash <(curl -Ls https://github.com/shieldfree/scriptforxui/raw/main/scriptforxui.sh)
```    



#
## 订阅节点 
- 2022.11.15： ...







