# coding:utf-8
from __future__ import unicode_literals, absolute_import
import os
import socket
import platform
from fabric.api import lcd, local, task

LOCAL_APP_DIR = os.getcwd()
PROJECT_NAME = 'api.tutorial'
SITE_DOMAIN = '{0}{1}'.format(PROJECT_NAME, '.br')
LOCAL_CONFIG_DIR = os.path.join(LOCAL_APP_DIR, 'conf')
LOCAL_ENV_HOST = [(s.connect(('google.com', 80)), s.getsockname()[0],
                   s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
LOCAL_HOST = 'localhost'
LOCAL_MACHINE_NAME = platform.node()

# NGINX
SITES_ENABLED_DIR = os.path.join('/', 'etc', 'nginx', 'sites-enabled')


@task(alias='cnc')
def create_nginx_config():
    """ Cria o arquivo de configuração do nginx """
    if not os.path.exists(os.path.join(LOCAL_CONFIG_DIR)):
        local('mkdir ' + os.path.join(LOCAL_CONFIG_DIR))

    file_list = [
        'server {',
        '    listen 80;',
        '    server_name {};'.format(SITE_DOMAIN),
        '    location / {',
        '        proxy_pass http://127.0.0.1:8000;',
        '        proxy_set_header Host $host;',
        '        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;',
        '    }',
        '    location /static/ {',
        '        autoindex on;',
        '        alias "{}/static/";'.format(LOCAL_APP_DIR),
        '    }',
        '}'
    ]
    with lcd(LOCAL_CONFIG_DIR):
        if os.path.exists(os.path.join(LOCAL_CONFIG_DIR, PROJECT_NAME + '-local')):
            local('rm {}'.format(os.path.join(LOCAL_CONFIG_DIR, PROJECT_NAME + '-local')))
            local('touch {}'.format(PROJECT_NAME + '-local'))

    with open(os.path.join(LOCAL_CONFIG_DIR, PROJECT_NAME + '-local'), 'w') as f:
        for i in file_list:
            f.write(i + '\n')


@task(alias='cnl')
def configure_nginx_local():
    """ Configura o nginx local. Obs.: Executar com sudo (sudo fab cnl) """
    create_nginx_config()

    with lcd(SITES_ENABLED_DIR):
        if os.path.exists(os.path.join(SITES_ENABLED_DIR, 'default')):
            local('rm ' + os.path.join(SITES_ENABLED_DIR, 'default'))

    if not os.path.exists(os.path.join(SITES_ENABLED_DIR, PROJECT_NAME + '-local')):
        local('sudo ln -s {0} {1}'
              .format(os.path.join(LOCAL_CONFIG_DIR, PROJECT_NAME + '-local'),
                      os.path.join(SITES_ENABLED_DIR, PROJECT_NAME + '-local')))

    with open(os.path.join('/', 'etc', 'hosts'), 'w') as f:
        file_list = [
            '# The following lines are desirable for IPv6 capable hosts',
            '::1 ip6-localhost ip6-loopback',
            'fe00::0 ip6-localnet',
            'ff00::0 ip6-mcastprefix',
            'ff02::1 ip6-allnodes',
            'ff02::2 ip6-allrouters',
            '# Hosts',
            '{:40}{}'.format('127.0.0.1', LOCAL_HOST),
            '{:40}{}'.format('127.0.1.1', LOCAL_MACHINE_NAME)
        ]
        for i in file_list:
            f.write(i + '\n')

        f.write('{:40}{}'.format(LOCAL_ENV_HOST, SITE_DOMAIN))

    local('sudo service nginx restart')
