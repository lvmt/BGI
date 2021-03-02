#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @Author lvmengting
# @Time   2020/12/15 16:58
# @Email  13554221497@163.com
# @File   mk_ln.py


import os


def mkdir(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)


def hand(bamfile):
    with open(bamfile, 'r') as fr:
        for line in fr:
            if line.startswith('#'):
                pass
            path = line.strip()
            *_, dirname, _1, _2 = line.strip().split('\t')
            mkdir(dirname)
            mkdir('{}/pindel'.format(dirname))
            mkdir('{}/varben'.format(dirname))

            cmd = 'ln {path}/*markdup.bam* {dirname}/'.format(**locals())
            os.system(cmd)
