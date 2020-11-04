#!/usr/bin/env python
#-*- coding:utf-8 -*-

'''处理HLA结果文件
'''

import glob
import os
import argparse
import pandas
import textwrap


def check_dir(dirname):
    if os.path.exists(dirname):
        return True
    else:
        return False


def mkdir(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)


'''获取所有的HLA exom 文件
'''
def get_HLAexomfile(projdir):

    exom_files = glob.glob('{projdir}/*/exon_num.txt'.format(**locals()))
    flowcell = projdir.rsplit('/', 1)[-1]
    exom_result_dir = '{projdir}/{flowcell}_exom_file'.format(**locals())
    mkdir(exom_result_dir)

    if exom_files:
        for exom_file in exom_files:
            libid = exom_file.split('/')[-2]
            os.system('scp {exom_file} {projdir}/{libid}/{libid}_exon_num.txt'.format(**locals()))
            os.system('scp {projdir}/{libid}/{libid}_exon_num.txt {exom_result_dir}'.format(**locals()))
    else:
        exit('please check : No exom file')



'''check b2 exon 手动 
参数： result文件下面的xlsx

'''

def get_single_excel(resultfile, typename):
    '''从结果文件中获取每种类型单独的结果文件
    A,B,D。。。
    返回值是pandas Dataframe
    '''
    type_info_dict = {
        'A': 'HLA-A',
        'B': 'HLA-B',
        'C': 'HLA-C',
        'D': 'HLA-DRB1',
        'Q': 'HLA-DQB1'
    }

    sheetname = type_info_dict[typename]
    single_excel = pandas.read_excel(resultfile, sheet_name=sheetname)
    return single_excel


def get_single_lib_index(single_excel):
    '''从single_excel文件中提取b2标签信息
    (libid, samid, gene)
    '''
    lib_index_list = []
    
    for item in single_excel.values:  # 返回数组，每个item是每行的值
        if item[4] == 'b2':
            libid = item[0]
            samid = item[1]
            genename = item[5].split('*')[0]
            # tmp = '{libid}_{samid}_{genename}'.format(**locals())
            lib_index_list.append((libid,samid,genename))
    return lib_index_list


def get_all_snpfile(single_excel,projdir,typename=None,):
    '''获取某种类型的b2 snp文件
    typename: A,B,C,D,E
    '''
    snpfiles = []
    lib_index_list = get_single_lib_index(single_excel)

    for item in lib_index_list:
        libid,samid,genename = item
        if not typename:
            tmp = glob.glob('{projdir}/{libid}/fastq/{samid}/{genename}-E*.snp'.format(**locals()))
        elif typename in ('A','B','C','D','Q'):
            tmp = glob.glob('{projdir}/{libid}/fastq/{samid}/{typename}-E*.snp'.format(**locals()))
        else:
            exit('wrong typename {typename}')
        snpfiles.extend(tmp)
    return snpfiles


def write_single_result(single_excel,projdir,typename):
    '''按照HLA_A基因类型输出结果
    '''
    flowcell = projdir.split('/')[-1]
    resultdir = '{projdir}/{flowcell}_HLAb2_check'.format(**locals())
    #resultdir = '{projdir}/20HLA028P_HLAb2_check_test'.format(**locals())
    mkdir(resultdir)

    with open('{resultdir}/{typename}_b2_.xls'.format(**locals()), 'w') as fw:
        title = '\t'.join(map(str,
                                    ['samplename',
                                     'position',
                                     'base1',
                                     'base2',
                                     'base/base',
                                     'qc1',
                                     'qc2',
                                     'depth',
                                     'A_num',
                                     'T_num',
                                     'C_num',
                                     'G_num',
                                     'exon']))
        fw.write(title + '\n')
        snpfiles = get_all_snpfile(single_excel,projdir,typename)
        for snpfile in snpfiles:
            with open(snpfile,'r') as fr:
                tmp_list = snpfile.split('/')
                gene = tmp_list[-1].split('.')[0]
                samid = tmp_list[-2]
                libid = tmp_list[-4]
                flowcell = tmp_list[-5]
                sampelname = '_'.join([flowcell, libid, samid, gene])
                for line in fr:
                    linelist = line.strip().split('\t')
                    if linelist[11] == '0':
                        continue
                    if int(linelist[4]) < 120 or int(linelist[5]) < 120 or int(linelist[6]) < 50:
                        tmp = '{0}\t{1}\n'.format(sampelname,line[0:-2].strip())
                        fw.write(tmp)


def HLAb2_check(resultfile,projdir):
    for typename in ['A','B','C','D','Q']:
        single_excel = get_single_excel(resultfile,typename)
        write_single_result(single_excel,projdir,typename)


'''result.combined
'''
def get_type_result_combined(projdir):
	
    type_result_combined_files = glob.glob('{projdir}/*/fastq/L*/type.result.combined'.format(**locals()))
    text = ''

    for combine_file in type_result_combined_files:
        tmp = ''
        with open(combine_file, 'r') as fr:
            tmp_list = combine_file.split('/')
            for line in fr:
                linelist = line.strip().split('\t')
                if line.startswith('A') and len(line) > 2:
                    tmp += linelist[1] + ' ' + linelist[3]
                    if 'A*24:353' in (linelist[1], linelist[3]) and 'A*24:02' in tmp:
                        text += tmp_list[-4] + '\t' + tmp_list[-2] + '\t' + line

    
    flowcell = projdir.split('/')[-1]
    with open('{projdir}/{flowcell}_result_combine.xls'.format(**locals()), 'w') as fw:
        fw.write(text)

	

'''combine snp file
'''
def get_hla_snp(projdir):
    flowcell = projdir.split('/')[-1]
    outdir = '{projdir}/{flowcell}/snp_bias_file'.format(**locals())
    mkdir(outdir)

    snp_files_list = glob.glob('{projdir}/*/total.type.result.final')
    libids = [snp_file.split('/')[-2] for snp_file in snp_files_list]
    
    for libid in libids:
        cmd = textwrap.dedent('''
        /ifs9/BC_B2C_01A/B2C_Cancer/PIPELINE/Software/anaconda3/bin/python /ifs7/B2C_Cancer/USER/zhougengmin/HLA/HLAsnp_statistics.py\
            -d {projdir}/{libid}
        '''.format(**locals()))
        os.system(cmd)

        
        os.system('mv {projdir}/HLA_{flowcell}_*.xls {outdir}'.format(**locals()))



def main():
    if args['checkb']:
        HLAb2_check(args['resultfile'], args['projdir'])
    if args['handexon']:
        get_HLAexomfile(args['projdir'])
    if args['combine']:
        get_type_result_combined(args['projdir'])
    if args['snp']:
        get_hla_snp(args['projdir'])

    

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='step5')
    
    parser.add_argument('--projdir', help='project dir')
    parser.add_argument('--resultfile', help='result/*xlsx')
    parser.add_argument('--checkb', action='store_true', help='if check b2 or not')
    parser.add_argument('--handexon', action='store_true', help='if cp exon')
    parser.add_argument('--combine', action='store_true', help='if combie file')
    parser.add_argument('--snp', action='store_true', help='if move snp stat')


    args = vars(parser.parse_args())
    print(args)

    main()
