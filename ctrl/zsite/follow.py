#!/usr/bin/env python
# -*- coding: utf-8 -*-
from _handler import ZsiteBase, LoginBase, XsrfGetBase
from zkit.page import page_limit_offset
from ctrl._urlmap.zsite import urlmap
from model.cid import CID_ZSITE
from model.follow import follow_rm, follow_new, follow_count_by_to_id, follow_id_list_by_to_id, follow_id_list_by_from_id, follow_id_list_by_from_id_cid
from model.zsite import Zsite

PAGE_LIMIT = 42

@urlmap('/follow')
class Follow(XsrfGetBase):
    def get(self):
        current_user = self.current_user
        zsite_id = self.zsite_id
        follow_new(current_user.id, zsite_id)
        self.render()

@urlmap('/follow/rm')
class FollowRm(XsrfGetBase):
    def get(self):
        current_user = self.current_user
        zsite_id = self.zsite_id
        follow_rm(current_user.id, zsite_id)
        self.redirect('/')

@urlmap('/follower')
@urlmap('/follower-(\d+)')
class Follower(ZsiteBase):
    def get(self, n=1):
        zsite_id = self.zsite_id
        total = follow_count_by_to_id(zsite_id)
        page, limit, offset = page_limit_offset(
            '/follower-%s',
            total,
            n,
            PAGE_LIMIT
        )
        if type(n) == str and offset >= total:
            return self.redirect('/follower')

        ids = follow_id_list_by_to_id(zsite_id, limit, offset)
        follower = Zsite.mc_get_list(ids)

        self.render(
            follower=follower,
            page=page,
        )

@urlmap('/following(\d)?')
@urlmap('/following(\d)?-(\d+)')
class Following(ZsiteBase):
    def get(self, cid=0, n=1):
        cid = int(cid)
        if cid not in CID_ZSITE:
            cid = 0

        zsite_id = self.zsite_id
        if cid:
            ids = follow_id_list_by_from_id_cid(zsite_id, cid)
        else:
            ids = follow_id_list_by_from_id(zsite_id)
        total = len(ids)
        page, limit, offset = page_limit_offset(
            '/following%s-%%s' % cid,
            total,
            n,
            PAGE_LIMIT
        )
        if type(n) == str and offset >= total:
            return self.redirect('/following%s' % (cid or ''))

        ids = ids[offset: offset + limit]
        following = Zsite.mc_get_list(ids)

        self.render(
            cid=cid,
            following=following,
            page=page,
        )
