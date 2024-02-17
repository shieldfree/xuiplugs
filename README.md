# Funny X-UI plugs
##  快速使用


<details>
-  <summary><b> 点击查看快速使用说明</b></summary> 

 - 用一键安装命令进行安装
```
bash <(curl -Ls https://github.com/shieldfree/xuiplugs/raw/main/installxuiplugs.sh)

```
运行界面如下

```
    0. 退出脚本 (Exit) 
 —————————————————————————————————————————————————————————————————
     1. 搭建/删除订阅服务器(Build/Remove Subscription Server)
     2. 启用/删除定时切换节点端口(Enable/Disable Inbound Port Changer)
     3. 启用/删除客户端用量显示(Enable/Disable Client Usage Display)
     4. 订阅/X-UI服务器管理(Subscription/X-UI Server Management)
     5. 订阅链接管理(Manage Subscription Links)
     6. 批量添加节点(Create Multiple Inbounds)
     7. 安装NPM代理服务器(Install NginX Proxy Manager)
     8. 创建订阅转换服务器（Build Subconverter Server)
     9. inbound_config文件编辑
    10. X-UI服务器信息编辑
 —————————————————————————————————————————————————————————————————

  Please input a number [0-9]  

```

 1. 进入 <4. 订阅/X-UI服务器管理> 填写当前服务器的域名和订阅服务用的http端口。
 1. 进入 <4. 订阅/X-UI服务器管理> 添加X-UI 所在的服务器信息，
输入服务器的域名，linux系统的用户名和密码(不是面板的)，以及服务器的名称(英文字母)， 安装在xui面板所在的服务器也需要输入, 
    - 输入的用户名 需要有权限能够访问 /etc目录下面板数据库
    - 如 xxxx.myserver.com   root   pass1234   candy
 1. 进入 <5.订阅节点信息管理> 菜单，添加订阅链接
    - 每个订阅链接的 需要输入一个文件名(数字字母组合的10个字符以上)
    - inbound项目 是给当前订阅链接要添加的节点， **由xui服务器的名称+入站节点的ID组成**， 
    - 假设 订阅链接**test98e9e8ijgf.txt**添加的服务器标签为 **candy**的服务器有入站(inbound) 1，2，3，4，5 ...
    - 就在给这个订阅链接的inbound 填写 ** candy1  candy2 candy3 ** 中间空格区分
    - 该订阅链接就可以订阅这三个节点 
 1. 运行 <1. 搭建订阅服务器> 创建静态网站,运行完后屏幕显示订阅链接地址
    - 订阅地址为 http://当前服务器域名:18080/sublinks/文件名，大概下面这个样子
    - http://xxxx.myserver.com:18080/sublinks/test98e9e8ijgf.txt
    - http://xxxx.myserver.com:18080/sublinks/test3-kdiflvid
 1. 上面订阅地址如果需要转换成CLASH订阅链接
    - 需要转换成clash 订阅链接,就用菜单**<8. 创建订阅转换服务器>**
    - 创建的时候需要指定一个本机端口用于给clash链接访问
    - clash订阅地址为 https://xxxx.myserver.com:55555/sub?target=clash&url=**<你的ss订阅网址>**
    - **<你的ss订阅网址>** 需要用URL Encoding转换特殊 可以到这里转换☞：https://www.urlencoder.org/
    - 最终clash订阅的链接样子应该如下：
    - https://xxxx.myserver.com:55555/sub?target=clash&url=http%3A%2F%2Fxxxx.myserver.com%3A18080%2Fsublinks%2Ftest3-kdiflvid
    - 
 1. 目前Ubuntu机器上测试过可以运行。centos 还没试过
 
</details>  


## 菜单选项 
- [1. 搭建订阅服务器](#搭建订阅服务器)  
- [2. 删除订阅服务器](#删除订阅服务器)
- 
<details>
-  <summary><b> 点击查看使用说明</b></summary> 



##
## 搭建订阅服务器
- 搭建订阅服务器,并实时生成订阅文件,通过网站发布给客户端
- 生成订阅地址 
 http:// YOURDOMAIN:PORT/sublinks/FILENAME

 ###  - 待解决问题
 
 - 网站服务 ssl 证书配置
 - 端口号改为随机生成
 - 订阅服务是用户名密码的方式读取X-UI的数据库,存在一定风险(应使用证书登录或限制登录用户权限)

## 删除订阅服务器
- 关闭并删除订阅网站服务器

## 运行 端口++插件
- 每天定时更改端口
- 超过流量更改端口

 ###  - 待解决问题
 - 更改规则设置菜单还没有(只能手动修改配置文件)

## 停止 端口++插件
- 停止运行

## 安装使用流量显示
- 定时读取用量信息,在备注栏显示

## 删除使用流量显示
- 删除插件

## 订阅节点信息管理
- 没写完


## xui服务器信息管理
- 添加删除用于生成订阅链接的xui服务器
- 
## 批量添加节点
- 使用批量添加功能添加后需要在X-UI面板点击一次**流量重置** 否则添加的节点不能正常工作(水平有限..)

## 其他参数设置
- 手动编辑config设置文件


## 申请 SSL证书
- 没写完
## 密钥文件路径一键填写
- 没写完

- X-UI panel
  

  
  

  

  
</details>  

-   一键安装
 

```
bash <(curl -Ls https://github.com/shieldfree/xuiplugs/raw/main/installxuiplugs.sh)
```    



#
## 订阅节点 
- 2022.11.15： ...







