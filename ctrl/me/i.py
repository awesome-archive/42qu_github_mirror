# -*- coding: utf-8 -*-
from _handler import LoginBase, XsrfGetBase
from ctrl._urlmap.me import urlmap
from zkit.pic import picopen
from zkit.jsdict import JsDict
from model.motto import motto as _motto
from model.user_info import UserInfo, user_info_new
from model.namecard import namecard_get, namecard_new
from model.ico import ico_new, ico_pos, ico_pos_new
from model.zsite_url import url_by_id, url_new, url_valid, RE_URL
from model.user_mail import mail_by_user_id, user_mail_new
from model.txt import txt_get, txt_new
from model.mail_notice import CID_MAIL_NOTICE_ALL, mail_notice_all, mail_notice_set
from model.zsite import zsite_name_edit, user_can_reply, ZSITE_STATE_VERIFY, ZSITE_STATE_ACTIVE, ZSITE_STATE_WAIT_VERIFY, ZSITE_STATE_APPLY
from model.user_auth import user_password_new, user_password_verify
from cgi import escape
from urlparse import parse_qs, urlparse
from model.zsite_link import OAUTH2NAME_DICT, link_list_save, link_id_name_by_zsite_id, link_id_cid, link_by_id, OAUTH_LINK_DEFAULT, link_list_cid_by_zsite_id
from model.oauth2 import oauth_access_token_by_user_id, oauth_token_rm_if_can, OauthClient
from config import SITE_URL, SITE_DOMAIN
from model.oauth import OAUTH_DOUBAN, OAUTH_SINA, OAUTH_TWITTER, OAUTH_QQ, oauth_by_zsite_id, oauth_rm_by_oauth_id, OAUTH_SYNC_TXT, linkify
from model.zsite import Zsite
from collections import defaultdict
from model.sync import sync_state_set, sync_all, sync_follow_new, SYNC_CID
from zkit.errtip import Errtip
from model.search_zsite import search_new
from model.invite_email import invite_user_id_list_by_cid, CID_MSN, CID_QQ, invite_invite_email_list_by_cid, invite_message_new
from model.follow import follow_id_list_by_from_id, follow_new
from zkit.txt import EMAIL_VALID
from model.verify import verify_mail_new
from model.cid import CID_VERIFY_LOGIN_MAIL
from model.user_school import user_school_json

def _upload_pic(files, current_user_id):
    error_pic = None
    if 'pic' in files:
        pic = files['pic'][0]['body']
        pic = picopen(pic)
        if pic:
            ico_new(current_user_id, pic)
            error_pic = False
        else:
            error_pic = '图片格式有误'
    return error_pic



class LinkEdit(LoginBase):

    def get(self):
        zsite_id = self.zsite_id
        link_list, link_cid = link_list_cid_by_zsite_id(zsite_id)
        return self.render(
            link_list=link_list,
            link_cid=link_cid
        )

    def save(self):
        zsite_id = self.zsite_id

        arguments = parse_qs(self.request.body, True)
        link_cid = []
        link_kv = []
        for cid, link in zip(arguments.get('cid'), arguments.get('link')):
            cid = int(cid)
            name = OAUTH2NAME_DICT[cid]
            link_cid.append((cid, name, linkify(link, cid)))


        for id, key, value in zip(
            arguments.get('id'),
            arguments.get('key'),
            arguments.get('value')
        ):
            id = int(id)
            link = linkify(value)

            link_kv.append((id, key.strip() or urlparse(link).netloc, link))

        link_list_save(zsite_id, link_cid, link_kv)



class CareerEdit(LoginBase):
    def get(self):
        from model.career import CID_JOB, CID_EDU, career_list
        current_user_id = self.current_user_id
        self.render(
            job_list=career_list(current_user_id, CID_JOB),
            school_list=user_school_json(current_user_id),
        )

    def save(self):
        from model.career import CID_TUPLE, career_list_set
        current_user_id = self.current_user_id
        #Tornado会忽略掉默认为空的参数
        arguments = parse_qs(self.request.body, True)

        for cid, prefix in CID_TUPLE:
            id = arguments.get('%s_id' % prefix, [])
            unit = arguments.get('%s_unit' % prefix, [])
            title = arguments.get('%s_title' % prefix, [])
            txt = arguments.get('%s_txt' % prefix, [])
            begin = arguments.get('%s_begin' % prefix, [])
            end = arguments.get('%s_end' % prefix, [])
            career_list_set(id, current_user_id, unit, title, txt, begin, end, cid)

        search_new(current_user_id)


