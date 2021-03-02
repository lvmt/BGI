#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @Author lvmengting
# @Time   2021/1/4 16:54
# @Email  13554221497@163.com
# @File   get_maf.py.py


"""
处理文件, 得到landascape的输入文件.
"""


from collections import defaultdict


def get_dict_info(infile):
    """
    Args:
        infile:

    Returns:
    dict:
    {
        'samid':
            gene1: (snv, indel)
            gene2: (snv, indel, splice)
        'samid':
            'gene1': ()
            gene2: ()
        }
    """
    dict_info = defaultdict(dict)
    gene_set = set()
    with open(infile, 'r') as fr:
        for line in fr:
            linelist = line.strip('\n').split('\t')
            samid, _, gene, mut_type = linelist
            gene_set.add(gene)
            if gene not in dict_info[samid]:
                dict_info[samid][gene] = mut_type
            elif mut_type in dict_info[samid][gene]:
                pass
            else:
                dict_info[samid][gene] += ';' + mut_type

    return dict_info, gene_set


def out_stat(dict_info, gene_set, resultfile):
    sams = dict_info.keys()
    head = "\t".join(sams)
    with open(resultfile, 'w') as fw:
        fw.write('\t{head}\n'.format(**locals()))
        for gene in gene_set:
            tmp = []
            for sam in sams:
                tmp.append(dict_info[sam].get(gene, ''))
            fw.write('{0}\t{1}\n'.format(gene, '\t'.join(tmp)))



dd, gene_set = get_dict_info('mutation.txt')
out_stat(dd, gene_set, 'maf.xls')





# print(dd.keys())
# print('样本数目', len(dd.keys()))
# # print(get_dict_info('mutation.txt'))
# print(dd['17S0053489'])
# print(len(dd['17S0053489']))
# print(gene_set)
# print('gene numbers: ', len(gene_set))
