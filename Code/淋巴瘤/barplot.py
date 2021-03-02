#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @Author lvmengting
# @Time   2021/1/5 10:39
# @Email  13554221497@163.com
# @File   barplot.py


"""
整体数据, 全部样本, 每个基因每个变异的突变数目统计.
堆彻条形图
"""


from collections import defaultdict


def get_dict_info(infile):
    """
    Args:
        infile:

    Returns:
    {
        gene: {
            'missense': int,
            'stop-gain': int,
        },
        gene2:{


        }
    }
    """
    dict_info = defaultdict(dict)
    with open(infile, 'r') as fr:
        for line in fr:
            linelist = line.strip('\n').split('\t')
            _, _, gene, mut = linelist
            if mut not in dict_info[gene]:
                dict_info[gene][mut] = 1
            else:
                dict_info[gene][mut] += 1

    return dict_info


def out_result(dict_info, outfile):
    genes = dict_info.keys()
    muts = [
        'cds-indel',
        'frameshift',
        'missense',
        'misstart',
        'nonsense',
        'splice',
        'stop-gain',
        'stop-loss']

    with open(outfile, 'w') as fw:
        head = '\t'.join(genes)
        fw.write('\t{head}\n'.format(**locals()))

        for mut in muts:
            tmp = []
            for gene in genes:
                tmp.append(str(dict_info[gene].get(mut, 0)))
            fw.write('{}\t{}\n'.format(mut, '\t'.join(tmp)))



dd = get_dict_info('mutation.txt')
out_result(dd, 'barplot.xls')
print(dd)

'KMT2C', 'PCLO', 'ITPKB', 'GTSE1', 'NCOR2', 'PANX1', 'AMOTL1', 'TP53', 'LILRA2', 'KMT2D'
