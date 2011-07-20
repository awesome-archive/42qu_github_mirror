#!/usr/bin/env python
#coding:utf-8


import _handler
from _urlmap import urlmap
from model.user_mail import user_id_by_mail, mail_by_user_id
from model.user_auth import mail_password_verify
from model.api_client import api_session_new
from model.api_user import json_info
from model.follow import follow_id_list_by_from_id, follow_id_list_by_to_id, follow_count_by_to_id, follow_count_by_from_id, follow_rm, follow_new
from model.oauth2 import oauth_access_token_new, oauth_refresh_token_new
from model.user_session import id_binary_decode


@urlmap('/user/info/mail')
class InfoMail(_handler.OauthBase):
    def get(self):
        mail = self.get_argument('mail')
        user_id = user_id_by_mail(mail)
        if user_id:
            data = json_info(user_id)
            self.finish(data)
        else:
            self.finish({
                'error':'user_dont_exist!'
                })


@urlmap('/user/oauth/login')
class Login(_handler.OauthBase):
    def get(self):
        mail = self.get_argument('mail', None)
        passwd = self.get_argument('passwd', None)
        auth = self.get_argument('client_secret', None)
        client_id = self.get_argument('client_id', None)

        if mail_password_verify(mail, passwd):
            user_id = user_id_by_mail(mail)
            id, access_token = oauth_access_token_new(client_id, user_id)
            refresh_token = oauth_refresh_token_new(client_id, id)
            return self.finish({
                        'access_token': access_token,
                        'refresh_token': refresh_token,
                        "expires_in": 87063,
                        "scope": "basic"
                   })
        else:
            self.finish(
                    {
                        'error_code':1
                        }
                    )



@urlmap('/user/info/id')
class InfoId(_handler.OauthBase):
    def get(self):
        user_id = self.get_argument('user_id')
        data = json_info(user_id)
        self.finish(data)


@urlmap('/user/follower')
class UserFollower(_handler.OauthBase):
    def get(self):
        user_id = self.get_argument('user_id')
        limit = int(self.get_argument('limit', 25))
        offset = int(self.get_argument('offset', 0))
        if limit > 100:
            limit = 100
        ids = follow_id_list_by_to_id(user_id, limit, offset)
        total_num = follow_count_by_to_id(user_id)
        data = {}
        data['follower_list'] = list(ids)
        data['total_num'] = total_num
        self.finish(data)


@urlmap('/user/following')
class UserFollowing(_handler.OauthBase):
    def get(self):
        user_id = self.get_argument('user_id')
        ids = follow_id_list_by_from_id(user_id)
        total_num = follow_count_by_from_id(user_id)
        data = {}
        data['total_num'] = total_num
        data['following_list'] = list(ids)
        self.finish(data)


@urlmap('/user/follow')
class UserFollow(_handler.OauthAccessBase):
    def get(self):
        user_id = self.current_user_id
        follow_id = int(self.get_argument('id'))
        res = follow_new(user_id, follow_id)
        self.finish({
            'status':res
        })


@urlmap('/user/follow/rm')
class UserFollowRm(_handler.OauthAccessBase):
    def get(self):
        user_id = self.current_user_id
        unfollow_id = int(self.get_argument('id'))
        res = follow_rm(user_id, unfollow_id)
        self.finish({
            'status':res
        })
