#!/usr/bin/env python
#-*- coding:utf-8 -*- 

from collections import defaultdict
import pandas as pd



class AnnoSite(object):

    def __init__(self,args):
        self.snp = args['snp']
        self.snp_result = args['snp_result']
        self.out = args['out']

        self.snp_dict = self.get_snp_dict()
        self.anno_dict = self.get_snp_anno_dict()

    def get_snp_dict(self):
        '''每个分型结果，对应的突变
        部分位置存在2种类型的突变
        {
            510: ['A'],
            680: ['C', 'T']
        }
        '''
        snp_dict = defaultdict(set)
        with open(self.snp, 'r') as fr:
            for line in fr:
                k,v = line.strip().split(':')
                snp_dict[k].add(v)
        return snp_dict

    def get_snp_anno_dict(self):
        '''分析中产生的snp文件,
        该文件包含了系列信息
        {
            510: {
                'var': 'A', 'qual': 255, 'depth': 300,
                'A': 100, 'T': 50, 'G': 50, 'C': 100
            }
            
        
        }
        '''

        anno_dict = defaultdict(dict)
        with open(self.snp_result, 'r') as fr:
            for line in fr:
                linelist = line.strip().split('\t')
                pos = str(linelist[0])
                ref = {linelist[1]}
                var = set(linelist[3].split('/')) - ref
                var = list(var)
                qual = linelist[5]
                depth = linelist[6]
                A = linelist[7]
                T = linelist[8]
                C = linelist[9]
                G = linelist[10]
                #exon = item[11] 
                anno_dict[pos] = {
                    'var': var,
                    'qual': qual,
                    'depth': depth,
                    'A': A,
                    'T': T,
                    'C': C,
                    'G': G
                }
        return anno_dict

    def anno(self):
        '''利用snp_dict里面的位置信息及变异信息,
        提取snp_anno_dict里面的信息
        '''
        anno_result = defaultdict(dict)
        
        for pos in self.snp_dict:  # 遍历库文件位点信息
            anno_result[pos] = {
                        'var': '',
                        'qual': '',
                        'depth': '',
                        'read': '',
                        'bak': ''
                    }
            if pos in self.anno_dict:
                print(pos)
                if self.anno_dict[pos]['var'] in self.snp_dict[pos]:    # 库文件和此次检出结果是否一致
                    print('\033[1;32mYES\033[0m')
                    anno_result[pos]['var'] = self.anno_dict[pos]['var']
                    anno_result[pos]['qual'] = self.anno_dict[pos]['qual']
                    anno_result[pos]['depth'] = self.anno_dict[pos]['depth']
                    anno_result[pos]['read'] = self.anno_dict[pos][self.anno_dict[pos]['var']]
                else:
                    print('\033[1;33mNo\033[0m')
                    anno_result[pos]['qual'] = self.anno_dict[pos]['qual']
                    anno_result[pos]['depth'] = self.anno_dict[pos]['depth']
                    anno_result[pos]['read'] = self.anno_dict[pos][self.anno_dict[pos]['var']]
                    anno_result[pos]['var'] = 'ori:{}|mut:{}'.format(self.snp_dict[pos], self.anno_dict[pos]['var'])
                    anno_result[pos]['bak'] = '变异类型不一致,read为此次检出结果的reads.ori：库文件碱基, mut：此次检测结果.'
            else:
                anno_result[pos]['var'] = self.snp_dict[pos]
                anno_result[pos]['bak'] = '库文件中该位点此次未检出.'
            print(anno_result[pos])
            print('===================')

        return anno_result


    def output(self):
        '''输出结果保存
        '''
        anno_result = self.anno()


        with open(self.out, 'w') as fw:
            fw.write('pos\tvarType\tqual\tdepth\tread\t备注信息\n')
            for pos in anno_result:
                fw.write('{}\t{}\t{}\t{}\t{}\t{}\n'.format(pos, 
                                                   anno_result[pos]['var'], 
                                                   anno_result[pos]['qual'],
                                                   anno_result[pos]['depth'],
                                                   anno_result[pos]['read'],
                                                   anno_result[pos]['bak']))



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='extract information.')

    parser.add_argument('--snp', help='snp site.')
    parser.add_argument('--snp_result', help='snp result file while project.')
    parser.add_argument('--out', help='output file.')
    args = vars(parser.parse_args())

    aa = AnnoSite(args)
    aa.get_snp_anno_dict()
    aa.output()
    print(aa.snp_dict)
    # print(aa.snp_dict)
    # print(aa.anno_dict)
    # print(aa.anno())

