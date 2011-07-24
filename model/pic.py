#!/usr/bin/env python
# -*- coding: utf-8 -*-
from _db import Model, McModel, McCache
from time import time
from fs import fs_set_jpg, fs_url_jpg
from cid import CID_ICO, CID_ICO96, CID_PO_PIC, CID_PIC
from mail import rendermail


class PicMixin(object):
    def __getattr__(self, name):
        if name.startswith('src'):
            size = name[3:]
            if size.isdigit():
                return fs_url_jpg(size, self.id)


class Pic(Model, PicMixin):
    pass


def pic_new(cid, user_id):
    pic = Pic(
        cid=cid,
        user_id=user_id,
        create_time=int(time()),
    ).save()
    return pic.id

def pic_save(pic_id, pic):
    fs_set_jpg('0', pic_id, pic)


def _pic_list_to_review_by_cid(cid, start_id, limit):
    return Pic.where(cid=cid, state=1, admin_id=0).where('id>%s' % start_id).order_by('id')[:limit]

def pic_ico_to_review_iter(limit):
    from ico import ico
    count = 0
    start_id = 0
    while True:
        li = _pic_list_to_review_by_cid(CID_ICO, start_id, limit)
        for i in li:
            id = i.id
            user_id = i.user_id
            user_pic_id = ico.get(user_id)
            if id == user_pic_id:
                count += 1
                yield i
                if count == limit:
                    return
            else:
                i.state = 0
                i.save()
        if len(li) < limit:
            return
        else:
            start_id = id

def pic_ico_to_review(limit):
    return list(pic_ico_to_review_iter(limit))

def pic_to_review_count_by_cid(cid):
    return Pic.where(cid=cid, state=1, admin_id=0).count()

def pic_list_to_review_by_cid(cid, limit):
    if cid == CID_ICO:
        return pic_ico_to_review(limit)
    return _pic_list_to_review_by_cid(cid, limit)

def pic_list_reviewed_by_cid_state(cid, state, limit, offset):
    return Pic.where(cid=cid, state=state).where('admin_id>0').order_by('id desc')[offset: offset + limit]

def pic_reviewed_count_by_cid_state(cid, state):
    return Pic.where(cid=cid, state=state).where('admin_id>0').count()

def pic_yes(id, admin_id):
    pic = Pic.get(id)
    if pic:
        pic.admin_id = admin_id
        pic.state = 1
        pic.save()

def pic_no(id, admin_id):
    from ico import ico, ico96
    pic = Pic.get(id)
    if pic:
        pic.admin_id = admin_id
        pic.state = 0
        pic.save()
        cid = pic.cid
        #print pic.cid
        if cid == CID_ICO:
            user_id = pic.user_id
            if ico.get(user_id) == pic.id:
                ico.set(user_id, 0)
                ico96.set(user_id, 0)
        mq_pic_rm_mail(id)

PIC_RM_TEMPLATE = {
    CID_ICO: '/mail/pic/rm_ico.txt',
}

def pic_rm_mail(id):
    from ico import ico
    from user_mail import mail_by_user_id
    from zsite import Zsite
    pic = Pic.get(id)
    if pic:
        cid = pic.cid
        user_id = pic.user_id
        template = PIC_RM_TEMPLATE.get(cid)
        if template:
            user = Zsite.mc_get(user_id)
            name = user.name
            mail = mail_by_user_id(user_id)
            if cid == CID_ICO:
                if not ico.get(user_id):
                    rendermail(template, mail, name,
                               user=user,
                              )



from mq import mq_client
mq_pic_rm_mail = mq_client(pic_rm_mail)

if __name__ == '__main__':
    print  Pic.get(25763)