class PicEdit(LoginBase):
    def get(self):
        current_user_id = self.current_user_id
        pos = ico_pos.get(current_user_id)
        self.render(pos=pos)

    def save(self):
        current_user_id = self.current_user_id
        files = self.request.files
        pos = self.get_argument('pos', '')
        if pos:
            ico_pos_new(current_user_id, pos)
        error_pic = _upload_pic(files, current_user_id)
        return error_pic



class UserInfoEdit(LoginBase):
    def get(self):
        current_user_id = self.current_user_id
        current_user = self.current_user
        motto = _motto.get(current_user_id)
        txt = txt_get(current_user_id)
        o = UserInfo.mc_get(current_user_id) or JsDict()
        c = namecard_get(current_user_id) or JsDict()
        self.render(
            name=current_user.name,
            motto=motto,
            txt=txt,
            birthday='%08d' % (o.birthday or 0),
            marry=o.marry,
            pid_home=o.pid_home or 0,
            pid_now=c.pid_now or 0,
            sex=o.sex
        )

    def save(self):
        current_user_id = self.current_user_id

        name = self.get_argument('name', None)
        if name:
            zsite_name_edit(current_user_id, name)

        motto = self.get_argument('motto', None)
        if motto:
            _motto.set(current_user_id, motto)

        txt = self.get_argument('txt', '')
        if txt:
            txt_new(current_user_id, txt)

        birthday = self.get_argument('birthday', '0')
        birthday = int(birthday)
        marry = self.get_argument('marry', '')
        pid_home = self.get_argument('pid_home', '1')
        pid_now = self.get_argument('pid_now', '1')
        try:
            pid_now = int(pid_now)
        except ValueError:
            pid_now = 0
        try:
            pid_home = int(pid_home)
        except ValueError:
            pid_home = 0

        marry = int(marry)
        if marry not in (1, 2, 3):
            marry = 0

        o = user_info_new(current_user_id, birthday, marry, pid_home)
        if pid_now:
            c = namecard_get(current_user_id)
            if c:
                c.pid_now = pid_now
                c.save()
            else:
                c = namecard_new(current_user_id, pid_now=pid_now)

        if not o.sex:
            sex = self.get_argument('sex', 0)
            if sex and not o.sex:
                sex = int(sex)
                if sex not in (1, 2):
                    sex = 0
                if sex:
                    if o:
                        o.sex = sex
                        o.save()
                    else:
                        user_info_new(current_user_id, sex=sex)

        search_new(current_user_id)


@urlmap('/i/pic')
class Pic(PicEdit):
    def post(self):
        error_pic = self.save()
        if error_pic:
            self.render(error_pic=error_pic)
        else:
            self.get()

@urlmap('/i/url')
class Url(LoginBase):
    def prepare(self):
        super(Url, self).prepare()
        if not self._finished:
            user = self.current_user
            current_user_id = self.current_user_id
            link = self.current_user.link
            if user.state <= ZSITE_STATE_APPLY:
                self.redirect(link+'/i/verify')
            elif url_by_id(current_user_id):
                self.redirect(link)

    def get(self):
        self.render(url='')

    def post(self):

        current_user_id = self.current_user_id
        url = self.get_argument('url', None)
        if url:
            if url_by_id(current_user_id):
                error_url = '个性域名设置后不能修改'
            else:
                error_url = url_valid(url)
            if error_url is None:
                url_new(current_user_id, url)
                self.redirect(SITE_URL)
        else:
            error_url = '个性域名不能为空'
        self.render(
            error_url=error_url,
            url=url
        )


@urlmap('/i/verify')
class Verify(LoginBase):
    def prepare(self):
        super(Verify, self).prepare()
        if not self._finished:
            current_user = self.current_user
            current_user_id = self.current_user_id
            state = current_user.state
            if state >= ZSITE_STATE_VERIFY:
                return self.redirect('/')
            elif state <= ZSITE_STATE_APPLY:
                return self.redirect('/auth/verify/sended/%s' % current_user_id)

    def post(self):
        current_user = self.current_user
        current_user.state = ZSITE_STATE_WAIT_VERIFY
        current_user.save()
        return self.get()

    def get(self):
        self.render()


