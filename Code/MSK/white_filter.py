#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @Author lvmengting
# @Time   2020/12/16 16:31
# @Email  13554221497@163.com
# @File   white_filter.py


"""
白名单位点注释
- snp, indel分开注释
- 根据 chr_start_ref_alt
  start：为变异发生的位置
attention
- 流程indel文件中,start的位置需要 + 1
- DEL: ref = ref[1:], alt = -
- INS: ref = '-', alt = alt[1:]
- DELINS: ref = ref[1:], alt = alt[1:]
"""



import json
import re
from collections import OrderedDict


def get_database(jsonfile):
    """
    Args:
        jsonfile: database's json file

    Returns:
        python type dict
    """
    with open(jsonfile, 'r') as fr:
        dict_info = json.load(fr)
    return dict_info


def safe_open(filename, mode='r'):
    if not filename.endswith('.gz'):
        return open(filename, mode)
    else:
        import gzip
        return gzip.open(filename, mode)


def head_index(head):
    """
    Args:
        head: 文件表头

    Returns:
        dict
        每一列的索引信息
        {‘gene’: 1, 'Function': 5, ...}

    """
    head_index_dict = OrderedDict()
    if not isinstance(head, list):
        head = head.strip().split('\t')

    for index, item in enumerate(head):
        head_index_dict[item.lower()] = index

    return head_index_dict


def filter_snp(snvfile, snpout, snp_db):
    """
    Args:
        snvfile: somatic.snv.vcf.gz

    Returns:
        snvfile.whitelist

    """
    snp_dict = get_database(snp_db)
    with safe_open(snvfile, 'r') as fr, open(snpout, 'w') as fw:
        for line in fr:
            if line.startswith('##'):
                fw.write(line)
                continue
            elif line.startswith('#'):
                fw.write(line)
                head = line.strip()
                head_index_dict = head_index(head)
                continue
            linelist = line.strip().split('\t')
            _chr = linelist[head_index_dict['#chrom']].replace('chr', '')
            start = linelist[head_index_dict['pos']]
            ref = linelist[head_index_dict['ref']]
            alt = linelist[head_index_dict['alt']]

            key = '{_chr}_{start}_{ref}_{alt}'.format(**locals())
            if snp_dict.get(key, None):
                fw.write(line)
            else:
                print('not in snp whitelist file.')


def filter_indel(indelfile, indelout, indel_db):
    """
    Args:
        indelfile: indel.possible.afteraln.vcf.gz

    Returns:
        indelfile.whitelist

    ## 需要根据type进行区分.

    """
    indel_dict = get_database(indel_db)
    pattern = re.compile(r'Strand=.*;DP=.*;CtrlDP=.*;Type=(.*)', re.S)

    with safe_open(indelfile, 'r') as fr, open(indelout, 'w') as fw:
        for line in fr:
            if line.startswith('##'):
                fw.write(line)
                continue
            elif line.startswith('#'):
                fw.write(line)
                head = line.strip()
                head_index_dict = head_index(head)
                continue
            linelist = line.strip().split('\t')
            _chr = linelist[head_index_dict['#chrom']].replace('chr', '')
            start = str(int(linelist[head_index_dict['pos']]) + 1)  # +1 变异开始发生的位置
            info = linelist[head_index_dict['info']]
            sv_type = re.search(pattern, info).group(1)

            if sv_type == 'DEL':
                ref = linelist[head_index_dict['ref']][1:]
                alt = '-'
            elif sv_type == 'INS':
                ref = '-'
                alt = linelist[head_index_dict['alt']][1:]
            elif sv_type == 'DELINS':
                ref = linelist[head_index_dict['ref']][1:]
                alt = linelist[head_index_dict['alt']][1:]

            key = '{_chr}_{start}_{ref}_{alt}'.format(**locals())

            if indel_dict.get(key, None):
                fw.write(line)


def main(agrs):
    if agrs.filter_type == 'snp':
        filter_snp(agrs.snvfile, agrs.snpout, agrs.snp_db)
    elif agrs.filter_type == 'indel':
        filter_indel(agrs.indelfile, agrs.indelout, agrs.indel_db)
    else:
        filter_snp(agrs.snvfile, agrs.snpout, agrs.snp_db)
        filter_indel(agrs.indelfile, agrs.indelout, agrs.indel_db)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='filter cancerhotspots')
    parser.add_argument('--snvfile', help='input, snv file')
    parser.add_argument('--indelfile', help='input, indel file')
    parser.add_argument('--snp_db', help='snp cancerhotspot database')
    parser.add_argument('--indel_db', help='indel cancerhotspot database')
    parser.add_argument('--snpout', help='snp site in white list')
    parser.add_argument('--indelout', help='indel site in white list')
    parser.add_argument('--filter_type', help='while to filter, snp or indel',
                        default='snp,indel', choices=['snp', 'indel'])

    agrs = parser.parse_args()

    main(agrs)