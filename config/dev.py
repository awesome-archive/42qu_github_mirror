#!/usr/bin/env python
# -*- coding: utf-8 -*-
import zpage_host
SITE_DOMAIN = "42qu.info"
zpage_host.SITE_DOMAIN = SITE_DOMAIN
zpage_host.SITE_URL = "http://%s"%SITE_DOMAIN
zpage_host.SITE_DOMAIN_SUFFIX = ".%s"%(SITE_DOMAIN)
import getpass
LOCAL_SETTINGS = 'dev_%s' % getpass.getuser()
try:
    __import__(LOCAL_SETTINGS)
except ImportError, e:
    print e
