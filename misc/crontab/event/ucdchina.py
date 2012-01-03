#!/usr/bin/env python # -*- coding: utf-8 -*-

import _env
import urllib2
from zkit.htm2txt import htm2txt
from urllib2 import urlopen
from zkit.bot_txt import txt_wrap_by_all, txt_wrap_by
import os.path as path
from zkit.spider import Rolling, Fetch, NoCacheFetch, GCrawler
from time import sleep
from os.path import exists
import os.path
from yajl import dumps
from hashlib import md5
import threading
from zkit.lock_file import LockFile

CURRNET_PATH = path.dirname(path.abspath(__file__))

class Writer(object):
    instance = None
    WRITTER_DICT = {}
    def __init__(self):
        pass

    def get_writer(self,name):
        if name not in Writer.WRITTER_DICT:
            Writer.WRITTER_DICT[name]=LockFile(path.join(CURRNET_PATH, name),'wa')
        return Writer.WRITTER_DICT[name]

    @staticmethod
    def get_instance():
        if not Writer.instance:
            Writer.instance = Writer()
        return Writer.instance
        

def name_builder(url):
    return os.path.join(CURRNET_PATH,"ucdchina", url)

def parse_page(filepath):
    with open(filepath) as f:
        page = f.read()

        title = txt_wrap_by('<title>', '- UCD大社区', page)
        author = txt_wrap_by('style=" float:left; color:#999;">', '</span', page)
        author = txt_wrap_by('作者：','|',author)
        content_wrapper = txt_wrap_by('<div id="pageContentWrap" style="font-size:13px; ">','</div',page)

        if content_wrapper:
            content = str(htm2txt(content_wrapper)[0])
        else:
            return 

        out = dumps([ title,  content, author ])

        writer = Writer.get_instance()
        writer = writer.get_writer('ucdchina.data')
        writer.write(out+'\n')

def save_page(page,url):
    filename = name_builder(url)
    with open(filename,'w') as f:
        f.write(page)
    parse_page(filename)

def parse_index(page, url):
    link_wrapper_list = txt_wrap_by_all('<div id="mainWrap">', '<!--/#mainWrap', page)
    link_list = []
    for link_wrapper in link_wrapper_list:
        url = txt_wrap_by('/snap/', '"', link_wrapper)
        print url
        filename = name_builder(url)
        if not exists(filename):
            yield save_page, 'http://ucdchina.com/snap/'+url
        else:
            parse_page(filename)

def yeeyan_url_builder():
    for page in xrange(68):
        yield parse_index, 'http://ucdchina.com/PM?p=%s'%str(page)
    for page in xrange(1256):
        yield parse_index, 'http://ucdchina.com/UCD?p=%s'%str(page)
    for page in xrange(393):
        yield parse_index, 'http://ucdchina.com/UR?p=%s'%str(page)
    for page in xrange(1374):
        yield parse_index, 'http://ucdchina.com/ia-id?p=%s'%str(page)
    for page in xrange(297):
        yield parse_index, 'http://ucdchina.com/VD?%p=%s'%str(page)
    for page in xrange(1133):
        yield parse_index, 'http://ucdchina.com/HappyDesign?p=%s'%str(page)

def main():
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1.7) Gecko/20091221 Firefox/3.5.7',
            'Accept': ' text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',
            'Accept-Language':'zh-cn,zh;q=0.5',
            'Accept-Charset':'gb18030,utf-8;q=0.7,*;q=0.7',
            'Content-type':'application/x-www-form-urlencoded'
    }

    fetcher = NoCacheFetch(0, headers=headers)
    spider = Rolling( fetcher, yeeyan_url_builder() )
    spider_runner = GCrawler(spider, workers_count=1)
    spider_runner.start()

if __name__ == '__main__':
    main()
