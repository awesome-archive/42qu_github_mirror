#!/usr/bin/env python
# -*- coding: utf-8 -*-
from _handler import JLoginBase, Base
from ctrl._urlmap.j import urlmap
from model.vote import vote_state
from model.po import Po
from yajl import dumps
from model.vote import vote_down_x, vote_down, vote_up_x, vote_up
from model.feed_render import MAXINT, PAGE_LIMIT, render_feed_by_zsite_id, FEED_TUPLE_DEFAULT_LEN, dump_zsite
from model.feed import feed_rt, feed_rt_rm, feed_rt_id
from model.ico import pic_url_with_default
from model.cid import CID_NOTE, CID_QUESTION, CID_ANSWER, CID_PHOTO, CID_WORD
from model.zsite_tag import zsite_tag_id_tag_name_by_po_id
from itertools import groupby
from operator import itemgetter
from model.career import career_dict
from model.zsite import Zsite

@urlmap('/j/feed/up1/(\d+)')
class FeedUp(JLoginBase):
    def post(self, id):
        current_user_id = self.current_user_id
        vote_up(current_user_id, id)
        feed_rt(current_user_id, id)
        self.finish('{}')


@urlmap('/j/feed/up0/(\d+)')
class FeedUpX(JLoginBase):
    def post(self, id):
        current_user_id = self.current_user_id
        vote_up_x(current_user_id, id)
        feed_rt_rm(current_user_id, id)
        self.finish('{}')


@urlmap('/j/feed/down1/(\d+)')
class FeedDown(JLoginBase):
    def post(self, id):
        current_user_id = self.current_user_id
        vote_down(current_user_id, id)
        feed_rt_rm(current_user_id, id)
        self.finish('{}')


@urlmap('/j/feed/down0/(\d+)')
class FeedDownX(JLoginBase):
    def post(self, id):
        current_user_id = self.current_user_id
        vote_down_x(current_user_id, id)
        self.finish('{}')


@urlmap('/j/feed/(\d+)')
class Feed(JLoginBase):
    def get(self, id):
        id = int(id)
        if id == 0:
            id = MAXINT
        current_user_id = self.current_user_id

        result , last_id = render_feed_by_zsite_id(current_user_id, PAGE_LIMIT, id)
        result = tuple(
            (i, tuple(g)) for i, g in groupby(result, itemgetter(0))
        )
        zsite_id_set = set(
            i[0] for i in result
        )
        c_dict = career_dict(zsite_id_set)

        r = []
        for zsite_id, item_list in result:
            zsite = Zsite.mc_get(zsite_id)
            t = []
            for i in item_list:
                id = i[1]
                cid = i[3]
                rid = i[4]

                if len(i) >= FEED_TUPLE_DEFAULT_LEN:
                    after = i[FEED_TUPLE_DEFAULT_LEN:]
                    i = i[:FEED_TUPLE_DEFAULT_LEN]
                else:
                    after = None

                i.extend([
                    vote_state(current_user_id, id),
                ])

                if cid != CID_WORD:
                    i.extend(zsite_tag_id_tag_name_by_po_id(zsite_id, id))

                if after:
                    i.extend(after)
                t.append(i[1:])

            unit, title = c_dict[zsite_id]
            r.append((
                zsite.name,
                zsite.link,
                unit,
                title,
                pic_url_with_default(zsite_id, '219'),
                t
            ))
        r.append(last_id)
        result = dumps(r)
        self.finish(result)


@urlmap('/j/fdtxt/(\d+)')
class FdTxt(Base):
    def get(self, id):
        po = Po.mc_get(id)
        current_user_id = self.current_user_id
        if po.can_view(current_user_id):
            result = po.htm
        else:
            result = ''
        self.finish(result)
