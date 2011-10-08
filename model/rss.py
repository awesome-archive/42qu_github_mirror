#!/usr/bin/env python
# -*- coding: utf-8 -*-
from _db import Model, McModel
from zkit.google.greader import Reader
import json
import sys
from zkit.htm2txt import htm2txt, unescape
from config import GREADER_USERNAME, GREADER_PASSWORD
import traceback
from model.mail import rendermail
from model.user_mail import mail_by_user_id
from model.zsite import Zsite


RSS_UNCHECK = 0
RSS_RM = 1
RSS_PRE_PO = 2
RSS_RT_PO = 3
RSS_POED = 4

STATE_RSS_NEW = 5
STATE_RSS_EMAILD = 6
STATE_RSS_REJECT = 7
STATE_RSS_OK = 8

STATE2CN = {
        STATE_RSS_OK:'通过',
        STATE_RSS_NEW:'新建',
        STATE_RSS_EMAILD:'已经联系',
        STATE_RSS_REJECT:'已经被拒绝'
        }

class Rss(McModel):
    pass

class RssPo(McModel):
    pass

class RssPoId(McModel):
    pass

class RssUpdate(McModel):
    pass

def rss_po_id(rss_po_id, po_id):
    RssPoId.raw_sql('insert into rss_po_id (id, po_id, state) values (%s, %s, 0)', rss_po_id, po_id)

def rss_po_total(state):
    return RssPo.where(state=state).count()

def rss_new(user_id, url, name=None, link=None, gid=0, auto=0):
    rss = Rss.get_or_create(url=url)
    rss.user_id = user_id
    rss.gid = gid
    if name:
        rss.name = name
    if link:
        rss.link = link
    rss.auto = int(bool(auto))
    rss.save()
    return rss

def rss_update_new(id, state):
    rss = RssUpdate.get_or_create(id=id)
    rss.state = state
    rss.save()
    return rss


def rss_total_gid(gid):
    return Rss.where(gid=gid).count()

def get_rss_by_gid(gid, limit=1, offset=10):
    rss = Rss.raw_sql('select id,user_id,url,gid,name,link from rss where gid = %s order by id desc limit %s offset %s', gid, limit, offset).fetchall()
    return rss

def rss_po_list_by_state(state, limit=1, offset=10):
    p = RssPo.raw_sql('select id,link,user_id,title,txt,pic_list,rss_id from rss_po where state = %s order by id desc limit %s offset %s', state, limit, offset).fetchall()
    return p


def unread_update(greader=None):
    if greader is None:
        greader = Reader(GREADER_USERNAME, GREADER_PASSWORD)

    feeds = greader.unread_feed()

    for feed in feeds:
        try:
            unread_feed_update(greader, feed)
        except:
            traceback.print_exc()
            continue

    greader.mark_as_read()

def unread_feed_update(greader, feed):
    rs = Rss.raw_sql('select id,user_id from rss where url = %s', feed[5:]).fetchone()
    if rs:
        id, user_id = rs

        res = greader.unread(feed)
        rss_feed_update(res, id , user_id)


def rss_feed_update(res, id, user_id, limit=None):
    from zkit.rss.txttidy import txttidy
    from tidylib import  tidy_fragment


    rss = Rss.mc_get(id)
    for count , i in enumerate(res):
        if limit:
            if count > limit:
                break

        link = i['alternate'][0]['href']
        title = i['title']
        rss_uid = i.get('id') or 1
        snippet = i.get('summary') or i.get('content') or None

        if snippet:
            htm = snippet['content']

            if htm:
                htm = txttidy(htm)
                htm = tidy_fragment(htm,{"indent": 0})[0]

                txt, pic_list = htm2txt(htm)

                pic_list = json.dumps(pic_list)
                if txt:
                    title = unescape(title)
                    if rss.auto:
                        state = RSS_PRE_PO
                    else:
                        state = RSS_UNCHECK
                    RssPo.raw_sql(
'insert into rss_po (user_id,rss_id,rss_uid,title,txt,link,pic_list,state) values (%s,%s,%s,%s,%s,%s,%s,%s) on duplicate key update title=%s , txt=%s , pic_list=%s',
user_id, id, rss_uid, title, txt, link, pic_list, state, title, txt, pic_list
                    )


def mail_by_rss_id(rss_id):
    rss = Rss.mc_get(rss_id)
    rendermail('/mail/notice/invite_blog.txt',
        mail_by_user_id(rss.user_id),
        Zsite.mc_get(rss.user_id).name
        )
    ru = RssUpdate.mc_get(rss_id)
    if ru:
        ru.state = STATE_RSS_EMAILD
        ru.save()
    else:
        rss_update_new(rss_id,STATE_RSS_EMAILD)




def rss_subscribe(greader=None):
    from zkit.google.findrss import get_rss_link_title_by_url

    rss_list = []

    for i in Rss.where(gid=0):

        url = i.url.strip()

        if not all((i.link, i.url, i.name)):
            rss, link, name = get_rss_link_title_by_url(url)

            if rss:
                i.url = rss

            if link:
                i.link = link

                if not name:
                    name = link.split('://', 1)[-1]

            if name:
                i.name = name

            i.save()

        rss_list.append(i)

    if rss_list:
        if greader is None:
            greader = Reader(GREADER_USERNAME, GREADER_PASSWORD)

        for i in rss_list:
            greader.subscribe(i.url)
            i.gid = 1
            i.save()
            #print i.url
            feed = 'feed/%s'%i.url
            rss_feed_update(greader.feed(feed), i.id, i.user_id, 512)
            greader.mark_as_read(feed)


    for i in Rss.where('gid<0'):
        if greader is None:
            greader = Reader(GREADER_USERNAME, GREADER_PASSWORD)
        greader.unsubscribe('feed/'+i.url)
        #print "unsubscribe",i.url
        i.delete()


if __name__ == '__main__':
    print rss_po_list_by_state(0)
    #rss_subscribe()
    # from collections import defaultdict
    # user_id = defaultdict()
    # for i in RssPo.where():
    #     pass

    #greader = Reader(GREADER_USERNAME, GREADER_PASSWORD)
    #greader.empty_subscription_list()
    pass
    #rss = Rss.get(202)
    #rss.gid = 0
    #rss.save() 
    #RssPo.where(user_id=10098398).delete()
