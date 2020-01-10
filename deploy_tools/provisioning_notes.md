配置新网站
=========================

## 需要安装的包:
* nginx
* Python3
* virtualenv + pip
* Git

on Ubuntu:
    sudo apt-get install nginx

## 配置Nginx虚拟主机
* 参考nginx_template.conf
* 把SITENAME替换成所需的域名，例如toeflprepare.club

## 配置Systemd service
* 参考gunicorn-systemd.template.service
* 把SITENAME替换成所需的域名，例如toeflprepare.club

## 文件结构
假设用户目录为/home/ubuntu

```
/home/ubuntu/
└── sites
    └── www.toeflprepare.club
        ├── database
        ├── source
        ├── static
        └── virtualenv
```