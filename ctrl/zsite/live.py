#!/usr/bin/env python
# -*- coding: utf-8 -*-

from _handler import Base, LoginBase, XsrfGetBase
from ctrl._urlmap.zsite import urlmap

@urlmap('/live')
class Index(LoginBase):
    def get(self):
        user_id = self.current_user_id
        return self.render()
