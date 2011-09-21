#!/usr/bin/env python
# -*- coding: utf-8 -*-

import _db
from model.zsite import zsite_new, ZSITE_STATE_ACTIVE, Zsite
from model.cid import CID_SITE
from model.zsite_admin import zsite_admin_new
from model.zsite_show import zsite_show_new

ZSITE_STATE_SITE_PUBLIC = 40
ZSITE_STATE_SITE_SECRET = 20


ZSITE_STATE_SITE2CN = (
    (ZSITE_STATE_SITE_PUBLIC, '公开'),
    (ZSITE_STATE_SITE_SECRET, '私密'),
)

ZSITE_STATE_SITE2CN_DICT = dict(ZSITE_STATE_SITE2CN)

def site_new(name, admin_id, state):
    if state not in ZSITE_STATE_SITE2CN:
        state = ZSITE_STATE_SITE_PUBLIC

    site = zsite_new(name, CID_SITE, state)
    site_id = site.id
    zsite_admin_new(site_id, admin_id)

    if state > ZSITE_STATE_SITE_SECRET:
        zsite_show_new(site_id, CID_SITE)

    return site

def site_state_total(state):
    if state:
        return Zsite.where(cid=CID_SITE,state=state).count()
    else:
        return Zsite.where(cid=CID_SITE).count()

def site_by_state(state,limit=None,offset=None):
    if state:
        return Zsite.where(cid=CID_SITE,state=state).order_by('id desc').col_list(limit,offset,'id')
    else:
        return Zsite.where(cid=CID_SITE).order_by('id desc').col_list(limit,offset,'id')
if __name__ == '__main__':
    print '..'

