#coding:utf-8


SITE_REC_STATE_REJECT = 0
SITE_REC_STATE_PASS = 1
SITE_REC_STATE_FAV = 2
SITE_REC_STATE = (0, 1, 2)



from _db import cursor_by_table, McModel, McCache, McNum, Model, McCacheM, McCacheA
from model.zsite import Zsite
from kv import Kv
from model.zsite import  Zsite
from model.cid import CID_SITE, CID_USER
from model.zsite_fav import zsite_fav_new, zsite_fav_rm
from model.top_rec import top_rec_unmark, TOP_REC_CID_SITE_REC, top_rec_mark
from model.follow import follow_get_list
from model.ico import ico_url_bind
from model.career import career_bind
from zkit.txt import cnenoverflow
from model.motto import motto

SiteRec = Kv('site_rec', 0)
#SiteRecNew = Kv('site_rec_new', 0)

class SiteRecHistory(Model):
    pass

#def site_rec(user_id):
#    zsite_id = SiteRecNew.get(user_id)
#    if zsite_id:
#        return Zsite.mc_get(zsite_id)

def site_rec(user_id):
    #zsite_id = SiteRecNew.get(user_id)
    zsite_id = '10000000'
    if zsite_id:
        return Zsite.mc_get_list(map(int, zsite_id.split()))


def site_rec_feeckback(user_id, zsite_id, state):
    site = Zsite.mc_get(zsite_id)
    state = int(state)

    if not (site and site.cid == CID_SITE):
        return

    if state not in SITE_REC_STATE:
        return


    if state == SITE_REC_STATE_FAV:
        zsite_fav_new(site, user_id)
    if state == SITE_REC_STATE_REJECT :
        zsite_fav_rm(site, user_id)


    rech = SiteRecHistory.where(user_id=user_id).where(zsite_id=zsite_id)

    if rech:
        rech[0].state = state
        rech[0].save()
    else:
        SiteRecHistory(
                user_id=user_id, zsite_id=zsite_id, state=state
                ).save()


    id_list = SiteRecNew.get(user_id).split()
    if zsite_id in id_list:
        id_list.remove(zsite_id)

    SiteRecNew.set(user_id, ' '.join(map(str, id_list)))

    top_rec_unmark(user_id, TOP_REC_CID_SITE_REC)

def site_rec_set(user_id, site_id):
    SiteRecNew.set(user_id, ' '.join([str(i) for i in site_id]))
    top_rec_mark(user_id, TOP_REC_CID_SITE_REC)

def site_rec_dump(user_id):
    zsite_list = site_rec(user_id)
    ico_url_bind(zsite_list)
    zsite_id_list = tuple(i.id for i in zsite_list)

    user_list = []
    for i in zsite_list:
        if i.cid == CID_USER:
            user_list.append(i)
    career_bind(user_list)
    motto_dict = motto.get_dict(zsite_id_list)

    cnenoverflow
    result = []


    for i, is_follow in zip(
        zsite_list,
        follow_get_list(user_id, zsite_id_list)
    ):
        career = (' , '.join(filter(bool, i.career)) if i.cid==CID_USER else 0) or 0
        _motto = motto_dict.get(i.id) or 0
        if _motto:
            length = 14
            if not career:
                length += length
            _motto = cnenoverflow(_motto, length)[0]

        if is_follow and is_follow is not True:
            is_follow = 1
        result.append((
            i.id, #0 
            i.link, #1
            i.name, #2
            i.ico, #3
            career, #4
            i.cid , #5
            _motto , #6
            is_follow , #7
        ))
    return result

if __name__ == '__main__':
    from model.zsite_url import id_by_url
    jid = id_by_url('jandan')
    from zweb.orm import ormiter
    for i in ormiter(SiteRecHistory):
        print i.id
