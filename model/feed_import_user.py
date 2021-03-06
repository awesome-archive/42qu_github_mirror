#coding:utf-8
from _db import redis
from model.zsite import Zsite
from operator import itemgetter

REDIS_FEED_IMPORT_USER = 'FeedImportUser'
REDIS_FEED_IMPORT_USER_ID_LIST = 'FeedImportUser:%s'


def feed_import_user_new(user_id, feed_import_id):
    if redis.sadd(REDIS_FEED_IMPORT_USER_ID_LIST%user_id, feed_import_id):
        redis.zincrby(REDIS_FEED_IMPORT_USER, user_id, 1)


def feed_import_user_rm(user_id, feed_import_id):
    key = REDIS_FEED_IMPORT_USER_ID_LIST%user_id
    redis.srem(key, feed_import_id)
    length = redis.scard(key)
    if length:
        redis.zadd(REDIS_FEED_IMPORT_USER, user_id, length)
    else:
        redis.zrem(REDIS_FEED_IMPORT_USER, user_id)

def feed_import_id_by_user_id(user_id):
    return redis.srandmember(REDIS_FEED_IMPORT_USER_ID_LIST%user_id) 

def user_list_count_by_feed_import_user():
    id_count_list = redis.zrevrange(REDIS_FEED_IMPORT_USER, 0, -1, True, int)
    zsite_list = Zsite.mc_get_list(map(itemgetter(0), id_count_list))
    for i, count in zip(zsite_list, map(itemgetter(1), id_count_list)):
        i.feed_import_count = count 
    return zsite_list
    #count = redis.zcard(REDIS_FEED_IMPORT_USER) 
    #return count,  zsite_list

if __name__ == '__main__':
    pass
    print user_list_count_by_feed_import_user()

#    user_id = 10000000
#    feed_import_id = 1
#
#    feed_import_user_new(user_id, feed_import_id)
#    print id_count_by_feed_import_user(11, 0)
#    print feed_import_id_by_user_id(user_id)
#    feed_import_user_rm(user_id, feed_import_id)
#    print feed_import_id_by_user_id(user_id)
#    print id_count_by_feed_import_user(11, 0)

