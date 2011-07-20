# -*- coding: utf-8 -*-
from _handler import Base, LoginBase, XsrfGetBase
from ctrl._urlmap.main import urlmap
from model.zsite_tag import ZsiteTag
from model.zsite import Zsite

@urlmap('/')
class Index(Base):
    def get(self):
        current_user = self.current_user
        if current_user:
            self.redirect(
                '%s/live'%current_user.link
            )
        else:
            self.redirect('/login')


@urlmap('/tag/(\d+)')
class Tag(Base):
    def get(self, id, n=1):
        tag = ZsiteTag.mc_get(id)
        tag_zsite = Zsite.mc_get(tag.zsite_id)
        return self.redirect('%s/tag/%s'%(tag_zsite.link, id))
