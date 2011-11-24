#coding:utf-8
from ctrl._urlmap.j import urlmap
from _handler import JLoginBase
from model.zsite_member import zsite_member_can_admin, zsite_member_rm
from model.zsite_url import zsite_by_domain, url_by_digit_domain
from model.cid import CID_COM
from model.po_review import po_review_show_new, po_review_show_rm
from model.com_apply import com_apply_rm, com_apply_accept

class AdminBase(JLoginBase):
    def prepare(self):
        super(AdminBase, self).prepare()

        request = self.request
        host = request.host
        zsite = zsite_by_domain(host)
        if zsite is None:
            self.zsite_id = 0
        else:
            self.zsite_id = zsite.id
        self.zsite = zsite

        zsite = self.zsite
        if not zsite.cid == CID_COM or not zsite_member_can_admin(self.zsite_id, self.current_user_id):
            self.finish('{}')

@urlmap('/j/member/invite/rm/(\d+)')
class MemberInviteRm(AdminBase):
    def get(self, id):
        zsite_id = self.zsite_id
        current_user_id = self.current_user_id
        id = int(id)
        if id != current_user_id:
            zsite_member_rm(zsite_id, id)
        self.finish('{}')
    post = get

@urlmap('/j/member/rm/(\d+)')
class MemberRm(AdminBase):
    def post(self, id):
        com_id = self.zsite_id
        if id and zsite_id_count_by_member_admin(com_id) > 1:
            zsite_member_rm(com_id, id)
        self.finish('{}')

@urlmap('/j/review/show/rm/(\d+)')
class ReviewShowRm(AdminBase):
    def get(self, id):
        zsite_id = self.zsite_id
        po_review_show_rm(zsite_id, id)
        self.finish('{}')

@urlmap('/j/review/show/new/(\d+)')
class ReviewShowNew(AdminBase):
    def get(self, id):
        zsite_id = self.zsite_id
        po_review_show_new(zsite_id, id)
        self.finish('{}')

@urlmap('/j/com/apply/rm/(\d+)')
class MemberApplyRm(AdminBase):
    def post(self, id):
        com_apply_rm(id, com_id, self.current_user_id)
        self.finish('{}')

@urlmap('/j/com/apply/new/(\d+)')
class MemberApplyNew(AdminBase):
    def get(self, state, id):
        com_apply_accept(id, com_id, self.current_user_id)
        self.finish('{}')



