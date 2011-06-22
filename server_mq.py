#!/usr/bin/env python
# -*- coding: utf-8 -*-
from model.mq import mq_server
from model.feed import mq_feed_rt_rm_by_rid
from model.mail import mq_rendermail
from model.buzz import mq_buzz_follow_new, mq_buzz_wall_new, mq_buzz_po_reply_new
from model.notice import mq_notice_question
from model.pic import mq_pic_rm_mail
from model.zsite import mq_zsite_verify_mail

def run():
    mq_server()

if __name__ == '__main__':
    run()
