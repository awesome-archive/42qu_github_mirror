#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
CREATE TABLE  `zpage`.`import_feed` (
  `id` int(11) NOT NULL auto_increment,
  `title` varbinary(256) NOT NULL, `txt` blob NOT NULL,
  `author_id` int(11) NOT NULL,
  `url` varbinary(1024) NOT NULL,
  `state` int(11) NOT NULL,
  `src_id` int(11) NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=binary

CREATE TABLE `zpage`.`import_record` (
  `key` int  NOT NULL,
  `value` int  NOT NULL,
  PRIMARY KEY (`key`)
)
ENGINE = MyISAM;


CREATE TABLE `zpage`.`import_po_user` (
  `id` int  NOT NULL,
  `name` varchar(128)  NOT NULL,
  `cid` SMALLINT  NOT NULL,
  `url` int  NOT NULL,
  PRIMARY KEY (`id`)
)
ENGINE = MyISAM;

'''

import _env
from _db import Model, McModel
from po import po_note_new
from douban import DoubanUser, douban_feed_to_review_iter, douban_user_id_by_feed_id
from zkit.htm2txt import htm2txt
from zkit.txt import format_txt
from model.txt_img_fetch import txt_img_fetch
from kv import Kv
from duplicate import Duplicator
from url_short import url_short_id
from site_sync import site_sync_new
from config import DUMPLICATE_DB_PREFIX
from rec_read import rec_cid_push

douban_duplicator = Duplicator(DUMPLICATE_DB_PREFIX%'douban')
#douban_duplicator = Duplicator('douban.kch')

IMPORT_FEED_STATE_RM = 0
IMPORT_FEED_STATE_INIT = 10

IMPORT_FEED_STATE_REVIEWED = 20
IMPORT_FEED_STATE_REVIEWED_WITHOUT_AUTHOR = 30
IMPORT_FEED_STATE_REVIEWED_SYNC = 40
IMPORT_FEED_STATE_REVIEWED_WITHOUT_AUTHOR_SYNC = 50

IMPORT_FEED_STATE_POED = 60 

DOUBAN_ZSITE_ID = 68615

class PoMeta(McModel):
    pass

class ImportFeed(Model):
    pass

class PoMetaUser(McModel):
    @property
    def link(self):
        if self.cid == DOUBAN_ZSITE_ID:
            return 'http://www.douban.com/people/%s'%self.url

def user_url_by_po_meta_user_id(id):
    user = PoMetaUser.mc_get(id)
    if user:
        if user.cid == DOUBAN_ZSITE_ID:
            return 'http://www.douban.com/people/%s'%user_id.url

def user_id_by_feed_id_zsite_id(feed_id, zsite_id):
    if zsite_id == DOUBAN_ZSITE_ID:
        return douban_user_id_by_feed_id(feed_id)

def feed_next():
    return ImportFeed.where(state=IMPORT_FEED_STATE_INIT)[1]

def import_feed_rm(id):
    feed_state_set(id, IMPORT_FEED_STATE_RM)

def import_feed_new(title, txt, author_id, url, src_id, zsite_id, state=IMPORT_FEED_STATE_INIT):
    txt = format_txt(htm2txt(txt))
    if not douban_duplicator.txt_is_duplicate(txt):

        douban_user = DoubanUser.get(author_id)
        user_id = zsite_id_by_douban_user_id(douban_user)

        new_feed = ImportFeed(
                title=title,
                txt=txt,
                user_id=user_id,
                zsite_id=zsite_id,
                state=state,
                rid=src_id,
                url=url
                )

        new_feed.save()
        douban_duplicator.set_record(txt, new_feed.id)

        return new_feed

def feed_state_set(id, state):
    feed = ImportFeed.get(id)
    if feed:
        feed.state = state
        feed.save()

def zsite_id_by_douban_user_id(douban_user):
    zsite_id = 0
    if douban_user:
        douban_username = douban_user.name
        #TODO: get zsite_user_id
        zsite_id = 10001518
    return zsite_id

def feed2po_new():
    from zweb.orm import ormiter
    for feed in ormiter(
            ImportFeed,
            'state>%s and state<%s'%(
                IMPORT_FEED_STATE_INIT,
                IMPORT_FEED_STATE_POED
            )
        ):
        txt = txt_img_fetch(feed.txt)

        user_id = feed.user_id
        zsite_id = feed.zsite_id

        is_without_author = ((feed.state == IMPORT_FEED_STATE_REVIEWED_WITHOUT_AUTHOR_SYNC) or (feed.state == IMPORT_FEED_STATE_REVIEWED_WITHOUT_AUTHOR))

        if is_without_author:
            user_id = 0
            zsite_id = 0

        po = po_note_new(user_id, feed.title, txt, zsite_id=zsite_id)

        if po:
            feed_user =  user_id_by_feed_id_zsite_id(feed.rid, zsite_id)

            if not feed_user:
                feed_user_id = 0
            else:
                user = PoMetaUser.get_or_create(name = feed_user.name, cid = zsite_id)
                user.url = feed_user.id

                user.save()

                feed_user_id = user.id

            record = PoMeta.get_or_create(id = po.id)
            record.user_id = feed_user_id
            record.url_id = url_short_id(feed.url)

            record.save()

            if not is_without_author:
                po.rid = record.id
                po.save()

            if feed.state >= IMPORT_FEED_STATE_REVIEWED_SYNC:
                site_sync_new(po.id)

            feed.state = IMPORT_FEED_STATE_POED
            feed.save()

            rec_cid_push(feed.cid, po.id)

def review_feed(id, cid, author_rm=False, sync=False):
    feed = ImportFeed.get(id)
    if feed and feed.state==IMPORT_FEED_STATE_INIT :
        if author_rm:
            if sync:
                feed.state = IMPORT_FEED_STATE_REVIEWED_WITHOUT_AUTHOR_SYNC
            else:
                feed.state = IMPORT_FEED_STATE_REVIEWED_WITHOUT_AUTHOR
        else:
            if sync:
                feed.state = IMPORT_FEED_STATE_REVIEWED_SYNC
            else:
                feed.state = IMPORT_FEED_STATE_REVIEWED

        feed.cid = cid
        feed.save()

def import_feed_by_douban_feed():
    for i in douban_feed_to_review_iter():
        import_feed_new(
            i.title, i.htm, i.user_id, i.link, i.id, DOUBAN_ZSITE_ID
        )

if __name__ == '__main__':
    pass
    #import_feed_by_douban_feed()
    #print ImportFeed.where(state = IMPORT_FEED_STATE_INIT)
    feed2po_new()

