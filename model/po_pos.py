#!/usr/bin/env python
# -*- coding: utf-8 -*-
from time import time
from _db import cursor_by_table, Model, McModel, McLimitA, McCache, McCacheA, McCacheM
from po import Po

STATE_BUZZ = 1
STATE_MUTE = 0

class PoPos(Model):
    pass

mc_po_pos = McCacheM('PoPos.%s')

@mc_po_pos('{user_id}_{po_id}')
def po_pos_get(user_id, po_id):
    p = PoPos.get(user_id=user_id, po_id=po_id)
    if p:
        return p.pos, p.state
    return -1, STATE_MUTE

mc_po_viewed_list = McLimitA('PoViewedList.%s', 128)

@mc_po_viewed_list('{po_id}')
def po_viewed_list(po_id, limit, offset):
    qs = PoPos.where(po_id=po_id).order_by('id desc')
    return [i.user_id for i in qs]

def po_buzz_list(po_id):
    qs = PoPos.where(po_id=po_id, state=STATE_BUZZ)
    return [i.user_id for i in qs]

def po_pos_set(user_id, po):
    pos = po.reply_id_last
    po_id = po.id
    pos_old, _ = po_pos_get(user_id, po_id)
    if pos > pos_old:
        PoPos.raw_sql('insert delayed into po_pos (user_id, po_id, pos, state) values (%s, %s, %s, %s) on duplicate key update pos=values(pos)', user_id, po_id, pos, STATE_MUTE)
        mc_po_pos.delete('%s_%s' % (user_id, po_id))
    if pos_old == -1:
        mc_po_viewed_list.delete(po_id)

def po_pos_set_by_po_id(user_id, po_id):
    if user_id:
        po = Po.mc_get(po_id)
        if po:
            po_pos_set(user_id, po)

def po_pos_state(user_id, po_id, state):
    pos, state_old = po_pos_get(user_id, po_id)
    if pos >= 0 and state_old != state:
        PoPos.raw_sql('update po_pos set state=%s where user_id=%s and po_id=%s', state, user_id, po_id)
        mc_po_pos.delete('%s_%s' % (user_id, po_id))

if __name__ == '__main__':
    pass
