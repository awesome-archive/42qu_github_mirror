#!/usr/bin/env python
# -*- coding: utf-8 -*-
from _db import Model, McModel, McCache
from zkit.earth import place_name
from zkit.astrology import astrology
from zkit.attrcache import attrcache
from days import today_year

MARRY_ONE = 1

class UserInfo(McModel):
    @attrcache
    def place_home(self):
        return place_name(self.pid_home)

    @property
    def age(self):
        birthday = self.birthday
        if birthday:
            year = birthday//10000
            if year:
                return today_year() - year

    @property
    def astrology(self):
        return astrology(self.birthday)

def user_info_new(
    user_id,
    birthday=0,
    marry=0,
    pid_home=0,
    sex=0,
):
    o = UserInfo.get_or_create(id=user_id)
    if birthday:
        o.birthday = birthday
    if sex:
        o.sex = sex
    o.marry = marry
    if pid_home:
        o.pid_home = pid_home
    o.save()
    return o

if __name__ == "__main__":
    pass
#    n = UserInfo.get(10011475)
#    n.sex=2
#    n.marry=0
#    n.save()



