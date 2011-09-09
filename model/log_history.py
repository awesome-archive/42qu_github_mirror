#!/usr/bin/env python
# -*- coding: utf-8 -*-
from _db import Model
from zsite import Zsite
from po import Po
from reply import Reply
from model.days import today_days
import time
from model.cid import CID_USER
from operator import itemgetter
from follow import Follow


LOG_HISTORY_CID_USER = 1
LOG_HISTORY_CID_PO = 2
LOG_HISTORY_CID_REPLY = 3
LOG_HISTORY_CID_FOLLOW = 4

LOG_HISTORY_CID = (
    LOG_HISTORY_CID_USER,
    LOG_HISTORY_CID_PO,
    LOG_HISTORY_CID_REPLY,
    LOG_HISTORY_CID_FOLLOW,
)
LOG_HISTORY_CN_CID = {
    LOG_HISTORY_CID_USER: '用户',
    LOG_HISTORY_CID_PO: '帖子',
    LOG_HISTORY_CID_REPLY: '回复',
    LOG_HISTORY_CID_FOLLOW:'关注',
}


class LogHistory(Model):
    pass



def log_history_new(cls , cid, num, day=None):
    if day is None:
        day = today_days()
    c = LogHistory.raw_sql(
        'select num from log_history where cid=%s and day<%s order by day desc limit 1',
        cid, day
    )
    pre_num = c.fetchone()
    if pre_num:
        pre_num = pre_num[0]

    if pre_num:
        incr = num - pre_num
    else:
        incr = 0

    max_id = cls.raw_sql('select max(id) from %s'%cls.Meta.table).fetchone()
    if max_id:
        max_id = max_id[0]
    else:
        max_id = 0

    LogHistory.raw_sql(
'insert into log_history (day,num,incr,cid, max_id) values (%s,%s,%s,%s,%s) on duplicate key update num=%s, incr=%s, max_id=%s',
day , num, incr, cid, max_id, num, incr, max_id
    )


def log_incr_list(cid, limit=100):
    c = LogHistory.raw_sql(
'select incr from log_history where cid=%s order by day desc limit %s', cid, limit+1
    ).fetchall()
    return list(reversed(map(itemgetter(0), c)))[1:]


def log_num_user():
    num = Zsite.raw_sql(
        'select count(1) from zsite where cid=%s', CID_USER
    ).fetchone()[0]
    log_history_new(Zsite, LOG_HISTORY_CID_USER, num)

def log_num_po():
    num = Po.raw_sql('select count(1) from po').fetchone()[0]
    log_history_new(Po, LOG_HISTORY_CID_PO, num)


def log_num_reply():
    num = Reply.raw_sql('select count(1) from reply').fetchone()[0]
    log_history_new(Reply, LOG_HISTORY_CID_REPLY, num)


def log_num_follow():
    num = Follow.raw_sql('select count(1) from follow').fetchone()[0]
    log_history_new(Follow, LOG_HISTORY_CID_FOLLOW, num)


def log_num():
    log_num_user()
    log_num_reply()
    log_num_po()
    log_num_follow()


if __name__ == '__main__':
    c = LogHistory.raw_sql(
        'select day , incr, num from log_history where cid=%s order by day desc limit %s', LOG_HISTORY_CID_REPLY, 100
    ).fetchall()
    print c
    log_num()
    print log_incr_list(LOG_HISTORY_CID_REPLY, limit=100)
