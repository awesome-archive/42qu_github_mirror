#!/usr/bin/env python
# -*- coding: utf-8 -*-
from _db import Model, McModel
from hashlib import sha256
from user_mail import user_mail_new, user_id_by_mail
from zsite import zsite_new_user, Zsite
from binascii import hexlify

def hash_password(id, password):
    return sha256('%s%s'%(password, id)).digest()

class UserPassword(Model):
    pass

def user_password_sha256(user_id):
    password = UserPassword.get(id=user_id)
    return hexlify(password.password)

def user_password_new(user_id, password):
    if password is not None:
        o = UserPassword.get_or_create(id=user_id)
        o.password = hash_password(user_id, password)
        o.save()

def user_password_verify(user_id, password):
    p = UserPassword.get(user_id)
    if p is None:
        user_password_new(user_id, password)
        return True
    if p.password == hash_password(user_id, password):
        return True

def user_new_by_mail(mail, password=None):
    name = mail.split('@', 1)[0].split('+', 1)[0]
    zsite = zsite_new_user(name)
    user_id = zsite.id
    user_mail_new(user_id, mail)
    user_password_new(user_id, password)
    return user_id

if __name__ == '__main__':
    print user_password_sha256(1)
    

