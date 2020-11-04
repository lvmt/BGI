#!/usr/bin/env python
#-*- coding:utf-8 -*-


'''
提取参考基因组,指定位置的碱基.
'''


import re
import textwrap
import subprocess

def get_base(pos,outfile=None):
    '''pos需要包含的信息
    chr:start-end
    '''
    chr,start,end = re.split(r':|-|,|;', pos)

    cmd = 'samtools faidx /jdfstj1/B2C_COM_P1/pipeline/oseq/db/alignment/hg19/hg19.fa chr{chr}:{start}-{end}'.format(**locals())
    result = subprocess.getoutput(cmd)

    if outfile:
        with open(outfile, 'w') as fw:
            fw.write(result)
    else:
        cmd = textwrap.dedent('''\033[1;32m
        查询位置信息: {pos}
        查询结果如下所示:\033[1;33m
        {result}\033[0m''').format(**locals())
        print(cmd)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='\033[1;32m== 获取参考基因组指定位置碱基 (默认:hg19) ==\033[0m')
    parser.add_argument('pos', help='query position,eg: chr:start-end.')
    parser.add_argument('--outfile', help='filename, write result to file.')

    args = vars(parser.parse_args())
    pos = args.get('pos')
    outfile = args.get('outfile', 'None')

    get_base(pos,outfile)


