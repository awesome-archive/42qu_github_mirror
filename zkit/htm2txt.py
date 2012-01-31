# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup, Tag, NavigableString
import htmlentitydefs, re
from upyun import upyun_rsspic,upyun_fetch_pic
BLOD_LINE = re.compile(r"^\s*\*\*[\r\n]+", re.M)

_char = re.compile(r'&(\w+?);')
_dec = re.compile(r'&#(\d{2,4});')
_hex = re.compile(r'&#x(\d{2,4});')
RE_TU = re.compile(r"^\s*图:\d+\s*$")

def _char_unescape(m, defs=htmlentitydefs.entitydefs):
    try:
        return defs[m.group(1)]
    except KeyError:
        return m.group(0)


import re, htmlentitydefs
def unescape(s):
    # First convert alpha entities (such as &eacute;)
    # (Inspired from http://mail.python.org/pipermail/python-list/2007-June/443813.html)
    def entity2char(m):
        entity = m.group(1)
        if entity in htmlentitydefs.name2codepoint:
            return unichr(htmlentitydefs.name2codepoint[entity])
        return u" "  # Unknown entity: We replace with a space.
    t = re.sub(u'&(%s);' % u'|'.join(htmlentitydefs.name2codepoint), entity2char, s)

    # Then convert numerical entities (such as &#233;)
    t = re.sub(u'&#(\d+);', lambda x: unichr(int(x.group(1))), t)

    # Then convert hexa entities (such as &#x00E9;)
    return re.sub(u'&#x(\w+);', lambda x: unichr(int(x.group(1), 16)), t)


BLOCK_BOLD = set([
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'h6',
])

BLOCK = set([
    'form',
    'hr',
    'div',
    'table',
    'tr',
    'li',
    'pre',
    'p',
])

BOLD = set([
    'b',
    'strong',
    'i',
    'em',
])

PASS = set([
    'span',
    'font',
])

def htm2txt(htm):
    htm = htm.replace(u'*', u'﹡')

    soup = BeautifulSoup(htm)


    def soup2txt_recursion(soup):
        li = []
        for i in soup:

            if isinstance(i, NavigableString):

                li.append(i.string)

            else:

                name = i.name
                if name == 'a':
                    s = soup2txt_recursion(i)
                    ss = s.rstrip()
                    if not RE_TU.match(ss.lstrip().encode('utf-8')):
                        li.append(ss)
                        href = i.get('href')
                        if href and href.startswith('http'):
                            li.append('[[%s]]'%href)
                        li.append(s[len(ss):])
                    else:
                        li.append(s)
                elif name == 'img':
                    src = i.get('src')
                    if src:
                        #img_url = upyun_fetch_pic(src)
                        li.append(u'\n图:%s \n' % src)
                else:
                    s = soup2txt_recursion(i)

                    if name in BLOCK_BOLD:
                        if '\n' not in s:
                            li.append(u'\n**%s**\n' % s)
                        else:
                            li.append(s)
                    elif name in BLOCK:
                        li.append(u'\n%s\n' % s)
                    elif name in BOLD and '**' not in s and '\n' not in s:
                        li.append(u'**%s**' % s)
                    else:
                        li.append(s)

        return u''.join(li)

    s = soup2txt_recursion(soup)
    s = unescape(s.strip())
    txt = '\n\n'.join(filter(bool, [i.strip() for i in s.splitlines()]))
    txt = BLOD_LINE.sub('**', txt)
    return txt 

if __name__ == '__main__':
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')
    print htm2txt("""
<pre style="font-family:Verdana;font-size:14px;white-space:pre-wrap;word-wrap:break-word;line-height:27px;"><span class="cc"><table><tr><td><img src="http://27.media.tumblr.com/tumblr_lj8noxh3ee1qixe63o1_250.jpg" alt=""/></td></tr><tr><td align='center' class="wr pl"></td></tr></table></span>
如果<h1><h2>某一天</h2></h1>，
你身上多了一个“恢复出厂设置”按钮，一按身体和记忆一切归为出生时。 你会去按它吗？</pre>
""")
    #print unescape("""<option value='&#20013;&#22269;&#35821;&#35328;&#25991;&#23398;&#31995;'>&#20013;&#22269;&#35821;&#35328;&#25991;&#23398;&#31995;</option>""")

