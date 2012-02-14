#!/usr/bin/env python
# -*- coding: utf-8 -*-

from name2id import NAME2ID
from model.po_by_tag import tag_alias_new

def main():
    for k,v in NAME2ID:
        tag_alias_new(alias=k,id=v)

if __name__ == '__main__':
    main()
