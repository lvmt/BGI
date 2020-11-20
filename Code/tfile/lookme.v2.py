#!/usr/bin/env python
#-*- coding:utf-8 -*-


'''
文件转置脚本:
方便查看结果文件

# 输入文件
- 常规txt文件
- vcf文件

# 功能
- 转置前5行
- 指定分割符（默认tab）
- 转置指定列：数字 -c 1-6,8,9
- 转置指定列：名字
- 忽略指定字符开头的行.

# 美化可视化
'''



class LookFile(object):

    def __init__(self,args):
        self.infile = args.infile
        self.ignore = args.ignore
        self.sep = args.sep
        self.col = args.col # 列数
        self.title = args.title # 列名

    def safe_open(self, infile, mode='r'):
        if not infile.endswith('.gz'):
            return open(infile, mode)
        elif infile.endswith('.gz'):
            import gzip
            return gzip.open(infile, mode)
        else:
            exit('{} not exist'.format(infile))


    def get_head_index(self, headlist):
        '''将处理好的文件首行作为head
        '''
        index_head_dict = {}
        for index,item in enumerate(headlist):
            index_head_dict[item] = index

        return index_head_dict


    def handle_file(self):
        '''获取文件前5行
        '''
        content = []
        n = 0
        with self.safe_open(self.infile, 'r') as fr:
            for line in fr:
                if self.ignore:
                    if line.startswith(self.ignore):
                        continue
                    content.append(line.strip())
                else:
                    content.append(line.strip())
                n += 1
                if n == 5:
                    break
        return content


    def split_content(self, content):
        '''根据指定分割符分割文件.
        '''
        split_list = []
        for item in content:
            tmp = item.split(self.sep)
            split_list.append(tmp)

        return split_list


    def get_target_content(self, split_list):
        '''根据指定列数或者表头获取需要的列
        '''
        headlist = split_list[0] # 获取表头
        head_index = self.get_head_index(headlist)
        need_content = []

        need_cols = []
        if self.col: # 数字
            cols = self.col.split(',')
            for c in cols:
                if '-' in c:
                    start = int(c.split('-')[0])
                    end = int(c.split('-')[-1])
                    need_cols.extend([item-1 for item in range(start, end+1)]) # python starts 0.
                else:
                    need_cols.append(int(c)-1)

        if self.title: # 列名
            titles = self.title.split(',')
            for t in titles:
                need_cols.append(head_index[t])

        for linelist in split_list:
            tmp = [] # 嵌套列表
            for index,item in enumerate(linelist):
                if need_cols and index in need_cols:
                    tmp.append(item)
                elif not need_cols:
                    tmp.append(item)
            need_content.append(tmp)

        return need_content


    def print_content(self):
        content = self.handle_file()
        split_list = self.split_content(content)
        need_content = self.get_target_content(split_list)
        length = len(need_content[0])
        max_len = [max(map(len, i)) for i in need_content] # 记录原始文件,每一行的最大长度,转置后成为列的宽度.

        t = [ [row[i] for row in need_content] for i in range(length)] # 列表转置

        n = 1
        print('\033[1;31m-\033[0m'*(sum(max_len)+20))
        for item in t:
            print('{}\033[1;32m|\033[1;34m{}'.format(str(n).center(4), item[0].center(max_len[0]+2)), end='')
            for index,i in enumerate(item[1:]):
                c = max_len[index+1]
                print('\033[1;32m|\033[0m{}'.format(i.center(c+2)), end='')

            print('\033[1;32m|\033[0m')
            print('\033[1;31m-\033[0m'*(sum(max_len)+20))
            #print('\033[1;32m{} {:<30}\033[1;33m\t{:<20}\033[0m'.format(n, item[0], '||'.join(item[1:])))
            n += 1



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='\033[1;32mtransver result. {}\033[0m'.format(__doc__), formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('infile', help='the file to transver.')
    parser.add_argument('-g', '--ignore', help='omit line start with str.')
    parser.add_argument('-s', '--sep', help='the sep', default='\t')
    parser.add_argument('-c', '--col', help='which cols to look.like:4,5-9')
    parser.add_argument('-t', '--title', help='while col name to look')

    args = parser.parse_args()

    ll = LookFile(args).print_content()




