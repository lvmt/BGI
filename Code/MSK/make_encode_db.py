#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @Author lvmengting
# @Time   2020/12/15 14:35
# @Email  13554221497@163.com
# @File   make_encode_db.py.py


"""
将encode 黑名单库文件整理为json, 存储在本地, 后续注释.
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


encode_header = ['chr', 'start', 'end', 'anno', 'score', 'other']



def file2dict(encodefile):
    """

    Args:
        encodefile:  encode blacklist

    Returns:


    """
    encode_dict = defaultdict(list)

    with safe_open(encodefile, 'r') as fr:
        for line in fr:
            tmp = {}
            if line.startswith('#'):
                pass
            linelist = line.strip().split('\t')
            for index, item in enumerate(linelist):
                tmp[encode_header[index]] = item
            encode_dict[linelist[encode_header.index('chr')]].append(tmp)
    return encode_dict


def dict2json(encode_dict, jsonfile):
    with open(jsonfile, 'w') as fw:
        fw.write(json.dumps(encode_dict, ensure_ascii=False, indent=4, separators=(',', ':')))


def json2dict(jsonfile):
    with open(jsonfile, 'r', encoding='utf-8') as fr:
        encode_dict = json.load(fr)
        return encode_dict


def main():
    encode_dict = file2dict(encodefile)
    dict2json(encode_dict, outjson)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='change rmsk to json file.')
    parser.add_argument('--encodefile', help='encode blacklist file.')
    parser.add_argument('--outjson', help='output encode db json.')

    args = parser.parse_args()
    encodefile = args.encodefile
    outjson = args.outjson

    main()

    #
    # dd = file2dict('encode_blacklist.txt')
    # # print(dd['chr1-27832-28014'])
    # dict2json(dd, 'db.json')
    # t = json2dict('db.json')
    # print('\033[1;32mjson文件转换为字典\033[0m')
    # print(t)
    #

