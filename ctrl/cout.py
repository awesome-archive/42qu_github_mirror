#!/usr/bin/env python
# -*- coding: utf-8 -*-
import _handler
from zweb._urlmap import urlmap
from model.mblog import mblog_word_new, mblog_note_new, MBLOG_STATE_SECRET, MBLOG_STATE_ACTIVE



@urlmap("/cout/word")
class Word(_handler.LoginBase):
    def post(self):
        current_user = self.current_user
        txt = self.get_argument('txt', '')
        if txt.strip():
            mblog_word_new(current_user.id, txt)
        return self.redirect("/news")
