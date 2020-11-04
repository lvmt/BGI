#!/ifs9/BC_B2C_01A/B2C_Cancer/PIPELINE/Software/anaconda3/bin/python
#-*- coding:utf-8 -*-

import os
## 

def mkdir(dirname):
    if os.path.exists(dirname):
        pass
    else:
        os.mkdir(dirname)


def write_shell(cmd, shellname):
    with open(shellname, 'w') as fw:
        fw.write(cmd)


## 处理输入文件
def hand_sams_file(samsfile):
    '''
    处理sams文件，得到字典
    '''
    sams_dict = {}
    with open(samsfile, 'r') as fr:
        for line in fr:
            linelist = line.strip().split('\t')
            libid = linelist[3]  # 20GSK139-1
            num = linelist[3].split('-')[-1]
            k = '{}_{}'.format(linelist[2], num) # L02_1
            sams_dict[k] = libid
    
    return sams_dict
          

def hand_id_file(idfile):
    '''处理sams文件，得到字典
    '''
    id_dict = {}
    with open(idfile,'r') as fr:    
        for line in fr:
            line = line.strip() #/ifs9/zebra/MGISEQ-2000/100400180007/V300071039/L02/V300071039_L02_7_1.fq.gz
            k = line.split('_',1)[-1].replace('_1.fq.gz', '') # L02_1
            id_dict[k] = line
        
    return id_dict


def get_info_dict(idfile,samsfile):
    '''根据文库文件和sample文件得到二者的对应字典关系
    info_dict = {
        libid: 'fastq'
    }
    '''
    
    sams_dict = hand_sams_file(samsfile)
    id_dict = hand_id_file(idfile)
    
    info_dict = [(sams_dict[k],id_dict[k]) for k in id_dict.keys()]
    return dict(info_dict)
  
  
if __name__ == '__main__':
    
    import sys
    idfile = sys.argv[1]
    samsfile = sys.argv[2]
    
    print(get_info_dict(idfile, samsfile))

