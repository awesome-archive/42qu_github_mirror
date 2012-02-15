#coding:utf-8
import _env
from os.path import abspath, dirname, join
from json import loads
from urllib import quote
from zkit.pprint import pformat, pprint
from operator import itemgetter
from zkit.spider import Rolling, Fetch, MultiHeadersFetch, GSpider, NoCacheFetch
from zkit.bot_txt import txt_wrap_by, txt_wrap_by_all
from zkit.howlong import HowLong
from zhihu_question_id import QUESTION_ID_SET
from zkit.htm2txt import unescape

RESULT = []

def zhihu_question_parser(html, url):
    name = txt_wrap_by(
        '<title>',
        ' - 知乎</title>',
        html
    )
    name = unescape(name)
    if  '<h3>邀请别人回答问题</h3>' in html:
        answer_count = txt_wrap_by('<span id="xhrw">', ' 个答案</span>', html)
    else:
        answer_count = txt_wrap_by('<h3 style="margin: 0 0 5px;">', ' 个答案</', html)

    tag = map(unescape, txt_wrap_by('<a class="xjl" href="javascript:;">', '</a>', html))

    RESULT.append((int(answer_count), url, name, tag))

    print how_long.again(), how_long.remain, how_long.done

def zhihu_question_url():
    for i in QUESTION_ID_SET:
        yield zhihu_question_parser, 'http://www.zhihu.com/question/%s'%i

how_long = HowLong(len(QUESTION_ID_SET))

def zhihu_topic_title(url , html):
    if '请输入图中的数字：' in html:
        print '请输入图中的数字：'
        return

    r = '<h3>邀请别人回答问题</h3>' in html
    if not r:
        r = '>已有帐号了？请登录</h' in html

    return r

def spider(url_list):
#    fetcher = MultiHeadersFetch(  headers=tuple( { 'Cookie': i } for i in COOKIE))
    fetcher = Fetch(
        '/tmp',
    #    tuple( { 'Cookie': i } for i in COOKIE),
        {},
        0, #2.6,
        zhihu_topic_title
    )
    spider = Rolling( fetcher, url_list )

    debug = False
    debug = True

    spider_runner = GSpider(spider, workers_count=3, debug=debug)
    spider_runner.start()


spider(zhihu_question_url())
RESULT.sort(key=lambda x:-x[0])

with open('zhihu_question_order_by_answer.py',"w") as result:
    result.write(pformat(RESULT))
