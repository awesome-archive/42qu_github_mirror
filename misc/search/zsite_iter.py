#!/usr/bin/env python
# -*- coding: utf-8 -*-
import _env
from collections import defaultdict
from mmseg.search import seg_txt_search, seg_title_search, seg_txt_2_dict
from zweb.orm import ormiter
from model.career import career_list_all
from model.txt import txt_get
from model.user_mail import mail_by_user_id
from model.zsite import Zsite, CID_USER, ZSITE_STATE_CAN_REPLY
from model.zsite_url import url_by_id
from model.zsite_rank import zsite_rank_by_zsite_id

def zsite2keyword(z):
    r = []
    t = defaultdict(int)
    id = z.id
    if z.cid == CID_USER:
        mail = mail_by_user_id(id)
        if mail:
            t[mail] += 2
            t[mail.split('@', 1)[0]] += 2

    url = url_by_id(id)
    if url:
        t[url] += 2

    name = z.name
    if name:
        for word in seg_title_search(name):
            t[word] += 2

    txt = txt_get(id)

    if txt:
        man_txt_len = len(txt)

        for word in seg_txt_search(txt):
            t[word] += 1

    for seq, career in enumerate(career_list_all(id)):
        if seq:
            add = 1
        else:
            add = 2

        unit = career.unit
        title = career.title
        txt = career.txt

        if unit:
            for word in seg_title_search(unit):
                t[word] += add

        if title:
            for word in seg_title_search(title):
                t[word] += add
        if txt:
            for word in seg_txt_search(txt):
                t[word] += add

    return t


def zsite_keyword_iter():
    for i in ormiter(Zsite):
        id = i.id
        kw = zsite2keyword(i)
        if not kw:
            continue

        yield str(id), zsite_rank_by_zsite_id(id), kw.items()


if __name__ == '__main__':
    z = Zsite.mc_get(16)
    if z:
        for k, v in zsite2keyword(z)[1].iteritems():
            print k, v
