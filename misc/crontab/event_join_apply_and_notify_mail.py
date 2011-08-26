#!/usr/bin/env python
# -*- coding: utf-8 -*-
import _env
from model.event import EventJoiner, event_review_join_apply, EVENT_JOIN_STATE_NEW, event_ready, EVENT_STATE_BEGIN, Event
from time import time, timezone
from model.kv_misc import kv_int_call, KV_EVENT_READY
from zkit.single_process import single_process
from zweb.orm import ormiter
from model.days import today_days, ONE_DAY_MINUTE

def buzz_join_apply_review_mail():
    ago = int(time() + timezone) - 18*60*60

    c = EventJoiner.raw_sql('select distinct(event_id) from event_joiner where state=%s and create_time<%s;', EVENT_JOIN_STATE_NEW, ago)

    event_id_list = c.fetchall()

    for event_id, in event_id_list:
        event_review_join_apply(event_id)

def event_ready_mail(begin):
    end = (today_days() + 3) * ONE_DAY_MINUTE
    for event in ormiter(Event, 'state=%s and begin_time>%s and begin_time<=%s' % (EVENT_STATE_BEGIN, begin, end)):
        event_ready(event)
    return end

@single_process
def main():
    buzz_join_apply_review_mail()
    kv_int_call(KV_EVENT_READY, event_ready_mail)

if __name__ == '__main__':
    main()
