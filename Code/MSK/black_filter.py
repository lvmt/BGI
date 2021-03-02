#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @Author lvmengting
# @Time   2020/12/15 15:20
# @Email  13554221497@163.com
# @File   black_filter.py


"""
rmsk, encode数据库过滤
"""


import json
from collections import OrderedDict


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


def is_overlap(start1, end1, start2, end2, cutoff):
    """
    Args:
        start1: from rmsk database
        end1: from rmsk database
        start2: from input file
        end2: from input file
        cutoff: float, overlap/(end2-start2) > cutoff, think is a valid overlap

    Returns:
        True or False
    """

    rmsk_region = (i for i in range(int(start1), int(end1)+1))
    input_region = (i for i in range(int(start2), int(end2)+1))
    intersection = set(rmsk_region) & set(input_region)

    if len(intersection) / (int(end2) - int(start2) + 1) >= cutoff:
        return True
    return False


def anno_rmsk(infile, rmsk_dict, cutoff):
    """
    Args:
        infile: 待过滤的文件
        rmsk_dict: rmsk 库
        cutoff:

    Returns:
        infile.fail_rmsk  # 区间和rmsk叠合, 且repclass的tag为:Simple_repeat or Low_complexity
        infile.pass_rmsk  # 不在rmsk区间内

    """
    with open(infile, 'r') as fr, open(infile+'.fail_rmsk', 'w') as fw_fail,\
         open(infile+'.pass_rmsk', 'w') as fw_pass:
        for line in fr:
            if line.startswith('#'):
                head = line.strip()
                fw_fail.write('{}\trmsk_class\n'.format(head))
                fw_pass.write('{}\trmsk_class\n'.format(head))
                head_index_dict = head_index(head)
                continue
            linelist = line.strip().split('\t')
            _chr = linelist[head_index_dict['chr']]
            start2 = linelist[head_index_dict['start']]
            end2 = linelist[head_index_dict['end']]

            repclass = '.'
            sub_rmsk_dict = rmsk_dict[_chr]
            for d in sub_rmsk_dict:
                start1 = d['genoStart']
                end1 = d['genoEnd']
                if is_overlap(start1, end1, start2, end2, cutoff):
                    repclass = d['repClass']
                    break  # 找到一个就跳出循环

            linelist.append(repclass)
            if not repclass in ('Simple_repeat', 'Low_complexity'):
                fw_pass.write('{}\n'.format('\t'.join(linelist)))
            else:
                fw_fail.write('{}\n'.format('\t'.join(linelist)))


def anno_encode(infile, encode_dict, cutoff):
    """
    Args:
        infile: 需要进行过库的文件,
        encode_dict: encode 黑名单数据库
        cutoff: 阈值,同anno_rmsk

    Returns:
        infile.fail_encode
        infile.pass_encode

    """
    with open(infile, 'r') as fr, open(infile+'.fail_encode', 'w') as fw_fail,\
        open(infile+'.pass_encode', 'w') as fw_pass:
        for line in fr:
            if line.startswith('#'):
                head = line.strip()
                fw_fail.write('{}\tencode_blacklist\n'.format(head))
                fw_pass.write('{}\tencode_blacklist\n'.format(head))
                head_index_dict = head_index(head)
                continue
            linelist = line.strip().split('\t')
            _chr = linelist[head_index_dict['chr']]
            start2 = linelist[head_index_dict['start']]
            end2 = linelist[head_index_dict['end']]

            sub_encode_dict = encode_dict[_chr]
            encode_tag = '.'
            for d in sub_encode_dict:
                start1 = d['start']
                end1 = d['end']
                if is_overlap(start1, end1, start2, end2, cutoff):
                    encode_tag = d['anno']
                    break

            linelist.append(encode_tag)
            if encode_tag == '.':  # 表明不在encode blacklist中.
                fw_pass.write('{}\n'.format('\t'.join(linelist)))
            else:
                fw_fail.write('{}\n'.format('\t'.join(linelist)))



def main():
    rmsk_dict = get_database(rmsk_json)
    encode_dict = get_database(encode_json)

    anno_rmsk(annofile, rmsk_dict, cutoff)
    anno_encode(annofile+'.pass_rmsk', encode_dict, cutoff)  # 顺序注释的话, 只针对第一步的pass文件进行.



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='anno rmsk database')
    parser.add_argument('--annofile', help='the filt_var file.')
    # parser.add_argument('--outfile', help='output file, add repclass tag.')
    parser.add_argument('--rmsk_db', help='rmsk database file, json file.')
    parser.add_argument('--encode_db', help='rmsk database file, json file.')
    parser.add_argument('--cutoff', help='design the cutoff value of overlap.',
                        type=float, default=0.5)
    args = parser.parse_args()

    rmsk_json = args.rmsk_db
    encode_json = args.encode_db

    annofile = args.annofile
    cutoff = args.cutoff

    main()


    # encode_dict = get_database('encode_db.json')
    # anno_encode('filt_variation', encode_dict, 0.1)

