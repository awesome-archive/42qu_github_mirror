#!/usr/bin/env python
# -*- coding: utf-8 -*-
from _db import Model, McModel, McCache, McLimitM, McNum, McCacheA, McCacheM
from zkit.job import JOBKIND2CN
from zsite_com import pid_by_com_id
from zkit.attrcache import attrcache

mc_job_type_by_job_id = McCacheA("JobTypeByJobId:%s")
mc_job_kind_by_job_id = McCacheA("JobKindByJobId:%s")
JOBTYPE = (
    (1, '兼职'),
    (2, '实习生'),
    (3, '全职'),
    (4, '合伙人'),
)

JOB_ACTIVE = 5
JOB_CLOSE = 4
JOB_DEL = 3


SALARY_TYPE=(
    (1,'月薪'),
    (2,'年薪')
)
JOBSALARY2CN = dict(SALARY_TYPE) 
JOBTYPE2CN = dict(JOBTYPE)

class ComJobNeeds(McModel):
    pass

class ComJob(McModel):
    @attrcache
    def job_department_list(self):
        return ComDepartment.where(com_id=self.id)

    @attrcache
    def needs(self):
        return ComJobNeeds.mc_get(self.id)
class JobPlace(McModel):
    pass

class JobType(McModel):
    pass

class JobPid(McModel):
    pass

class JobKind(McModel):
    pass


class ComDepartment(McModel):
    pass


def com_department_edit(id, name):
    cd = ComDepartment.get_or_create(id=id)
    cd.name = name
    cd.save()

def com_department_new(com_id, name):
    cd = ComDepartment(com_id=com_id, name=name)
    cd.save()
    return cd

def com_department_rm_by_id(id):
    return ComDepartment.where(id=id).delete()



def com_department_by_com_id(com_id):
    return ComDepartment.where(com_id=com_id)


def job_place_new(job_id, com_pid):
    jp = JobPlace.get_or_create(job_id=job_id, pid=com_pid)
    jp.save()
    return jp

@mc_job_kind_by_job_id("{id}")
def job_kind_by_job_id(id):
    return JobKind.where(job_id=id).col_list(col='kind_id')

def job_kind_set(id,kind_list):
    id_set_old = set(job_kind_by_job_id(id))
    id_set_new = set([
        i for i in map(int,kind_list) if i in JOBKIND2CN
        ])
    for kind_id in (id_set_old - id_set_new):
        JobKind.where(job_id=id,kind_id=kind_id).delete()

    for kind_id in (id_set_new - id_set_old):
        jkn = JobKind.get_or_create(job_id=id,kind_id=kind_id)
        jkn.save()
    mc_job_kind_by_job_id.delete(id)

@mc_job_type_by_job_id("{id}")
def job_type_by_job_id(id):
    return JobType.where(job_id=id).col_list(col='type_id')

def job_type_set(id, type_list):
    id_set_old = set(job_type_by_job_id(id))
    id_set_new = set([
        i for i in map(int,type_list) if i in JOBTYPE2CN
    ])
    
    for type_id in (id_set_old - id_set_new):
        JobType.where(job_id=id, type_id=type_id).delete()
 
    for type_id in (id_set_new - id_set_old):
        jtn = JobType.get_or_create(job_id=id, type_id=type_id)
        jtn.save() 

    mc_job_type_by_job_id.delete(id)


def job_pid_by_com_id(com_id):
    p = JobPid.where(com_id=com_id)
    if not p:
        p = pid_by_com_id(com_id)
    return p

def job_pid_new(com_id, pid):
    jp = JobPid.get_or_create(com_id=com_id, pid=pid)
    jp.save()
    return jp

def job_kind_new(job_id, kind_id):
    jt = JobKind(job_id=job_id, kind_id=kind_id)
    jt.save()
    return jt

def job_place_by_job_id(job_id):
    return JobPlace.where(job_id=job_id).col_list(col='pid')



def job_new(
        com_id, department_id, 
        title, create_time, salary_up, salary_down, salary_type, end_time,
        quota,
        txt, require,stock_option,welfare,priority,
        job=None
    ):
    if not job:
        job = ComJob(
            com_id = com_id,
        )
    cj.department_id=department_id
    cj.title=title
    cj.create_time=create_time
    cj.salary_up=salary_up
    cj.salary_down=salary_down
    cj.salary_type=salary_type
    cj.end_time=end_time
    cj.quota=quota
    cj.state = JOB_ACTIVE
    cj.save()

    cjn = ComJobNeeds.get_or_create(id=job_id)
    cjn.stock_option=stock_option
    cjn.welfare=welfare
    cjn.txt = txt
    cjn.priority = priority
    cjn.require = require
    cjn.save()

    return cj

def com_job_by_com_id(com_id):
    return ComJob.where(com_id=com_id)

def com_job_by_state_com_id(com_id,state):
    return ComJob.where(state=state,com_id=com_id)

def com_job_by_department_and_com(department_id,com_id):
    return ComJob.where(department_id=department_id,com_id=com_id,state=JOB_ACTIVE)

def job_place_list(self):
    return JobPlace.where(com_id=self.id)

if __name__ == "__main__":
    job_type_set(25, [2,3225])
