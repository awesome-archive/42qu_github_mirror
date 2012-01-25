#coding:utf-8

import _env
from zkit.spider import Rolling, Fetch, NoCacheFetch, GSpider
from zkit.bot_txt import txt_wrap_by_all
from json import loads
import sys
from time import time
from kvdb import KvDb

DOUBAN_REC_CID = set("""artist
artist_video
back
book
discussion
doulist
entry
event
group
movie
music
note
online
photo
photo_album
review
site
topic
url""".split())

kvdb = KvDb()

db = kvdb.open_db("rec.kch")
fetched = kvdb.open_db("rec_fetched.kch")
fetch_cache = kvdb.open_db( "fetch_cache.kch")

API_KEY = "00d9bb33af90bf5c028d319b0eb23e14"

URL_REC = "http://api.douban.com/people/%%s/recommendations?alt=json&apikey=%s"%API_KEY

URL_LIKE = "http://www.douban.com/j/like?tkind=%s&tid=%s"

URL_USER_INFO = "http://api.douban.com/people/%%s?alt=json&apikey=%s"%API_KEY

NOW = int(time()/60)

def user_id_list_by_like(data, url):
    for i in loads(data):
        id = int(i['id'])
        uid = i['uid']

        if not uid.isdigit():
            db[uid] = id

        url = URL_REC%id

        if id not in fetched:
            fetched[id] = NOW
            yield user_id_list_by_rec, url , id, 1
        else:
            yield user_id_list_by_rec, url , id

def fetch_id_by_uid(data, url, uid):
    data = loads(data)
    id = data[u'id'][u'$t'].rsplit("/",1)[1]
    db[uid] = id
    if id not in fetched:
        fetched[id] = NOW
        yield user_id_list_by_rec, URL_REC%id , id, 1
        
    
def fetch_if_new(uid):
    if not uid.isdigit() and uid not in db:
        return fetch_id_by_uid, URL_USER_INFO%uid, uid


def user_id_list_by_rec(data, url, id, start_index=None):
    print url

    data = loads(data)
    entry_list = data['entry']
    if entry_list:
        for i in entry_list:
            title = i[u'content'][u'$t'].replace("\r", " ").replace("\n", " ").strip()
            attribute = i[u'db:attribute']
            cid = str(attribute[0][u'$t'])
            if cid in DOUBAN_REC_CID:
                if cid == "note":
                    t = [i.split('">', 1) for i in txt_wrap_by_all('<a href="', '</a>', title)]
                    uid_url = t[0][0]
                    if uid_url.startswith("http://www.douban.com/people/"):
                        uid = uid_url.strip("/").rsplit("/", 1)[1]
                        yield fetch_if_new(uid)
                    #print t[1]
                elif cid == "url":
                    pass
                elif cid == "topic":
                    pass
                elif cid == "entry":
                    pass
                else:
                    fetch_cache[ i[u'id'][u'$t'].rsplit("/", 1)[1] ] = "%s %s %s"%(id, cid, title)

        if start_index is not None:
            start = start_index+10
            url = "%s&max-result=10&start-index=%s"%(URL_REC%id, start)
            yield user_id_list_by_rec, url, id, start

def main():
    url_list = [
        (user_id_list_by_like, URL_LIKE%(1015 , 193974547)),
    ]

    headers = {
        'Cookie': 'bid="i9gsK/lU40A"; ll="108288"; __gads=ID=94ec68b017d7ed73:T=1324993947:S=ALNI_MaYLBDGa57C4diSiOVJspHn0IAVQw; __utma=164037162.1587489682.1327387877.1327387877.1327387877.1; __utmz=164037162.1327387877.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); viewed="7153184"; __utmb=164037162.2.8.1327387877; __utmc=164037162; RT=s=1327387895075&r=http%3A%2F%2Fwww.douban.com%2Fnote%2F196951541%2F; dbcl2="13593891:UKKGQFylj18"; ck="lLgF"'

    }

    fetcher = NoCacheFetch( headers=headers)
    spider = Rolling( fetcher, url_list )
    spider_runner = GSpider(spider, workers_count=1)
    spider_runner.start()


if __name__ == "__main__":

    main()
    kvdb.close_db()
