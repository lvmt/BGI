#!/usr/bin/env python
#-*- coding:utf-8 -*-


'''发送邮件提醒任务是否顺利完成
'''

import os
import textwrap

def check_file(resultfile):
    if os.path.exists(resultfile):
        return True
    return False


def sendemail(projdir, name):
    
    fenqi = projdir.split('/')[-1]
    
    result = '{projdir}/release/{name}.{fenqi}.xlsx'.format(**locals())
    exom = '{projdir}/release/{name}.{fenqi}_exom_file.zip'.format(**locals())
    snp = '{projdir}/release/{name}.{fenqi}_snp_bias_file.zip'.format(**locals())
    combine = '{projdir}/release/{name}.{fenqi}_result_combined.xls'.format(**locals())

    job_status = {}
    
    job_status['result'] = True if check_file(result) else False
    job_status['exom'] = True if check_file(exom) else False
    job_status['snp'] = True if check_file(snp) else False
    job_status['combine'] = True if check_file(combine) else False

    if all(job_status.values()):
        mail_title = 'HLA结果文件: {name}'.format(**locals())
        #receiver = 'lvmengting@genomics.cn wanglinlin1@genomics.cn'
        receiver = 'lvmengting@genomics.cn zhangliming@genomics.cn liangyingmin@genomics.cn yanhong@genomics.cn '
        mail_body = textwrap.dedent('''<h3 style="color:red"> hi, all:</h3>
                      <br>
                      <p style="font:bold">
                      <br>
                      此次分析结果见附件,
                      </p>'''.format(**locals()))
    else:
        mail_title = 'HLA结果文件: 【项目失败】'
        receiver = 'lvmengting@genomics.cn'
        mail_body = textwrap.dedent('''<h2 style="color:red"> 抱歉,项目失败，请及时check</h2> 
                       <br> 
                       <p style="font:bold">项目目录：{projdir}</p>'''.format(**locals()))
        result = snp = exom = combine = None
    cmd = textwrap.dedent('''
    /ifs9/B2C_COM_P1/PROJECT/HLA/WORK/lmt/Code/email/sendEmail \
        -f  lvmengting@genomics.cn \
        -t {receiver} \
        -s 192.168.59.6 \
        -u {mail_title} \
        -o message-content-type=html \
        -o message-charset=utf-8 \
        -m "{mail_body}" \
        -a  {result} {snp} {exom} {combine} \
		-cc wurh@genomics.cn chaixianghua@genomics.cn yunlili@genomics.cn shaominghui@genomics.cn zhangcaifen@genomics.cn huangxiaoyan@genomics.cn yangxiaoqin@genomics.cn wanglinlin1@genomics.cn 

    '''.format(**locals()))

    if not all(job_status.values()):
        cmd = cmd.split('-a')[0]
    os.system(cmd)


def main():
    projdir = args['projdir']
    name = args['name']
    sendemail(projdir,name)



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='sendemail to minitor project')
    parser.add_argument('--projdir', help='the project dir')
    parser.add_argument('--name', help='the suffix name of result')
    #parser.add_argument('--receiver', help='the receiver,default=lvmengting@genomics.cn', default='lvmengting@genomics.cn')

    args = vars(parser.parse_args())
    main()
