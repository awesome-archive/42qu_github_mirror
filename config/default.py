#!/usr/bin/env python
# -*- coding: utf-8 -*-
import _env
from hmako.lookup import TemplateLookup
import sys
from os.path import join
import yajl
import json
from mysql import DB_MAIN_TABLE, DB_GOOGLE_TABLE

json.dump = yajl.dump
json.dumps = yajl.dumps
json.loads = yajl.loads
json.load = yajl.load

def prepare(o):
    o.SITE_DOMAIN = '42qu.test'
    o.SITE_NAME = '42区'
    o.PORT = 6666

    o.MYSQL_HOST = '127.0.0.1'
    o.MYSQL_PORT = '3306'
    o.MYSQL_MAIN = 'zpage'
    o.MYSQL_USER = 'root'
    o.MYSQL_PASSWD = '42qu'

    o.MQ_PORT = 11300

    o.FILE_DOMAIN = 'p.%s'%o.SITE_DOMAIN
    o.FS_DOMAIN = 's.%s'%o.SITE_DOMAIN

    o.DEBUG = False

    o.DISABLE_LOCAL_CACHED = False
    o.MEMCACHED_ADDR = ('127.0.0.1:11211', )

    o.SMTP = 'smtp.163.com'
    o.SMTP_USERNAME = 'zpagedev'
    o.SMTP_PASSWORD = '42qu_com'
    o.SENDER_MAIL = 'zpagedev@163.com'

    o.LOGO_TEXT = '找到给你答案的人'

    o.ALIPAY_ID = ''
    o.ALIPAY_SALT = ''
    o.ALIPAY_EMAIL = ''

    o.TWITTER_CONSUMER_KEY = ''
    o.TWITTER_CONSUMER_SECRET = ''

    o.WWW163_CONSUMER_KEY = ''
    o.WWW163_CONSUMER_SECRET = ''

    o.SINA_CONSUMER_KEY = ''
    o.SINA_CONSUMER_SECRET = ''

    o.SOHU_CONSUMER_KEY = ''
    o.SOHU_CONSUMER_SECRET = ''

    o.QQ_CONSUMER_KEY = ''
    o.QQ_CONSUMER_SECRET = ''

    o.RENREN_CONSUMER_KEY = ''
    o.RENREN_CONSUMER_SECRET = ''

    o.GOOGLE_CONSUMER_REAL_SECRET = ''
    o.GOOGLE_CONSUMER_SECRET = ''

    o.DOUBAN_CONSUMER_KEY = ''
    o.DOUBAN_CONSUMER_SECRET = ''

    o.GOD_PORT = None
    o.RPC_PORT = None
    o.API_PORT = None

    o.SINA_FOLLOW = '1827906323'
    o.WWW163_FOLLOW = '6122584690'
    o.QQ_FOLLOW = 'cn42qu'

    return o


def debug(o):
    o.DEBUG = True


def finish(o):
    o.MQ_USE = o.MYSQL_MAIN

    o.FILE_PATH = '/mnt/zpage'
    o.SEARCH_DB_PATH = '/mnt/zpage_searchdb'


    if not o.GOD_PORT:
        o.GOD_PORT = o.PORT + 20

    if not o.API_PORT:
        o.API_PORT = o.PORT + 30

    if not o.RPC_PORT:
        o.RPC_PORT = o.PORT + 40


    o.FILE_URL = 'http://%s'%o.FILE_DOMAIN
    o.FS_URL = 'http://%s'%o.FS_DOMAIN

    o.SITE_DOMAIN_SUFFIX = '.%s' % o.SITE_DOMAIN
    o.SITE_URL = '//%s' % o.SITE_DOMAIN
    o.SITE_HTTP = 'http://%s' % o.SITE_DOMAIN

    o.API_URL = '//api.%s' % o.SITE_DOMAIN
    o.API_HTTP = 'http:%s' % o.API_URL
    o.RPC_URL = '//RPC.%s' % o.SITE_DOMAIN
    o.RPC_HTTP = 'http:%s' % o.RPC_URL

    o.SENDER_NAME = o.SITE_DOMAIN

    HTM_PATH = join(_env.PREFIX, 'htm')
    MAKOLOOKUP = TemplateLookup(
        directories=HTM_PATH,
        module_directory='/tmp/%s'%HTM_PATH.strip('/').replace('/', '.'),
        disable_unicode=True,
        encoding_errors='ignore',
        default_filters=['str', 'h'],
        filesystem_checks=o.DEBUG,
        input_encoding='utf-8',
        output_encoding=''
    )


    def render(htm, **kwds):
        mytemplate = MAKOLOOKUP.get_template(htm)
        return mytemplate.render(**kwds)
    o.render = render

    DB_HOST_MAIN = '%s:%s:%s:%s:%s' % (
        o.MYSQL_HOST, o.MYSQL_PORT, o.MYSQL_MAIN, o.MYSQL_USER, o.MYSQL_PASSWD
    )
    DB_HOST_GOOGLE = '%s:%s:%s:%s:%s' % (
        o.MYSQL_HOST, o.MYSQL_PORT, '%s_google'%o.MYSQL_MAIN, o.MYSQL_USER, o.MYSQL_PASSWD
    )


    o.DB_CONFIG = {
        'main': {
            'master': DB_HOST_MAIN,
            'tables': DB_MAIN_TABLE,
        },
        'google': {
            'master': DB_HOST_GOOGLE,
            'tables': DB_GOOGLE_TABLE,
        },
    }
    return o

def load(self, *args):
    PREPARE = [
        prepare
    ]
    FINISH = [
        finish
    ]

    def load(name):
        try:
            mod = __import__(
                name,
                globals(),
                locals(),
                [],
                -1
            )
        except ImportError:
            print 'NO CONFIG %s'%name
            return
        for i in name.split('.')[1:]:
            mod = getattr(mod, i)
        prepare = getattr(mod, 'prepare', None)

        if prepare:
            PREPARE.append(prepare)

        finish = getattr(mod, 'finish', None)
        if finish:
            FINISH.append(finish)
    for i in args:
        load(i)
    funclist = PREPARE+list(reversed(FINISH))
    for _ in funclist:
        _(self)

    return self
