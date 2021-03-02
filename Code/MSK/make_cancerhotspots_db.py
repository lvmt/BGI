#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @Author lvmengting
# @Time   2020/12/16 15:06
# @Email  13554221497@163.com
# @File   make_cancerhotspots_db.py


"""
处理cancerhotspots.v2.maf.gz,得到库文件，
按照snp, indel分开保存.
"""


from collections import defaultdict
from collections import OrderedDict
import json


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


def file2dict(cancerhospot):
    """
    Args:
        cancerhospot:  *.gz

    Returns:
        snp_dict, indel_dict

    Examples:
        {'chr_start_ref_alt':  # 查询键
            {'gene': gene, 'strand':'+', 'Variant_Classification':'Missense_Mutation',
             'Reference_Allele':'A', 'Tumor_Seq_Allele1':'A', 'Tumor_Seq_Allele2':'T'},
        .....

        }

    """

    snp_dict = defaultdict(dict)
    indel_dict = defaultdict(dict)

    with open(cancerhospot, 'r') as fr:
        next(fr)
        header = next(fr)
        head_index_dict = head_index(header)
        for line in fr:
            linelist = line.strip().split('\t')
            ncbi_build = linelist[head_index_dict['ncbi_build']]  # reference version
            var_type = linelist[head_index_dict['variant_type']]  # SNP or INDEL
            _chr = linelist[head_index_dict['chromosome']]
            start = linelist[head_index_dict['start_position']]
            end = linelist[head_index_dict['end_position']]
            gene = linelist[head_index_dict['hugo_symbol']]
            strand = linelist[head_index_dict['strand']]
            func = linelist[head_index_dict['variant_classification']]
            ref = linelist[head_index_dict['reference_allele']]
            alt1 = linelist[head_index_dict['tumor_seq_allele1']]
            alt2 = linelist[head_index_dict['tumor_seq_allele2']]
            tmp = {
                    'var_type': var_type,
                    '_chr': _chr,
                    'start': start,
                    'end': end,
                    'gene': gene,
                    'strand': strand,
                    'func': func,
                    'ref': ref,
                    'alt1': alt1,
                    'alt2': alt2
                    }

            if ncbi_build == 'GRCh37' and var_type == 'SNP':
                snp_dict['{_chr}_{start}_{ref}_{alt2}'.format(**locals())] = tmp
            elif ncbi_build == 'GRCh37' and var_type in ('DEL', 'INS', 'DNP', 'TNP', 'ONP'):
                indel_dict['{_chr}_{start}_{ref}_{alt2}'.format(**locals())] = tmp
            else:
                print('not snp or indel', tmp)

    return snp_dict, indel_dict


def dict2json(a_dict, jsonfile):
    """
    Args:
        a_dict: snp_dict, indel_dict
        jsonfile: output json file.

    Returns:
        json file
    """
    with open(jsonfile, 'w') as fw:
        fw.write(json.dumps(a_dict, ensure_ascii=False, indent=4, separators=(',', ':')))


def main():
    snp_dict, indel_dict = file2dict(cancerhotspot)
    dict2json(snp_dict, cancerhot_snp_db)
    dict2json(indel_dict, cancerhot_indel_db)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='make cancerhotspot database json file.')
    parser.add_argument('--cancerhot', help='cancer hotspot file')
    parser.add_argument('--snp_db', help='output json database for snp.')
    parser.add_argument('--indel_db', help='output json database for indel.')

    args = parser.parse_args()

    cancerhotspot = args.cancerhot
    cancerhot_snp_db = args.snp_db
    cancerhot_indel_db = args.indel_db

    main()

