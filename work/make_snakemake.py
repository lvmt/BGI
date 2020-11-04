#!/usr/bin/env python
#-*- coding:utf-8 -*-


'''生成每个任务所需要的snakemake文件
'''

import textwrap
import time
from utils import get_info_dict

class MakeSnakemake(object):


    def __init__(self,args):
        self.idfile = args['idfile']
        self.samfile = args['samfile']
        self.projdir = args['projdir']
        
        self.fq_info_dict = get_info_dict(self.idfile,self.samfile)
        self.cmds = []

    
    def raw_reads_filter_make(self,libid):
        '''生成第一步的makefile段落
        '''
        fq1 = self.fq_info_dict[libid]
        fq2 = fq1.replace('1.fq.gz', '2.fq.gz')
        newlibid = libid.replace('-', '_')
        cmd = textwrap.dedent('''
        rule raw_reads_filter_{newlibid}:
            input:
                fq1="{fq1}",
                fq2="{fq2}",
            output:
                newfq1="{self.projdir}/{libid}/new_filter_1.fq",
                newfq2="{self.projdir}/{libid}/new_filter_2.fq",
                statfile="{self.projdir}/{libid}/statistic.txt",
            shell:
                """
                perl /ifs9/BC_B2C_01A/B2C_Common/HLA/HST_MGI/bin/raw_reads_filter_v0.2.pl
                {{input.fq1}} 
                {{input.fq2}}
                1 15
                {{output.newfq1}}
                {{output.newfq2}} > {{output.statfile}}
                """
        '''.format(**locals()))

        #print(cmd)
        return cmd


    def sample_grouping_gz_make(self,libid):
        '''
        '''
        newlibid = libid.replace('-', '_')
        cmd = textwrap.dedent('''
        rule sample_grouping_gz_{newlibid}:
            input:
                newfq1="{self.projdir}/{libid}/new_filter_1.fq",
                newfq2="{self.projdir}/{libid}/new_filter_1.fq",
                index="/ifs9/BC_B2C_01A/B2C_Common/HLA/HST_MGI/database/index/index.index",
            output:
                dirname="{self.projdir}/{libid}",
            shell:
                """
                /ifs9/BC_B2C_01A/B2C_Common/HLA/HST_MGI/bin/sample_grouping_gz 
                -a {{input.newfq1}}
                -b {{input.newfq2}}
                -i {{input.index}}
                -o {{output.dirname}}
                """
        '''.format(**locals()))

        return cmd


    def write_snakemake(self):
        '''输出snakemake文件
        '''
        with open('demo.smk', 'w') as fw:
            for cmd in self.cmds:
                fw.write(cmd)


    def go(self):
        
        # 
        for libid in self.fq_info_dict.keys():
            cmd = self.raw_reads_filter_make(libid)
            self.cmds.append(cmd)
            cmd = self.sample_grouping_gz_make(libid)
            self.cmds.append(cmd)
            print('\033[1;32m>>> libid: {libid}\033[0m'.format(**locals()))
            print(cmd)    
            
            time.sleep(1)

        self.write_snakemake()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='make snakemakefile of project need.')
    parser.add_argument('--idfile', help='file contail fq.gz')
    parser.add_argument('--samfile', help='file contain sams information')
    parser.add_argument('--projdir', help='project dir, absolute path')

    args = vars(parser.parse_args())
    gg = MakeSnakemake(args)
    gg.go()
