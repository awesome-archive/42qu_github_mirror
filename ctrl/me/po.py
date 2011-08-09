# -*- coding: utf-8 -*-
from _handler import LoginBase
from ctrl._urlmap.me import urlmap
from model import reply
from model.cid import CID_WORD, CID_NOTE, CID_QUESTION, CID_ANSWER, CID_EVENT
from model.po import Po, po_rm, po_word_new, po_note_new, STATE_SECRET, STATE_ACTIVE, po_state_set
from model.po_pic import pic_list, pic_list_edit, mc_pic_id_list
from model.po_pos import po_pos_get, po_pos_set
from model.po_question import po_question_new, answer_word2note
from model.zsite import Zsite
from model.zsite_tag import zsite_tag_list_by_zsite_id_with_init, tag_id_by_po_id, zsite_tag_new_by_tag_id, zsite_tag_new_by_tag_name, zsite_tag_rm_by_tag_id, zsite_tag_rename
from zkit.jsdict import JsDict
from zkit.txt import cnenlen
from model.event import Event, event_init2to_review


def update_pic(form, user_id, po_id, id):
    pl = pic_list(user_id, id)
    for pic in pl:
        seq = pic.seq

        title = 'tit%s' % seq
        if title in form:
            title = form[title][0]
        else:
            title = ''

        align = 'pos%s' % seq
        if align in form:
            align = int(form[align][0])
            if align not in (-1, 0, 1):
                align = 0
        else:
            align = 0

        pic.title = title.strip()
        align = int(align)


        pic.align = align
        pic.po_id = po_id
        pic.save()


@urlmap('/po/word')
class PoWord(LoginBase):
    def post(self):
        current_user = self.current_user
        txt = self.get_argument('txt', '')
        if txt:
            po_word_new(current_user.id, txt)
        return self.redirect('/live')


def po_post(self):
    user_id = self.current_user_id
    name = self.get_argument('name', '')
    txt = self.get_argument('txt', '', strip=False).rstrip()
    secret = self.get_argument('secret', None)
    arguments = self.request.arguments
    if secret:
        state = STATE_SECRET
    else:
        state = STATE_ACTIVE
    po = self.po_save(user_id, name, txt, state)
    self_id = self.id
    if po:
        po_id = po.id
    else:
        po_id = 0
    if po or self_id == 0:
        update_pic(arguments, user_id, po_id, self_id)
        mc_pic_id_list.delete('%s_%s' % (user_id, self_id))
    return po


class PoBase(LoginBase):
    id = 0
    cid = None
    template = None
    po_save = None
    po_post = po_post

    def get(self):
        user_id = self.current_user_id
        self.render(
            'ctrl/me/po/po.htm',
            cid=self.cid,
            po=JsDict(),
            pic_list=pic_list_edit(user_id, 0),
        )

    def post(self):
        po = self.po_post()
        if po:
            if po.state == STATE_SECRET:
                link = po.link
            else:
                link = '/po/tag/%s' % po.id
        else:
            link = self.request.uri
        self.redirect(link)


@urlmap('/po/note')
class PoNote(PoBase):
    cid = CID_NOTE
    po_save = staticmethod(po_note_new)


@urlmap('/po/question')
class PoQuestion(PoBase):
    cid = CID_QUESTION
    po_save = staticmethod(po_question_new)


@urlmap('/po/edit/(\d+)')
class Edit(LoginBase):
    def po(self, user_id, id):
        po = Po.mc_get(id)
        if po:
            if po.can_admin(user_id):
                cid = po.cid
                if cid == CID_WORD and po.rid == 0:
                    return self.redirect(po.link)
                return po
            return self.redirect(po.link)
        return self.redirect('/')

    def get(self, id):
        user_id = self.current_user_id
        po = self.po(user_id, id)
        if po is None:
            return

        self.render(
            'ctrl/me/po/po.htm',
            po=po,
            cid=po.cid,
            pic_list=pic_list_edit(user_id, id)
        )

    def po_save(self, user_id, name, txt, state):
        po = self.po(user_id, self.id)
        if po is None:
            return
        if po.cid == CID_WORD:
            if cnenlen(txt) > 140:
                answer_word2note(po)
                po.txt_set(txt)
            else:
                po.name_ = txt
                po.save()
        else:
            if not po.rid and name:
                po.name_ = name
                po.save()
            if txt:
                po.txt_set(txt)
        if not (po.cid == CID_QUESTION and po.state == STATE_ACTIVE):
            po_state_set(po, state)
        return po

    po_post = po_post

    def post(self, id):
        user_id = self.current_user_id
        self.id = id

        po = self.po_post()

        cid = po.cid

        if cid == CID_EVENT:
            if event_init2to_review(po.rid):
                link = po.link
            else:
                link = po.link
        else:
            if cid == CID_WORD:
                link = po.link_question
            elif po.state == STATE_SECRET:
                link = po.link
            else:
                link = '/po/tag/%s' % id
        self.redirect(link)


@urlmap('/po/tag/(\d+)')
class Tag(LoginBase):
    def _po(self, id):
        current_user = self.current_user
        current_user_id = self.current_user_id
        po = Po.mc_get(id)
        if not po:
            self.redirect('/')
            return
        if not po.can_admin(current_user_id):
            self.redirect(po.link)
            return
        return po

    def get(self, id):
        po = self._po(id)
        if po:
            current_user_id = self.current_user_id
            tag_list = zsite_tag_list_by_zsite_id_with_init(current_user_id)
            po_id = po.id
            cid = po.cid
            tag_id = tag_id_by_po_id(current_user_id, po_id) or 1
            self.render(
                tag_list=tag_list,
                po=po,
                tag_id=tag_id,
            )

    def post(self, id):
        po = self._po(id)
        if po:
            tag_id = int(self.get_argument('tag'))
            name = self.get_argument('name', None)

            if not name and not tag_id:
                tag_id = 1

            if tag_id:
                zsite_tag_new_by_tag_id(po, tag_id)
            else:
                zsite_tag_new_by_tag_name(po, name)

            self.redirect(po.link_question)


