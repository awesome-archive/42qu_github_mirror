#!/usr/bin/env python
# -*- coding: utf-8 -*-
from _handler import Base, LoginBase, XsrfGetBase
from zweb._urlmap import urlmap
from model.po import Po, po_rm, po_word_new, po_note_new, po_question_new, STATE_SECRET, STATE_ACTIVE, po_state_set, CID_NOTE
from model.po_pic import pic_list, pic_list_edit, mc_pic_id_list
from model.po_pos import po_pos_get, po_pos_set
from model import reply
from model.zsite import Zsite
from zkit.jsdict import JsDict


def update_pic(form, user_id, po_id, id):
    pl = pic_list(user_id, id)
    for pic in pl:
        seq = pic.seq
        title = form['tit%s' % seq][0]
        align = form['pos%s' % seq][0]
        pic.title = title.strip()
        align = int(align)

        if align not in (-1, 0, 1):
            align = 0

        pic.align = align
        pic.po_id = po_id
        pic.save()


@urlmap('/po/(\d+)')
class PoIndex(Base):
    def get(self, id):
        po = Po.mc_get(id)
        current_user_id = self.current_user_id
        if po:
            link = po.link
            pos, state = po_pos_get(current_user_id, id)
            if pos > 0:
                link = '%s#reply%s' % (link, pos)
        else:
            link = '/'
        self.redirect(link)


@urlmap('/po/word')
class Word(LoginBase):
    def post(self):
        current_user = self.current_user
        txt = self.get_argument('txt', '')
        if txt.strip():
            po_word_new(current_user.id, txt)
        return self.redirect('/feed')


def po_can_edit(current_user_id, id):
    if id:
        po = Po.mc_get(id)
        if po:
            if po.can_admin(current_user_id):
                return po
    return JsDict()


@urlmap('/po/note')
@urlmap('/note/edit/(\d+)')
class Note(LoginBase):
    def get(self, id=0):
        current_user_id = self.current_user_id
        po = po_can_edit(current_user_id, id)
        self.render(po=po, pic_list=pic_list_edit(current_user_id, id))

    def post(self, id=0):
        current_user_id = self.current_user_id
        po = po_can_edit(current_user_id, id)
        name = self.get_argument('name', '')
        txt = self.get_argument('txt', '')
        secret = self.get_argument('secret', None)
        arguments = self.request.arguments
        if secret:
            state = STATE_SECRET
        else:
            state = STATE_ACTIVE
        if po:
            if name:
                po.name = name
                po.save()
            if txt:
                po.txt_set(txt)
            po_state_set(po, state)
        else:
            po = po_note_new(current_user_id, name, txt, state)

        if po:
            link = '/po/tag/%s'%id
            update_pic(arguments, current_user_id, po.id, id)
            mc_pic_id_list.delete('%s_%s'%(current_user_id, id))
        else:
            link = '/po/note'
        self.redirect(link)


@urlmap('/po/question')
class Question(LoginBase):
    def get(self, id=0):
        current_user_id = self.current_user_id
        po = po_can_edit(current_user_id, id)
        self.render(po=po, pic_list=pic_list_edit(current_user_id, id))

    def post(self, id=0):
        current_user_id = self.current_user_id
        po = po_can_edit(current_user_id, id)
        name = self.get_argument('name', '')
        txt = self.get_argument('txt', '')
        arguments = self.request.arguments
        if po:
            if name:
                po.name = name
                po.save()
            if txt:
                po.txt_set(txt)
        else:
            po = po_question_new(current_user_id, name, txt)

        if po:
            link = po.link
            update_pic(arguments, current_user_id, po.id, id)
            mc_pic_id_list.delete('%s_%s'%(current_user_id, id))
        else:
            link = '/po/question'
        self.redirect(link)
