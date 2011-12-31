import _env
import urllib2
from urllib2 import urlopen
from model._db import Model, McModel, McCache, McCacheA, McLimitA, McNum
from model.po import po_new, STATE_RM
from model.po_event import po_event_pic_new , EVENT_CID, po_event_feedback_new
from model.event import Event, event_init2to_review
from model.state import STATE_RM, STATE_SECRET, STATE_ACTIVE
from model.cid import CID_EVENT, CID_EVENT_FEEDBACK, CID_NOTICE_EVENT_JOINER_FEEDBACK, CID_NOTICE_EVENT_ORGANIZER_SUMMARY
from model.event import Event, EVENT_STATE_INIT, EVENT_STATE_REJECT, EVENT_STATE_TO_REVIEW, EVENT_STATE_NOW, EVENT_JOIN_STATE_END, EVENT_JOIN_STATE_YES, EVENT_JOIN_STATE_FEEDBACK_GOOD, EVENT_JOIN_STATE_FEEDBACK_NORMAL, event_new_if_can_change, EventJoiner, event_joiner_user_id_list, event_joiner_get, event_joiner_state, last_event_by_zsite_id, event_new
from model.po_event import po_event_pic_new , EVENT_CID, po_event_feedback_new
from model.days import today_ymd_int, ymd2minute, minute2ymd, ONE_DAY_MINUTE
from urllib import urlencode
from zkit.pic import picopen
from json import loads
from zkit.bot_txt import txt_wrap_by_all, txt_wrap_by
import os.path as path
from xml.sax.saxutils import unescape
from zkit.htm2txt import htm2txt
from zkit.spider import Rolling, Fetch, NoCacheFetch, GCrawler
from time import sleep
from os.path import exists
import os.path
from zkit.earth import PID2NAME
import re
from yajl import dumps
from hashlib import md5
from model.days import time_by_string, datetime_to_minutes
import threading

def name_builder(url):
    return os.path.join(CURRNET_PATH,"yeeyan", md5(url).hexdigest())

def dongxi_url_builder():
    for i in xrange(1,695):
        yield parse_index,'http://dongxi.net/index/original?type=channel&slug=all&cate=havetrans&page=%s'%str(i)

def parse_index(page,url):
    link_wrap_list = txt_wrap_by_all('<p class="status_name">','">',page)
    link_list = []
    for link_wrap in link_wrap_list:
        url = txt_wrap_by(' <a target="_blank" href="','">',link_wrap)
        yield parse_page,'http://dongxi.net%s'%url

def parse_page(page,url):
    title = txt_wrap_by('<div class="content_title clearfix">','</h1>',page).strip().split('>')[-1]
    author = txt_wrap_by('<a class="link_text_blue" href="','</a>',page).strip().split('>')[-1]

    tags = map(lambda x:x.split('>')[-1],txt_wrap_by_all("<a  class='link_text_blue'",'</a>',page))
    rating_num = txt_wrap_by('onclick="favorate(',')',page)
    yield parse_rat,'http://dongxi.net/content/widget/page_id/%s'%rating_num,title,author,tags, url

def page_rat(page,url,title,author,tags, po_url):
    dic = json.loads(page)
    rating = dic['fav_count']
    with open(name_builder(url),'w') as f:
        f.write(dumps([ title, author, tags, rating, po_url ]))

def main():
    headers = {
    }

    fetcher = NoCacheFetch(0, headers=headers)
    spider = Rolling(fetcher,dongxi_url_builder())
    spider_runner = GCrawler(spider, workers_count=100)
    spider_runner.start()

if __name__ == '__main__':
    main()