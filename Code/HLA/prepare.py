#!/usr/bin/env python
#-*- coding:utf-8 -*-


import pandas as pd
import os
import re
import textwrap
import time

# 目的
'''
输入文件: 
	信息搜集表
	项目路径
输出文件: 
	fqlist
	samid
	主流程的shell脚本

# 1.自动监控数据是否下机
# 2.如果下机,投递脚本
# 3.如果没有下机, 等待1小时,重新进行1.2的判断

'''



class Prepare(object):
    def __init__(self,args):
        self.info_excel = args['info_excel']
        self.projdir = args['projdir'] if args.get('projdir') else os.getcwd()
 
        self.name = self.info_excel.split('.xlsx')[0]
        self.fenqi = self.projdir.split('/')[-1]
        self.v = ''
        self.get_samid()
        self.get_fqlist()
        self.write_shell()


    def get_samid(self):
        samid = '{self.projdir}/{self.fenqi}.samid'.format(**locals())
        excel_values = pd.read_excel(self.info_excel).values
        
        with open(samid, 'w') as fw:
            for item in excel_values:
                item = [str(x) for x in item]
                if 'A' in item[-1]:
                    self.v = 'v'+ str(len(item[-1].split('/')))
                    fw.write('{}\n'.format('\t'.join(item[:-1]))) 
    
    
    def get_fqlist(self):
        fqs_set = set()
        with open('{self.projdir}/{self.fenqi}.samid'.format(**locals()), 'r') as fr:
            for line in fr:
                linelist = line.strip().split('\t')
                suffix = '/ifs9/zebra/MGISEQ-2000'
                machineid = linelist[0]
                chip = linelist[1]
                lane = linelist[2]
                lib = linelist[3].split('-')[-1]
                fq = '{suffix}/{machineid}/{chip}/{lane}/{chip}_{lane}_{lib}_1.fq.gz'.format(**locals())
                fqs_set.add(fq)

        with open('{self.projdir}/{self.fenqi}.fqlist'.format(**locals()), 'w') as fw:
            for fq in fqs_set:
                fw.write('{fq}\n'.format(**locals()))
    
    
    @staticmethod
    def path_exists(fqpath):
        if os.path.exists(fqpath):
            return True

    
    def check_fq(self):
        check_fq_tag = []
        with open(f'{self.projdir}/{self.fenqi}.fqlist', 'r') as fr:
            for line in fr:
                fqpath = line.strip()
                if self.path_exists(fqpath):
                    check_fq_tag.append(True)
                else:
                    check_fq_tag.append(False)
        return check_fq_tag
        
    
    def write_shell(self):
        cmd = textwrap.dedent('''
        source ~/.bashrc 
        python /ifs9/B2C_COM_P1/PROJECT/HLA/WORK/lmt/Code/pipelineHLA/pipeline.py \\
            --idfile {self.projdir}/{self.fenqi}.fqlist \\
            --samsfile {self.projdir}/{self.fenqi}.samid \\
            --projdir {self.projdir} \\
            --name {self.name} \\
            --site_version {self.v} 
        '''.format(**locals()))
        with open(f'{self.projdir}/hla_{self.fenqi}.sh', 'w') as fw:
            fw.write(cmd)


    def start(self):
        check_fq_tag = self.check_fq()
        if all(check_fq_tag):
            print('=======任务投递========')
            os.system(f'nohup sh {self.projdir}/hla_{self.fenqi}.sh &')
        else:
            print('=======部分数据暂未下机,等待中...====')
            time.sleep(3600)
            self.start()

    
    

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='monitor path')
    parser.add_argument('--info_excel', help='excel table')
    parser.add_argument('--projdir', help='project path')
    
    args = vars(parser.parse_args())
    print(args)
    
    pp = Prepare(args)
    pp.start()
    