@urlmap('/i/career')
class Career(CareerEdit):
    def post(self):
        self.save()
        self.get()


@urlmap('/i')
class Index(UserInfoEdit):
    def post(self):
        files = self.request.files
        current_user_id = self.current_user_id
        self.save()
        self.get()


@urlmap('/i/link')
class Link(LinkEdit):
    def post(self):
        self.save()
        self.get()


class NameCardEdit(object):
    def get(self):
        current_user = self.current_user
        current_user_id = self.current_user_id
        c = namecard_get(current_user_id) or JsDict()
        self.render(
            name=c.name or current_user.name,
            phone=c.phone,
            mail=c.mail or mail_by_user_id(current_user_id),
            pid_now=c.pid_now or 0,
            address=c.address,
        )

    def save(self):
        current_user = self.current_user
        current_user_id = self.current_user_id
        pid_now = self.get_argument('pid_now', '1')
        name = self.get_argument('name', '')
        phone = self.get_argument('phone', '')
        mail = self.get_argument('mail', '')
        address = self.get_argument('address', '')

        pid_now = int(pid_now)

        if pid_now or name or phone or mail or address:
            c = namecard_new(
                current_user_id, pid_now, name, phone, mail, address
            )
            return c


@urlmap('/i/namecard')
class Namecard(NameCardEdit, LoginBase):
    def post(self):
        self.save()
        self.get()

@urlmap('/i/mail/notice')
class MailNotice(LoginBase):
    def get(self):
        user_id = self.current_user_id
        self.render(
            mail_notice_all=mail_notice_all(user_id)
        )

    def post(self):
        user_id = self.current_user_id
        for cid in CID_MAIL_NOTICE_ALL:
            state = self.get_argument('mn%s' % cid, None)
            mail_notice_set(user_id, cid, state)
        self.get()

@urlmap('/i/mail/notice')
class MailNotice(LoginBase):
    def get(self):
        user_id = self.current_user_id
        self.render(
            mail_notice_all=mail_notice_all(user_id)
        )

    def post(self):
        user_id = self.current_user_id
        for cid in CID_MAIL_NOTICE_ALL:
            state = self.get_argument('mn%s' % cid, None)
            mail_notice_set(user_id, cid, state)
        self.get()

@urlmap('/i/invite')
class Invite(LoginBase):
    def get(self):
        self.render()


@urlmap('/i/invite/login/(\d+)')
class InviteLogin(LoginBase):
    def get(self, cid=CID_MSN):
        if cid != CID_QQ:
            self.render(cid=cid)
        else:
            self.render('/ctrl/me/i/import_qq.htm')

@urlmap('/i/invite/show')
@urlmap('/i/invite/show/(\d+)')
class InviteShow(LoginBase):
    def get(self, cid=CID_MSN):
        uid = self.current_user_id
        user_id_list = invite_user_id_list_by_cid(uid, cid)
        follow_id_list = follow_id_list_by_from_id(uid)
        user_id_list = set(user_id_list) - set(follow_id_list)
        if not user_id_list:
            return self.redirect('/i/invite/email/%s'%cid)
        self.render(cid=cid, user_id_list=user_id_list)

    def post(self, cid=CID_MSN):
        user_id = self.current_user_id
        fid_list = self.get_argument('follow_id_list', None)
        if fid_list:
            fid_list = fid_list.split(' ')
            for i in Zsite.mc_get_list(fid_list):
                if i.id != user_id:
                    follow_new(user_id, i.id)

        self.redirect('/i/invite/email/%s'%cid)

@urlmap('/i/invite/email')
@urlmap('/i/invite/email/(\d+)')
class InviteEmail(LoginBase):
    def get(self, cid=CID_MSN):
        emails = invite_invite_email_list_by_cid(self.current_user_id, cid)
        if not emails:
            return self.render('ctrl/me/i/invite.htm', success=True)

        self.render(emails=emails, cid=cid)

    def post(self, cid=CID_MSN):
        emails = self.get_arguments('mails', None)
        mail_txt = self.get_argument('mail_txt', None)
        if emails:
            invite_message_new(self.current_user_id, emails, mail_txt)
        self.render('ctrl/me/i/invite.htm', success=True)

@urlmap('/i/account/mail/success')
class AccountMailSuccess(LoginBase):
    def get(self):
        self.render()


