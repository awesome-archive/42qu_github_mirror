#!/usr/bin/env python
#coding:utf-8
import _env
import re
from cgi import escape
from config import SITE_DOMAIN
RE_LINK = re.compile(
r'((?:https?://[\w\-]+\.)'
r'[\w\-.%/=+#:~!,\'\*\^@]+'
r'(?:\?[\w\-.%/=+#:~!,\'\*&$@]*)?)'
)
RE_SPACE = re.compile(""" ( +)""")
RE_AT = re.compile(r'(\s|^)@([^@\(\)\s]+(?:\s+[^@\(\)\s]+)*)\(([a-zA-Z0-9][a-zA-A0-9\-]{,31}|-\d{8,10})\)(?=\s|$)')
RE_BOLD = re.compile(r'\*{2}([^\*].*?)\*{2}')

YOUKU = """<embed src="http://player.youku.com/player.php/sid/%s/v.swf" allowFullScreen="true" quality="high" width="480" height="400" align="middle" allowScriptAccess="always" type="application/x-shockwave-flash"></embed>""" 


def replace_space(match):
    return ' '+len(match.groups()[0])*'&nbsp;'

def replace_link(match):
    #p, g = match.groups()
    #if p in ('"', ">") or p.isalnum():
    #    return "%s%s"%(p, g)
    #else:
    g = match.groups()[0]
    if g.startswith('http://v.youku.com/v_show/id_'):
        g = g[29:g.rfind('.')]
        return YOUKU%g
    else:
        return """<a target="_blank" href="%s" rel="nofollow">%s</a>""" %(g, g)

def replace_bold(match):
    txt = match.groups()[0]
    return '<b>%s</b>' % txt.strip()

def txt_withlink(s):
    s = escape(s)
    s = RE_BOLD.sub(replace_bold, s)
    s = RE_LINK.sub(replace_link, s)
    s = RE_AT.sub(replace_at, s)
    return s

def txt2htm_withlink(s):
    s = escape(s)
    s = s.replace('\n', '\n<br>')
    s = RE_LINK.sub(replace_link, s)
    s = RE_SPACE.sub(replace_space, s)
    return s

def replace_at(match):
    prefix, name, url = match.groups()
    return '%s@<a target="_blank" href="//%s.%s">%s</a>' % (prefix, url, SITE_DOMAIN, name)


if __name__ == '__main__':
    print txt_withlink("""

**二**
""")
