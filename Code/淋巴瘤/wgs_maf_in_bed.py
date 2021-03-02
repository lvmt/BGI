#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @Author lvmengting
# @Time   2021/1/5 16:13
# @Email  13554221497@163.com
# @File   wgs_maf_in_bed.py


"""
WGS 数据, 统计位点在bed区间内的信息.

in_bed:
    3'Flank
    3'UTR
    5'Flank
    5'UTR
    Frame_Shift_Del
    Frame_Shift_Ins
    IGR
    In_Frame_Del
    In_Frame_Ins
    Intron
    Missense_Mutation
    Nonsense_Mutation
    Nonstop_Mutation
    RNA
    Silent
    Splice_Region
    Splice_Site
    Translation_Start_Site

not_bed :
    like above..
"""

import json
from collections import defaultdict


def is_overlap(_chr1, start1, end1, _chr2, start2, end2, cutoff):
    """
    Args:
        _chr1: 变异的染色体位置
        start1:
        end1:
        _chr2:  bed库文件的染色体位置
        start2:
        end2:
        cutoff: overlap / len(end1 - start1)

    Returns:

    """
    if end1 < start2 or end2 < start1:
        return False
    elif max(start1, start2) <= min(end1, end2):
        overlap = min(end1, end2) - max(start1, start2) + 1
        percent = float(overlap) / float(end1 - start1 + 1)
        if percent >= cutoff:
            return True
        return False


def get_bed_dict(bedfile):
    """
    根据问库文件bed, 构建查询字典
    dict
    {
        chr1: [(start, end), (start, end)...],
        chr2: [(start, end), (start, end)...],
        ..
    }
    """
    bed_dict = defaultdict(list)
    with open(bedfile, 'r') as fr:
        for line in fr:
            linelist = line.strip().split('\t')
            bed_dict[linelist[0]].append((int(linelist[1]), int(linelist[2])))
    return bed_dict


def out(bed_dict, infile, outfile, statfile):
    in_bed = defaultdict(int)
    not_in_bed = defaultdict(int)

    with open(infile, 'r') as fr, open(outfile, 'w') as fw:
        head = fr.readline().strip().split('\t')
        head.insert(1, 'mutation in bed')
        fw.write('{}\n'.format('\t'.join(head)))

        for line in fr:
            tag = 'not in bed'
            linelist = line.strip('\n').split('\t')[0:10]
            _chr = linelist[1]
            start1 = int(linelist[2])
            end1 = int(linelist[3])

            sub_bed_dict = bed_dict[_chr]
            for (start2, end2) in sub_bed_dict:
                if is_overlap(_chr, start1, end1, start2, end2):
                    tag = 'in bed'
                    in_bed[tag] += 1
                    break
                else:
                    not_in_bed[tag] += 1

            linelist.insert(1, tag)
            fw.write('{}\n'.format('\t'.join(linelist)))

    with open(statfile, 'w') as json_file:
        json_file.write(json.dumps(in_bed))
        json_file.write(json.dumps(not_in_bed))


if __name__ == '__main__':
    import sys
    bed_file = sys.argv[1]
    infile = sys.argv[2]
    outfile = sys.argv[3]
    statfile = sys.argv[4]

    bed_dict = get_bed_dict(bed_file)
    out(bed_dict, infile, outfile, statfile)