@urlmap('/i/account/mail')
class AccountMail(LoginBase):
    def get(self):
        errtip = Errtip()
        self.render(errtip=errtip)

    def post(self):
        errtip = Errtip()
        user_id = self.current_user_id
        password = self.get_argument('password', None)
        mail = self.get_argument('mail', None)
        if not mail:
            errtip.mail = '请输入邮箱'
        elif not EMAIL_VALID.match(mail):
            errtip.mail = '邮件格式不正确'

        if not password:
            errtip.password = '请输入密码'
        elif not user_password_verify(user_id, password):
            errtip.password = '密码有误'
            password = ''

        if not errtip:
            from model.user_mail import user_mail_new, user_mail_by_state, MAIL_VERIFIED, user_mail_active_by_user_id
            if mail in user_mail_by_state(user_id, MAIL_VERIFIED):
                user_mail_active_by_user_id(user_id, mail)
                return self.redirect('/i/account/mail/success')

            if user_mail_new(user_id, mail):
                verify_mail_new(
                    user_id, self.current_user.name, mail, CID_VERIFY_LOGIN_MAIL
                )
            else:
                errtip.mail = '该邮箱已经注册'

        self.render(mail=mail, errtip=errtip, password=password)

@urlmap('/i/account')
class Account(LoginBase):
    def get(self):
        self.render()

    def post(self):
        user_id = self.current_user_id
        password0 = self.get_argument('password0', None)
        password = self.get_argument('password', None)
        password2 = self.get_argument('password2', None)
        success = None
        error_password = None
        if all((password0, password, password2)):
            if password == password2:
                if user_password_verify(user_id, password0):
                    user_password_new(user_id, password)
                    success = True
                else:
                    error_password = '密码有误。忘记密码了？<a href="/auth/password/reset/%s">点此找回</a>' % escape(mail_by_user_id(user_id))
            else:
                error_password = '两次输入密码不一致'
        else:
            error_password = '请输入密码'
        self.render(
            success=success,
            error_password=error_password
        )

@urlmap('/i/invoke')
class Invoke(LoginBase):
    def get(self):
        user_id = self.current_user_id
        li = oauth_access_token_by_user_id(user_id)
        OauthClient.mc_bind(li, 'client', 'client_id')
        Zsite.mc_bind(li, 'user', 'user_id')
        self.render(li=li)

@urlmap('/i/invoke/rm/(\d+)')
class InvokeRm(XsrfGetBase):
    def get(self, id):
        if id:
            user_id = self.current_user_id
            oauth_token_rm_if_can(id, user_id)
            self.redirect('/i/invoke')

@urlmap('/i/bind/(\d+)')
class BindItem(LoginBase):
    def get(self, id):
        user_id = self.current_user_id
        return self.render(
            id=id,
            sync_all=sync_all(user_id, id),
        )

    def post(self, id):
        user_id = self.current_user_id
        cid_list = self.get_arguments('cid')
        cid_list = set(map(int, cid_list))
        for i in SYNC_CID:
            if i in cid_list:
                state = 1
            else:
                state = 0
            sync_state_set(user_id, i, state, id)

        self.redirect('/i/bind')


@urlmap('/i/bind')
class Bind(LoginBase):
    def get(self):
        user_id = self.current_user_id

        app_dict = defaultdict(list)

        for app_id , oauth_id in oauth_by_zsite_id(user_id):
            app_dict[app_id].append(oauth_id)

        self.render(
             app_dict=app_dict
        )


@urlmap('/i/binded/(\d+)')
class Binded(LoginBase):
    def get(self, cid):
        self.render(cid=cid, txt=OAUTH_SYNC_TXT)

    def post(self, cid):
        sync_txt = self.get_argument('sync_txt', None)
        txt = self.get_argument('weibo', None)

        user_id = self.current_user_id

        flag = 0
        if sync_txt:
            flag |= 0b10

        sync_follow_new(user_id, flag, cid, txt)

        url = 'http://rpc.%s/oauth/%s'%(SITE_DOMAIN, cid)

        self.redirect(url)


@urlmap('/i/bind/oauth_rm/(\d+)')
class BindOauthRm(XsrfGetBase):
    def get(self, id):
        if id:
            oauth_rm_by_oauth_id(id)
        self.redirect('/i/bind')

