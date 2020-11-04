#!/usr/bin/env python3
#-*- coding:utf-8 -*-


'''
思路梳理:
 - ps ef ：先杀掉主程序;
 - qdel jobid.
'''

import subprocess
import textwrap
import sys
import os


class Killjob(object):

    def __init__(self, projdir):
        self.projdir = projdir
    
    def kill_pid(self):
        '''先杀掉主程序.
        '''
        result = subprocess.getoutput("ps -ef|grep {self.projdir}|grep -v 'grep'".format(**locals()))
        if result:
            pass

    def get_all_jobid(self):
        '''
        获取当前所有的jobid
        '''
        ids = subprocess.getoutput("qstat | sed '1,2d' |awk -F ' ' '{print $1}'").split('\n')
        return ids


    def get_id_info(self,id):
        '''获取每个id的info信息
        '''
        workdir = subprocess.getoutput("qstat -j {id} | grep cwd | awk -F ' ' '{{print $NF}}'".format(**locals()))
        return workdir


    def get_kill_id(self,ids):
        kill_ids = []
        for id in ids:
            workdir = self.get_id_info(id)
            if workdir == self.projdir:
                kill_ids.append(id)
        return kill_ids


    def kill(self,kill_ids):
        for id in kill_ids:
            print('\033[1;32m任务杀掉中....{id}\033[0m'.format(**locals()))
            os.system('qdel {id}'.format(**locals()))


    def start(self):
        ids = self.get_all_jobid()
        kill_ids = self.get_kill_id(ids)
        self.kill(kill_ids)


if __name__ == '__main__':
    args = sys.argv

    if len(args) == 1:
        print('\033[1;33mUsage: python killjob.pl projdir\033[0m')
    else:
        projdir = args[1]
        Killjob(projdir).start()

