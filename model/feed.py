#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from _db import McModel, McCache, cursor_by_table, McCacheA, McCacheM
from mq import mq_client
from zkit.algorithm.merge import imerge
from gid import gid

class Feed(McModel):
    pass

MAXINT = sys.maxint
PAGE_LIMIT = 42

mc_feed_iter = McCacheM('FeedIter:%s')
mc_feed_tuple = McCacheM('F%s')
mc_feed_rt_id = McCache('R%s')

cursor = cursor_by_table('feed')

class Feed(McModel):
    pass

def feed_new(id, zsite_id, cid, rid=0):
    cursor.execute(
        'insert into feed (id, zsite_id, cid, rid) values (%s,%s,%s,%s) on duplicate key update id=id',
        (id, zsite_id, cid, rid)
    )
    cursor.connection.commit()
    mc_feed_iter.delete(zsite_id)
    return id

def feed_rm(id):
    cursor.execute('select zsite_id, rid from feed where id=%s', id)
    r = cursor.fetchone()
    if r:
        zsite_id , rid = r
        cursor.execute('delete from feed where id=%s', id)
        cursor.connection.commit()
        mc_feed_iter.delete(zsite_id)
        if not rid:
            feed_rt_rm_by_rid(id)
            #TODO MQ
            #mq_feed_rt_rm_by_rid(id)


def feed_rt_rm_by_rid(rid):
    cursor.execute('select id, zsite_id from feed where rid=%s', rid)
    for id, zsite_id in cursor:
        cursor.execute('delete from feed where id=%s', id)
        cursor.connection.commit()
        mc_feed_iter.delete(zsite_id)

mq_feed_rt_rm_by_rid = mq_client(feed_rt_rm_by_rid)

def feed_rt_rm(zsite_id, rid):
    id = feed_rt_id(zsite_id, rid)
    if id:
        cursor.execute('delete from feed where id=%s', id)
        cursor.connection.commit()
        mc_feed_iter.delete(zsite_id)
        mc_feed_rt_id.delete('%s_%s'%(zsite_id, rid))

def feed_rt(zsite_id, rid):
    feed = Feed.mc_get(rid)
    if feed and  not feed.rid and not feed_rt_id(zsite_id, rid):
        feed_new(gid(), zsite_id, feed.cid, rid)
        mc_feed_iter.delete(zsite_id)
        mc_feed_rt_id.delete('%s_%s'%(zsite_id, rid))

@mc_feed_rt_id('{zsite_id}_{rid}')
def feed_rt_id(zsite_id, rid):
    cursor.execute(
        'select id from feed where zsite_id=%s and rid=%s',
        (zsite_id, rid)
    )
    result = cursor.fetchone()
    if result:
        return result[0]
    return 0

FEED_ID_LASTEST_SQL = 'select id, rid from feed where zsite_id=%%s order by id desc limit %s'%PAGE_LIMIT
FEED_ID_ITER_SQL = 'select id, rid from feed where zsite_id=%%s and id<%%s order by id desc limit %s'%PAGE_LIMIT

@mc_feed_iter('{feed_id}')
def feed_id_lastest(feed_id):
    cursor.execute(FEED_ID_LASTEST_SQL, feed_id)
    return tuple(cursor.fetchall())

#TODO : 消息流的合并, feed_entry_id_iter 函数可以考虑用天涯的内存数据库来优化
#http://code.google.com/p/memlink/
def feed_iter(zsite_id, start_id=MAXINT):
    if start_id == MAXINT:
        id_list = feed_id_lastest(zsite_id)
        if id_list:
            for i in id_list:
                yield i
            start_id = i[0]
        else:
            return
    while True:
        cursor.execute(FEED_ID_ITER_SQL, (zsite_id, start_id))
        c = cursor.fetchall()
        if not c:
            break
        for i, in c:
            yield i
        start_id = i[0]


def feed_cmp_iter(zsite_id, start_id=MAXINT):
    for id, rid in feed_iter(zsite_id, start_id):
        yield FeedCmp(id, rid, zsite_id)

class FeedCmp(object):
    def __init__(self, id, rid, zsite_id):
        self.id = id
        self.rid = rid
        self.zsite_id = zsite_id

    def __cmp__(self, other):
        return other.id - self.id


class FeedMerge(object):
    def __init__(self, zsite_id_list):
        self.zsite_id_list = zsite_id_list

    def merge_iter(self, limit=MAXINT, begin_id=MAXINT):
        zsite_id_list = self.zsite_id_list
        count = 0
        for i in imerge(
            *[
                feed_cmp_iter(i, begin_id)
                for i in
                zsite_id_list
            ]
        ):
            yield i
            count += 1
            if count >= limit:
                break

if __name__ == '__main__':
#    for i in feed_iter(935):
#        print i
    #print feed_rt_rm(24,121)
    print feed_rt_id(24, 121)
