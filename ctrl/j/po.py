#!/usr/bin/env python
# -*- coding: utf-8 -*-
from yajl import dumps
from ctrl._urlmap.j import urlmap
from model.zsite_url import zsite_by_domain
from _handler import JLoginBase
from model.fs import fs_url_jpg
from model.po import Po, CID_WORD, CID_NOTE, po_word_new
from model.po_pic import pic_can_add, po_pic_new, po_pic_rm
from model.po_question import answer_word2note
from model.zsite import user_can_reply
from model.zsite_tag import zsite_tag_list_by_zsite_id_with_init, tag_id_by_po_id, zsite_tag_new_by_tag_id, zsite_tag_new_by_tag_name, zsite_tag_rm_by_tag_id, zsite_tag_rename
from zkit.pic import picopen
from model.cid import CID_SITE, CID_COM
from model.zsite_url import url_or_id
from model.career import career_dict
import time
from model.ico import pic_url_with_default
from model.feed_render import feed_tuple_by_db
from model.career import career_current
from model.txt2htm import txt_withlink

def post_reply(self, id):
    user = self.current_user

    if not user_can_reply(user):
        self.finish('{"can_not_reply":1}')
    else:
        result = {}
        txt = self.get_argument('txt', None)
        if txt:
            user_id = self.current_user_id
            po = Po.mc_get(id)
            if po.can_view(user_id):
                po.reply_new(user, txt, po.state)

        self.finish(result)


@urlmap('/j/po/reply/json/(\d+)')
class PoReplyJson(JLoginBase):
    def get(self, id):
        po = Po.mc_get(id)
        user_id = self.current_user_id
        result = []

        if po and po.can_view(user_id):
            for reply in po.reply_list():
                user = reply.user
                result.append(
                    (url_or_id(user.id), reply.htm, user.name)
                )

        return self.finish(dumps(result))



@urlmap('/j/po/(\d+)')
class JPo(JLoginBase):
    def get(self, id):
#        data = {
#            "zsite":{
#                "name":"w",
#                "unit":"xx",
#                "title":"zz"
#            },
#            "name":"2011年第2次BPUG活动",
#            "id":1234,
#            "fav":True,
#            "reply_count":1,
#            "tag_id":232,
#            "tag_name":"sss"
#        }
        po = Po.mc_get(id)
        user = po.user
        result = [id]
        result.extend(feed_tuple_by_db(id))
        result.pop()
        result.pop()
        result.append(po.htm)

        zsite = [user.name, user.link]
        zsite.extend(career_current(po.user_id))

        result.append(zsite)
        self.finish(dumps(result))


@urlmap('/j/po/word')
class Word(JLoginBase):
    def post(self):
        result = None
        current_user_id = self.current_user_id
        txt = self.get_argument('txt', None)
        if txt:
            host = self.request.host
            zsite = zsite_by_domain(host)
            if zsite and zsite.cid == CID_SITE:
                zsite_id = zsite.id
            else:
                zsite_id = 0

            m = po_word_new(current_user_id, txt, zsite_id=zsite_id)
            if not zsite_id and m:
                c_dict = career_dict(set([current_user_id]))
                unit, title = c_dict[current_user_id]
                result = [
                    [
                        1, zsite.name, zsite.link, unit,
                        title, pic_url_with_default(current_user_id, '219'),
                        [[m.id, [], 0, 61, 0, 0, 0, time.time(), None, txt_withlink(txt), False]]
                    ],
                    []
                ]
        self.finish(dumps(result))



@urlmap('/j/po/reply/(\d+)')
class Reply(JLoginBase):
    post = get = post_reply

@urlmap('/j/po/tag/edit')
class TagEdit(JLoginBase):
    def post(self):
        current_user_id = self.current_user_id
        tag_list = self.get_arguments('tag')
        name_list = self.get_arguments('name')
        for tag_id, tag_name in zip(tag_list, name_list):
            zsite_tag_rename(current_user_id, tag_id, tag_name)
        self.finish('{}')

@urlmap('/j/po/tag')
class Tag(JLoginBase):
    def get(self):
        current_user_id = self.current_user_id
        tag_list = zsite_tag_list_by_zsite_id_with_init(current_user_id)
        self.finish(dumps(tag_list.iteritems()))

@urlmap('/j/po/tag/rm/(\d+)')
class TagRm(JLoginBase):
    def get(self, id):
        current_user_id = self.current_user_id
        zsite_tag_rm_by_tag_id(current_user_id, id)
        self.finish('{}')

@urlmap('/j/po/upload/rm')
@urlmap('/j/po/upload/rm/(\d+)')
class NoteUploadRm(JLoginBase):
    def post(self, id=0):
        seq = self.get_argument('seq')
        user_id = self.current_user_id
        po_pic_rm(user_id, id, seq)
        self.finish('{}')

@urlmap('/j/po/upload')
@urlmap('/j/po/upload/(\d+)')
class NoteUpload(JLoginBase):
    def post(self, id=0):
        #USER DUMPS FIX HEADER FOR FIREFOX
        if id:
            id = int(id)
        r = self._post(id)
        if isinstance(r, (int, long)):
            r = {'status':r}
        r = dumps(r)
        self.finish(r)

    def _post(self, id):
        user_id = self.current_user_id

        files = self.request.files
        img = files.get('img')
        if img:
            img = img[0]['body']
        else:
            return 0

        if len(img) > 1024*1024*12:
            return 2

        img = picopen(img)
        if not img:
            return 10

        if id:
            po = Po.mc_get(id)
            if not po or po.user_id != user_id or (po.cid == CID_WORD and po.rid == 0):
                return 0
            if po.cid == CID_WORD:
                answer_word2note(po)

        if not pic_can_add(user_id, id):
            return 16

        pic = po_pic_new(user_id, id, img)
        if not pic:
            return 14

        r = {
            'status': 0,
            'src': fs_url_jpg(219, pic.id),
            'seqid': pic.seq,
        }

        return r



