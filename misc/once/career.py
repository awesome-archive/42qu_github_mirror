#!/usr/bin/env python
# -*- coding: utf-8 -*-
import _env
from model.zsite_list import ZsiteList
from model.zsite import Zsite
id_list = ZsiteList.where( owner_id=0, state=1).col_list(col='zsite_id')


for n,i in enumerate(id_list):
    z = Zsite.mc_get(i)
    if z:
        title, unit = z.career
        if not title and not unit:
            print n,' ',z.name
            print "http://god.42qu.com/zsite/%s"%i
            print "http://god.42qu.com/zsite/avatar/%s?next=%s/i/career"%(i,z.link)
            print ""
