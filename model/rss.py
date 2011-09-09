#!/usr/bin/env python
# -*- coding: utf-8 -*-
from _db import Model, McModel
from zkit.google.greader import Reader
import json
import sys
from zkit.htm2txt import htm2txt
from config import GREADER_USERNAME, GREADER_PASSWORD


RSS_UNCHECK = 0
RSS_RM = 1
RSS_PRE_PO = 2
RSS_POED = 3


class Rss(McModel):
    pass

class RssPo(McModel):
    pass



def rss_add(user_id, url):
    Rss.raw_sql('insert into rss (user_id, url) values(%s, %s)', user_id, url)

def rss_po_list_by_state(state, limit=1, offset=10):
    p = RssPo.raw_sql('select id,user_id,title,txt,pic_list from rss_po where state = %s order by id desc limit %s offset %s', state, limit, offset).fetchall()
    return p


def get_unread_update():
    GREADER = Reader(GREADER_USERNAME, GREADER_PASSWORD)

    feeds = GREADER.unread_feed()
    for feed in feeds:
        rs = Rss.raw_sql('select id,user_id from rss where url = %s', feed[5:]).fetchone()
        if rs:
            id, user_id = rs

            res = GREADER.unread(feed)
            for i in res:
                link = i['alternate'][0]['href']
                title = i['title']
                rss_uid = i.get('id') or 1
                snippet = i.get('summary') or i.get('content') or None

                if snippet:
                    htm = snippet['content']
                    
                    if htm:

                        txt, pic_list = htm2txt(htm)
                        pic_list = json.dumps(pic_list)

                        RssPo.raw_sql(
                            'insert into rss_po (user_id,rss_id,rss_uid,title,txt,state,link,pic_list) value(%s,%s,%s,%s,%s,%s,%s,%s)', 
                            user_id, id, rss_uid, title, txt, RSS_UNCHECK, link, pic_list
                        )




if __name__ == '__main__':
    get_unread_update()
    print RssPo.where(state=0).count()
    #get_unread_update()
    #get_rss_json('feed/http://feed43.com/rexsong.xml')
    #rss_feed()



