#!/usr/bin/env python
# -*- coding: utf-8 -*-
from _db import Model, McModel, McCache, McLimitM, McNum, McCacheA, McCacheM



JOB_MAIL_STATE_VERIFY = 10
JOB_MAIL_STATE_VERIFIED = 20

class JobMail(McModel):
    pass


mc_job_mail_by_com_id = McCache("JobMailByComId:%s")


def job_mail_new(zsite_id, mail, department_id=0, state=JOB_MAIL_STATE_VERIFY):
    mail = mail.strip().lower()
    if mail:
        jm = JobMail.get_or_create(zsite_id=zsite_id)
        jm.mail = mail
        jm.department_id = department_id
        jm.state = state
        jm.save()

        mc_job_mail_by_com_id.delete(zsite_id)

    return jm

@mc_job_mail_by_com_id("{id}")
def job_mail_by_com_id(id):
    jm = JobMail.get(zsite_id=id,department_id=0)
    if jm and jm.state >= JOB_MAIL_STATE_VERIFIED:
        return jm.mail
    return ''


def job_mail_if_exist(id):
    jm = JobMail.get(zsite_id=id,department_id=0)
    if jm:
        return jm.mail

def job_mail_verifyed(id):
    jm = JobMail.get(zsite_id=id,department_id=0)
    if jm:
        jm.state = JOB_MAIL_STATE_VERIFIED
        jm.save()
        mc_job_mail_by_com_id.delete(id)

