#!/usr/bin/env python
#-*- coding:utf-8 -*-


'''截取数据量
## 思路
1.计算每个样本的总reads
2.根据目标数据量,得到目标reads数目
3.得到目标数据量与样本总数据量间的百分数
4.对每个样本的每条lane按照比率进行截取数据量.

## 借助工具
seqkit
'''

import re
import subprocess
from collections import defaultdict

class CutData(object):

    def __init__(self,args):
        self.all_path = args['all_path'] # 泛癌的输入文件即可.
        self.outdir = args['outdir']
        self.target_reads = args['target'] * 1000 * 1000 * 1000   # G作为单位,
        self.info_dict = defaultdict(dict)


    def get_sam_fq(self):
        '''
        {
            samid:{
                'fq': [aa, bb],
                'totalreads': 19200291,
                'fq_read': [100, 300, 200],
                'ratio': 0.5, 
            }
        }
        '''        
        with open(self.all_path, 'r') as fr:
            for line in fr:
                linelist = line.strip().split('\t')
                if line.startswith('#'):
                    #headlist = linelist
                    continue
                samid = linelist[1]
                ty = linelist[2]
                fq1 = linelist[8]

                if self.info_dict[f'{samid}_{ty}']:
                    self.info_dict[f'{samid}_{ty}']['fq'].append(fq1)
                else:
                    self.info_dict[f'{samid}_{ty}']['fq'] = [fq1]
        
        print(self.info_dict)


    def get_fq_reads(self, fq):
        '''获取输入fq的reads数目
        '''
        out = subprocess.getoutput('seqkit stats {fq} --all '.format(**locals())).split('\n')[-1]
        out = [item for item in out.split(' ') if item]
        reads = ''.join(out[3].split(','))
        print(reads)
        return reads


    def stat_sams_reads(self):
        for samid in self.info_dict.keys():
            sumreads = 0
            fq_read = [] # 记录每个fq的reads数目
            for fq in self.info_dict[samid]:
                reads = int(self.get_fq_reads(fq))
                fq_read.append(reads)
                sumreads += reads

            self.info_dict[samid]['totalreads'] = sumreads
            self.info_dict[samid]['fq_read'] = fq_read
            self.info_dict[samid]['ratio'] = self.target_reads / sumreads  # 


    def write_shell(self):
        cmda = []
        for samid in self.info_dict.keys():
            for index,fq in enumerate(self.info_dict[samid]):
                need_read = int(self.info_dict[samid]['fq_read'][index] * self.info_dict[samid]['ratio'])
                suffix = re.match(r'(.+)(/V.+/L.+)', fq)
                newfq = '{self.outdir}/{suffix}'
                cmd = 'seqkit head -n {need_read} {fq} > {newfq}'.format(**locals()) 

                cmda.append(cmd)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--all_path', help='all_path.')
    parser.add_argument('--outdir', help='output dir.')
    parser.add_argument('--target', type=int, help='taget datasize.')

    args = vars(parser.parse_args())

    cc = CutData(args)
    
    #print(cc.get_sam_fq())

    cc.write_shell()
