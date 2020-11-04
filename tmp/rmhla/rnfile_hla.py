#!/usr/bin/env python
#-*- coding:utf-8 -*-

'''
删除HLA中的无效小文件
## 删除内容包括：
1.shell脚本的标准错误输出，主目录 和 sh目录
2.每个L001目录下面的内容，暂时不知道删啥
'''


import glob


class RmHlaFile(object):

    def __init__(self,args):
        self.projdir = args['projdir']
        self.suffix = args['suffix'] or args['projdir'].split('/')[-1]
        self.libs = self.get_libs()
        self.e_list = []
        self.o_list = []
        self.sh_list = []
        self.other_list = []


    def get_libs(self):
        '''得到所有文库目录, absolute path
        '''
        tmp = glob.glob('{self.projdir}/p1*sh'.format(**locals()))
        libs = list([lib.replace('p1_', '').replace('.sh', '') for lib in tmp])
        return libs


    @staticmethod
    def get_o(dirname):
        o_list = glob.glob('{dirname}/*.sh.o*'.format(**locals()))
        return o_list

    @staticmethod
    def get_e(dirname):
        e_list = glob.glob('{dirname}/*.sh.e*'.format(**locals()))
        return e_list

    @staticmethod
    def get_sh(dirname):
        pass
    
    @staticmethod
    def get_other(lib,samid):
        '''获取每个文库待删除文件
        '''
        other_list = []
        rm_type = ['.fq', '.sam', '.bam', '.sai', '.bai']  # 删除每个目录的指定类型, 可根据实际自己选择
        dirname = '{lib}/fastq/{samid}'.format(**locals())
        
        for ty in rm_type:
            tmp = glob.glob('{dirname}/*{ty}'.format(**locals()))
            other_list.extend(tmp)

        return other_list


    def write_rmfile(self,ty,filelist):
        '''不同类型的待删除文件分开写出
        '''
        with open('{self.suffix}.{ty}.sh'.format(**locals()), 'w') as fw:
            for item in filelist:
                tmp = 'rm -rf {item}\n'.format(**locals())
                fw.write(tmp)

    def start(self):

        # 获取所有的.e文件
        dirname_e_projdir = self.projdir
        dirname_e_sh = '{self.projdir}/sh'.format(**locals())

        self.e_list.extend(self.get_e(dirname_e_projdir))
        self.e_list.extend(self.get_e(dirname_e_sh))
        self.write_rmfile('e',self.e_list)
        
        # 获取所有的.o文件
        self.o_list.extend(self.get_o(dirname_e_projdir))
        self.o_list.extend(self.get_o(dirname_e_sh))
        self.write_rmfile('o', self.o_list)

        # 获取每个文库待删除文件
        samids = map(str,range(1,97))
        samids = ['L' + item.rjust(3, '0') for item in samids]

        for lib in self.libs:
            for samid in samids:
                self.other_list.extend(self.get_other(lib,samid))
        self.write_rmfile('other', self.other_list)



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='remove hla nouse file.')
    parser.add_argument('--projdir', help='project dir')
    parser.add_argument('--suffix', help='suffix of output file.')

    args = vars(parser.parse_args())
    print(args)

    rr = RmHlaFile(args)
    #rr.start()


    

