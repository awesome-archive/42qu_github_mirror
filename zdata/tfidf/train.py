#!/usr/bin/env python
# -*- coding: utf-8 -*-

import _env
import os
from tfidf.idf import Idf
from tfidf.config import DATA_DIR
from zkit.txt_cleanup import line_iter

def tf_idf_by_zhihu():
    current_path = os.path.dirname(os.path.abspath(__file__))
    infile = join(current_path,'train_data/','out.js')
    outfile = join(DATA_DIR, 'zhihu.idf')
    idf = Idf()

    with open(infile) as lib:
        for line in lib:
            l = loads(line)
            idf.append( l['title'] )
            for j in l['answer']:
                idf.append(j['answer'])

    with open(join(DATA_DIR,"review.txt")) as review:
        result = []
        for line in review:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">->->"):
                if result:
                    line = line.split(" ",5)
                    result.append(line[-1])
                    txt = "\n".join(result)
                    idf.append(txt)
                    #print line[1]
                    #print txt
                    #raw_input()
                result = []
            else:
                result.append(line)

    idf.tofile(outfile)