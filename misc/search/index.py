#!/usr/bin/env python
# -*- coding: utf-8 -*-
import _env
from config import SEARCH_DB_PATH
from mmseg.search import seg_txt_search, seg_title_search, seg_txt_2_dict
from os import makedirs
from os.path import join, exists
import xapian
from collections import defaultdict

PATH = join(SEARCH_DB_PATH, 'zsite')
if not exists(PATH):
    makedirs(PATH)

SEARCH_DB = xapian.WritableDatabase(PATH, xapian.DB_CREATE_OR_OPEN)

#print PATH

def flush_db():
    SEARCH_DB.flush()


def index():
    from zsite_iter import zsite_keyword_iter
    for id, rank, kw in zsite_keyword_iter():

        doc = xapian.Document()
        doc.add_value(0, id)
        doc.add_value(1, xapian.sortable_serialise(rank))

        for word, value in kw:
            if word:
                if not word.startswith('>'):
                    if len(word) < 254:
                        doc.add_term(word, value)

        key = '>%s'%id
        doc.add_term(key)
        SEARCH_DB.replace_document(key, doc)

    flush_db()

if __name__ == '__main__':
    index()
