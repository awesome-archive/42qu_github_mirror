#!/usr/bin/env python
#coding:utf-8

from random import random
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

if __name__ == '__main__':
    z = wsample_k2(
        [2, 3, 4], 2
    )
    for i in range(10):
        print z()
