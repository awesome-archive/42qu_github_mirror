#!/usr/bin/env python
# -*- coding: utf-8 -*-

import _db
from _db import Model, McModel, McCache, McLimitM, McNum, McCacheA, McCacheM, McCacheA, McLimitA
from model.zsite import zsite_new, ZSITE_STATE_ACTIVE, Zsite, ZSITE_STATE_VERIFY
from model.cid import CID_COM
from model.zsite_admin import zsite_admin_new, zsite_user_state, zsite_id_list_by_admin_id_sample, zsite_by_admin_id_count, zsite_id_list_by_admin_id
from model.zsite_show import zsite_show_new
from model.buzz import mq_buzz_site_new
from model.search_zsite import search_new
from model.zsite_list import ZsiteList, zsite_list_new
from zkit.algorithm.wrandom import sample_or_shuffle
from cid import CID_COM_PIC
from zkit.pic import pic_fit_width_cut_height_if_large
from fs import fs_set_jpg, fs_url_jpg
from pic import pic_new, pic_save


class ZsiteCom(McModel):
    pass

def com_pic_new(com_id, pic):
    pic_id = pic_new(CID_COM_PIC, com_id)
    pic_save(pic_id, pic)
    p1 = pic_fit_width_cut_height_if_large(pic, 357)
    fs_set_jpg('357', pic_id, p1)
    return pic_id

def zsite_com_new(com_id, hope, money, culture, team, cover_id, video_cid):
    zsite_com = ZsiteCom.get_or_create(id=com_id)
    zsite_com.hope = hope
    zsite_com.money = money
    zsite_com.culture = culture
    zsite_com.cover_id = cover_id
    zsite_com.team = team
    zsite_com.video_cid = video_cid
    zsite_com.save()

class ZsiteComPlace(McModel):
    pass

mc_zsite_com_id_list = McLimitA('ZsiteComList.%s',128)

@mc_zsite_com_id_list('{cid}')
def zsite_com_id_list(cid,limit,offset):
    return Zsite.where(cid=cid).col_list(limit, offset,'id')

def zsite_com_list(cid,limit,offset):
    return Zsite.mc_get_list(zsite_com_id_list(cid,limit,offset))

def zsite_com_place_new(zsite_id,pid,address):
    zsite_com = ZsiteComPlace.get_or_create(com_id=zsite_id, pid=pid)
    zsite_com.address = address
    zsite_com.save()
    return zsite_com


zsite_com_count = McNum(lambda cid: Zsite.where(cid= cid).count(), 'ZsiteComCount.%s')


def com_new(name,admin_id,state=ZSITE_STATE_VERIFY):
    com = zsite_new(name, CID_COM,state)
    com_id = com.id
    zsite_com_count.delete(CID_COM)
    mc_zsite_com_id_list.delete(CID_COM)
    return com

def com_can_admin(zsite_id, user_id):
    if zsite_user_state(zsite_id, user_id) >= STATE_ADMIN:
        return True

#def zsite_com_count(cid):
#    return Zsite.where(cid=cid).count()



def pid_by_com_id(com_id):
    return ZsiteComPlace.where(com_id=com_id)

if __name__ == "__main__":
    print zsite_com_count(3)
