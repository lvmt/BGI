#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @Author lvmengting
# @Time   2020/12/15 14:35
# @Email  13554221497@163.com
# @File   make_rmsk_db.py.py


"""
将rmsk库文件整理为json, 存储在本地, 后续注释.
"""

from collections import defaultdict
from collections import namedtuple
from collections import OrderedDict
import json


def safe_open(filename, mode='r'):
    if not filename.endswith('.gz'):
        return open(filename, mode)
    else:
        import gzip
        return gzip.open(filename, mode)


rmsk_header = ['bin', 'swScore', 'milliDiv', 'milliDel', 'milliIns', 'genoName',
               'genoStart', 'genoEnd', 'genoLeft', 'strand', 'repName', 'repClass',
               'repFamily', 'repStart', 'repEnd', 'repLeft', 'id']


def file2dict(rmskfile):
    """
    Args:
        rmskfile: 
    Returns:
        chr1:[
        {'bin':'', 'swScore':123, ..},  # 每个小字典是一行数据.
        {'bin':13, 'swScore':245},
        ...],
        chr2:[
        ....
        ]
    """
    rmsk_dict = defaultdict(list)

    with safe_open(rmskfile, 'r') as fr:
        for line in fr:
            tmp = {}
            if line.startswith('#'):
                pass
            linelist = line.strip().split('\t')
            for index, item in enumerate(linelist):
                tmp[rmsk_header[index]] = item
            rmsk_dict[linelist[rmsk_header.index('genoName')]].append(tmp)
    return rmsk_dict


def dict2json(rmskdict, jsonfile):
    with open(jsonfile, 'w') as fw:
        fw.write(json.dumps(rmskdict, ensure_ascii=False, indent=4, separators=(',', ':')))


def json2dict(jsonfile):
    with open(jsonfile, 'r', encoding='utf-8') as fr:
        rmsk_dict = json.load(fr)
        return rmsk_dict


def main():
    rmsk_dict = file2dict(rmskfile)
    dict2json(rmsk_dict, outjson)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='change rmsk to json file.')
    parser.add_argument('--rmskfile', help='rmsk orgin file.')
    parser.add_argument('--outjson', help='output rmsk db json.')

    args = parser.parse_args()
    rmskfile = args.rmskfile
    outjson = args.outjson

    main()


    # dd = file2dict('rmsk_demo.txt')
    # # print(dd['chr1-27832-28014'])
    # dict2json(dd, 'db.json')
    # t = json2dict('db.json')
    # print('\033[1;32mjson文件转换为字典\033[0m')
    # print(t)


