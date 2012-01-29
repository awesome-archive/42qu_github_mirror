#!/usr/bin/env python
# -*- coding: utf-8 -*-

from random import random, sample, shuffle
from bisect import bisect, insort


def wsample(wlist, key=None):
    lst = []
    s = 0
    if key is not None:
        vlist = map(key, wlist)
    else:
        vlist = wlist
    for w in vlist:
        s += w
        lst.append(s)
    r = random() * s
    idx = bisect(lst, r)
    return wlist[idx]


def wsample_k(wlist, k, key=None):
    L = len(wlist)
    if k >= L:
        return wlist
    lst = []
    s = 0
    if key is not None:
        vlist = map(key, wlist)
    else:
        vlist = wlist
    for w in vlist:
        s += w
        lst.append(s)
    popped = []
    rs = []
    for i in xrange(k):
        r = random()*s
        for idx, ss, w in popped:
            if r >= ss:
                r += w
        idx = bisect(lst, r)
        insort(popped, (idx, lst[idx-1] if idx else 0, vlist[idx]))
        s -= vlist[idx]
    return [wlist[p[0]] for p in popped]


def wsample2(wlist):
    lst = []
    s = 0
    for val, w in wlist:
        s += w
        lst.append(s)
    def sample():
        r = random() * s
        idx = bisect(lst, r)
        return wlist[idx]
    return sample


def wsample_k2(wlist, k, key=None):
    if k >= len(wlist):
        return lambda:wlist

    lst = []
    s = 0
    if key is not None:
        vlist = map(key, wlist)
    else:
        vlist = wlist

    _wlist = []
    _vlist = []
    for w, v in zip(wlist, vlist):
        if v:
            _wlist.append(w)
            _vlist.append(v)

    wlist = _wlist
    vlist = _vlist

    if k >= len(wlist):
        return lambda:wlist


    for w in vlist:
        s += w
        lst.append(s)


    def _():
        popped = []
        rs = []
        t = s
        for i in xrange(k):
            r = random()*t
            for idx, ss, w in popped:
                if r >= ss:
                    r += w
            idx = bisect(lst, r)
            insort(popped, (idx, lst[idx-1] if idx else 0, vlist[idx]))
            t -= vlist[idx]
        return [wlist[p[0]] for p in popped]
    return _


def sample_or_shuffle(population, k):

    if len(population) > k:
        return sample(population, k)
    shuffle(population)
    return population


def limit_by_rank(incr_rank_list, limit):
        
    result = [
       random() for i in xrange(limit)
    ]
    result.sort()

    incr_rank_list.append(1)
    
    l = []

    index = 0 
    small = incr_rank_list[index]
    count = 0

    for i in result:
        if i < small:
            count += 1
        else:
            l.append(count)
            count = 0
            index += 1
            small = incr_rank_list[index]

    l.append(count)

    return l

if __name__ == '__main__':
    print limit_by_rank([0.3, ], 10000)


    #z = wsample_k2(
    #    [2, 3, 4], 2
    #)
    #for i in range(10):
    #    print z()



