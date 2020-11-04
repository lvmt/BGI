#!/usr/bin/env python
#-*- coding:utf-8 -*-


'''利用HLA-HD软件对结果进行分型
'''


import glob
import os 
import textwrap



class HLAHDTyping(object):

    
    def __init__(self, args):
        self.libdir = args['libdir']
        self.outdir = args['outdir']

    
    def mkdir(self,dirname):
        if os.path.exists(dirname):
            pass
        else:
            os.mkdir(dirname)


    def get_fq_list(self, samid):
        fq_list = glob.glob(f'{self.libdir}/fastq/{samid}/*1.fq')
        return fq_list


    def write_shell(self,shellname,cmd):
        dirname = os.path.dirname(shellname)
        self.mkdir(dirname)
        with open(shellname,'w') as fw:
            fw.write(cmd)


    def cat_fq(self,fq_list):
        fq2_list = [item.replace('1.fq', '2.fq') for item in fq_list]
        samid = fq_list[0].split('/')[-2]

        shellname1 = f'{self.outdir}/{samid}/cat_fq_{samid}_1.sh'
        shellname2 = f'{self.outdir}/{samid}/cat_fq_{samid}_2.sh'
        fq1 = " ".join(fq_list)
        fq2 = " ".join(fq2_list)
        cmd1 = f'cat {fq1} > {self.outdir}/{samid}/{samid}_1.fq \n'
        cmd2 = f'cat {fq2} > {self.outdir}/{samid}/{samid}_2.fq \n'

        self.write_shell(shellname1,cmd1)
        self.write_shell(shellname2,cmd2)
        os.system(f'qsub -e {self.outdir}/log -o {self.outdir}/log -l vf=2g,p=1 -P B2C_HLA {shellname1}')
        os.system(f'qsub -e {self.outdir}/log -o {self.outdir}/log -l vf=2g,p=1 -P B2C_HLA {shellname2}')
        return shellname1,shellname2


    def HLA_typing(self,samid,orders):

        fq1 = f'{self.outdir}/{samid}/{samid}_1.fq'
        fq2 = f'{self.outdir}/{samid}/{samid}_2.fq'
        
        cmd = textwrap.dedent('''
        export PATH=$PATH:/ifs9/B2C_COM_P1/PROJECT/HLA/WORK/lmt/software/hlahd.1.2.0.1/bin 

        hlahd.sh \\
            -t 8 \\
            -m 100 \\
            -f /ifs9/B2C_COM_P1/PROJECT/HLA/WORK/lmt/software/hlahd.1.2.0.1/freq_data \\
            {fq1} \\
            {fq2} \\
            /ifs9/B2C_COM_P1/PROJECT/HLA/WORK/lmt/software/hlahd.1.2.0.1/HLA_gene.split.txt \\
            /ifs9/B2C_COM_P1/PROJECT/HLA/WORK/lmt/software/hlahd.1.2.0.1/dictionary \\
            {samid} \\
            {self.outdir} 
        '''.format(**locals()))

        shellname = f'{self.outdir}/{samid}/hlahd_typing_{samid}.sh'
        self.write_shell(shellname,cmd)
        os.system(f'qsub -e {self.outdir}/log -o {self.outdir}/log -l vf=2g,p=1 -hold_jid {orders} -P B2C_HLA {shellname}')

    
    def start(self):

        self.mkdir(f'{self.outdir}/log')
        samid_list = map(str, range(1,97))
        samid_list = ['L' + item.rjust(3,'0') for item in samid_list]

        for samid in samid_list:
            print(f'\033[1;33m{samid}\033[0m')
            fq_list = self.get_fq_list(samid)
            shellname1,shellname2 = self.cat_fq(fq_list)
            orders = [os.path.basename(item) for item in [shellname1,shellname2]]
            orders = ",".join(orders)
            self.HLA_typing(samid,orders)



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='HLA-HD typing result')

    parser.add_argument('--libdir', help='libdir')
    parser.add_argument('--outdir', help='output dir')

    args = vars(parser.parse_args())

    h = HLAHDTyping(args)
    h.start()


    

    