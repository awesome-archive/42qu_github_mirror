#coding:utf-8

from _db import cursor_by_table, McModel, McLimitA, McCache, McNum, Model, McCacheM, McCacheA
from po import Po, PO_CID
from model.state import STATE_PO_ZSITE_REVIEW , STATE_PO_ZSITE_ACCPET
from model.feed_render import render_zsite_feed_list

#mc_pos_id_list_by_cid = McCacheM("PosIdListByCid:%s")

mc_po_count_by_zsite_id = McCacheA('PoCountByZsiteId:%s')

def _po_cid_count_by_zsite_id(zsite_id, cid):
    qs = Po.where(
        zsite_id=zsite_id
    ).where('state>=%s'%STATE_PO_ZSITE_ACCPET)
    if cid:
        qs = qs.where(cid=cid)
    return qs.count()

po_cid_count_by_zsite_id = McNum(_po_cid_count_by_zsite_id, 'PoIdCount:%s')

@mc_po_count_by_zsite_id('{zsite_id}')
def _po_count_by_zsite_id(zsite_id):
    return tuple(
        po_cid_count_by_zsite_id(zsite_id, i) for i in PO_CID
    )

def po_count_by_zsite_id(zsite_id):
    return zip(
        PO_CID, _po_count_by_zsite_id(zsite_id)
    )

def po_list_by_zsite_id(user_id, zsite_id, cid, limit, offset):
    return render_zsite_feed_list(
            user_id,
            po_id_list_by_zsite_id(zsite_id, cid, limit, offset)
        )

def po_id_list_by_zsite_id(zsite_id, cid, limit, offset):
    qs = Po.where(
        zsite_id=zsite_id
    ).where('state>=%s'%STATE_PO_ZSITE_ACCPET)

    if cid:
        qs = qs.where(cid=cid)

    return qs.order_by('id desc').col_list(limit, offset)


class ZsiteSiteMax(Model):
    pass


class ZsiteSitePos(Model):
    pass


def pos_id_list_by_cid(zsite_id , user_id):
    r = ZsiteSitePos.where(zsite_id=zsite_id, user_id=user_id).col_list(
            col='cid,pos_id'
        )
    return dict(r)

def pos_mark_all(zsite_id, user_id):
    pass

def pos_mark(zsite_id, user_id, cid):
    pass

def next_id_list(zsite_id, user_id):
    pass


if __name__ == '__main__':
    print pos_id_list_by_cid(1, 2)

