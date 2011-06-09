#!/usr/bin/env python
#coding:utf-8
import subprocess
from os.path import dirname, abspath , join
import sys

PREFIX = dirname(abspath(__file__))
sys.path = [dirname(dirname(PREFIX))]+sys.path

from config import DB_CONFIG
COMM_OPTION = ' -h%s -P%s -u%s -p%s %s '
def backup_table(key, host, port, name, user, password):
    comm_option = COMM_OPTION%(host, port, user, password, name)

    """
    ����һ�������ݵ�����ʵ��
    mysqldump --skip-opt --no-create-info ���ݿ����� ���� --where="id<2000"
    """
    create_table_option = '--skip-comments --no-data --default-character-set=utf8 --skip-opt --add-drop-table --create-options --quick --hex-blob '+comm_option

    cmd = 'mysqldump '+create_table_option
    #print cmd

    with open(join(PREFIX, 'table_%s.sql'%key), 'w') as backfile:
        subprocess.Popen(
            cmd.split(),
            stdout=backfile
        )


for key, value in DB_CONFIG.iteritems():
    host, port, name, user, password = value.get('master').split(':')
    backup_table(key, host, port, name, user, password)
    #print key


"""
create_table_option = comm_option +  "--skip-opt --no-create-info hao123"

cmd = "mysqldump "+create_table_option
print cmd

with open("data.sql", "w") as backfile:
    subprocess.Popen(
        cmd.split(),
        stdout=backfile
    )
"""
