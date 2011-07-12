#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from _db import Model, McModel, McCache, McCacheA, McLimitA, McNum
from cgi import escape
from zkit.pic import pic_fit_width_cut_height_if_large
from pic import pic_new, pic_save, PicMixin
from cid import CID_PO_PIC
from fs import fs_set_jpg, fs_url_jpg

PIC_HTM = '<div class="PIC%s"><img src="%s"%s>%s</div>'

PIC_LIMIT = 42

#PIC_SAFE = 30
#PIC_ADD = 20
#PIC_SELF_DELETE = 10
#PIC_UNSAFE = 5
#PIC_ANTI = 0

PIC_SIZE = 721
PIC_THUMB_SIZE = 219
#PIC_LIST_SIZE = (219, 123)
#PIC_LIST_PATH = '%s_%s' % PIC_LIST_SIZE

PIC_LEFT = -1 # 1
PIC_CENTER = 0
PIC_RIGHT = 1 # 2


class PoPic(McModel, PicMixin):
    pass

po_pic_sum = McNum(lambda user_id, po_id: PoPic.where(user_id=user_id, po_id=po_id).count(), 'PoPicTotal.%s')

def pic_can_add(user_id, po_id=0):
    return po_pic_sum(user_id, po_id) < PIC_LIMIT

def seq_gen(user_id, po_id):
    c = PoPic.raw_sql('select max(seq) from po_pic where user_id=%s and po_id=%s', user_id, po_id)
    seq = c.fetchone()[0] or 0
    return seq + 1

def po_pic_new(user_id, po_id, pic, seq=None):
    pic_id = pic_new(CID_PO_PIC, user_id)
    pic_save(pic_id, pic)
    po_pic_save(pic_id, pic)

    if seq is None:
        seq = seq_gen(user_id, po_id)
    pp = PoPic(id=pic_id, user_id=user_id, po_id=po_id, seq=seq)
    pp.save()
    mc_flush(user_id, po_id)
    return pp

def po_pic_save(pic_id, pic):
    p1 = pic_fit_width_cut_height_if_large(pic, 721)
    fs_set_jpg('721', pic_id, p1)

    p2 = pic_fit_width_cut_height_if_large(pic, 219)
    fs_set_jpg('219', pic_id, p2)

def po_pic_rm(user_id, po_id, seq):
    pp = PoPic.get(user_id=user_id, po_id=po_id, seq=seq)
    if pp:
        pic_id = pp.id
        pp.delete()
        mc_flush(user_id, po_id)

def mc_flush(user_id, po_id):
    po_pic_sum.delete(user_id, po_id)
    mc_pic_id_list.delete('%s_%s' % (user_id, po_id))

#mc_pic_new_id_list = McCacheA('PoPicNewIdList.%s')
#
#@mc_pic_new_id_list('{user_id}')
#def pic_new_id_list(user_id):
#    return PoPic.where(user_id=user_id, po_id=0).order_by('seq desc').col_list()
#
#def pic_new_list(user_id):
#    ids = pic_new_id_list(user_id)
#    li = PoPic.mc_get_list(ids)
#    for i in li:
#        i.src219 = fs_url_jpg(i.id, 219)
#    return li

mc_pic_id_list = McCacheA('PoPicIdList.%s')

@mc_pic_id_list('{user_id}_{po_id}')
def pic_id_list(user_id, po_id):
    return PoPic.where(user_id=user_id, po_id=po_id).order_by('seq desc').col_list()

def pic_list(user_id, po_id):
    ids = pic_id_list(user_id, po_id)
    li = PoPic.mc_get_list(ids)
    return li

def pic_list_edit(user_id, po_id):
    li = pic_list(user_id, po_id)
#    for i in li:
#        i.src219 = fs_url_jpg(219, i.id)
    return li

def pic_seq_dict(user_id, po_id):
    ids = pic_id_list(user_id, po_id)
    return PoPic.mc_get_dict(ids)

def pic_seq_dict_html(user_id, po_id):
    d = {}
    for i in pic_seq_dict(user_id, po_id).itervalues():
        title = escape(i.title)
        align = i.align

        if align == -1:
            align = 'L'
        elif align == 1:
            align = 'R'
        else:
            align = ''

        if title:
            alt = ' alt="%s"' % title.replace('"', '&quot;')
            div = '<div>%s</div>' % title
        else:
            alt = ''
            div = ''

        d[i.seq] = PIC_HTM % (
            align,
            i.src721,
#            fs_url_jpg(684, i.id),
            alt,
            div,
        )
    return d

PIC_FIND = re.compile(r'图:([\d]+)')
PIC_SUB = re.compile(r'图:([\d]+)')
PIC_HTML = '<div class="pmix np%s"><img src="%s" alt="%s"><div>%s</div></div>'

#mc_htm = McCache('PoHtm.%s')
#@mc_htm('{self.id}')
#def htm(self):
#    return pic2htm(self.txt, pic_seq_dict_html(self.user_id, self.id))

def re_pic2htm(match, d):
    m = int(match.group(1))
    return d.get(m, match.group(0))

def pic_htm(htm, user_id, po_id):
    pic_dict = pic_seq_dict_html(user_id, po_id)
    return PIC_SUB.sub(lambda x: re_pic2htm(x, pic_dict), htm)

if __name__ == '__main__':
    pass
