#!/usr/bin/env python
# -*- coding: utf-8 -*-
from hashlib import md5
from _db import McCache
from decorator import decorator

SPAM_USER_ID = set((
    10009078, #欲望清单 www.desirelist.nst
    10003899, #欲望清单 www.desirelist.nst
    10011921,
    10022520,
))

def is_spammer(user_id):
    if int(user_id) in SPAM_USER_ID:
        return True

mc_lastest_hash = McCache('LastestHash:%s')

def is_same_post(user_id, *args):
    m = md5()
    for i in args:
        if type(i) is not str:
            i = str(i)
        m.update(i)
    h = m.digest()
    user_id = str(user_id)
    if h == mc_lastest_hash.get(user_id):
        return True
    mc_lastest_hash.set(user_id, h, 60)
    return False

@decorator
def anti_same_post(func, user_id, *args, **kwds):
    values = kwds.values()
    values.extend(args)
    if is_same_post(user_id, *values):
        return
    return func(user_id, *args, **kwds)

if __name__ == '__main__':
    print is_spammer(14)
