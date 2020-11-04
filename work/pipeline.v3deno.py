#!/usr/bin/env python
#-*- coding:utf-8 -*-

'''HLA主流程脚本 demo
# add job control
'''

import textwrap
import os 
import time
import subprocess
from utils import get_info_dict
from utils import mkdir,write_shell


class HLA(object):
    
    def __init__(self,args):
        self.args = args
        self.projdir = self.args['projdir'] 
        self.idfile = self.args['idfile']
        self.samsfile = self.args['samsfile']

        self.info_dict = get_info_dict(self.idfile,self.samsfile)
        
    
    @staticmethod
    def can_qsub_job(jobcmd):
        '''判断job是否可以进行投递，
        因为qsub投递系统的限制，每个账号最多可以投递1500个job，
        我们是每次投递一个job，所以只需要判断当前有多少个job在节点上。
        jobcmd = 'qsub -cwd -l vf=2g,p=1 -hold_jid {orders} -P B2C_HLA {shellname}'
        '''
        now_job_nums = subprocess.getoutput('qstat -u HLApub | wc -l')
        if now_job_nums < 1400:
            os.system(jobcmd)
        else:
            time.sleep(3600)
            HLA.can_qsub_job(jobcmd)


    def get_step1_shell(self,libid):
        '''得到第一步脚本
        '''
        fq1 = self.info_dict[libid]
        fq2 = fq1.replace('1.fq.gz', '2.fq.gz')

        cmd = textwrap.dedent('''
        #! /bin/sh
        #...........................part1 of HLA................................
        # Usage: 1. Filter raw data
        #	2. split a lane sequences into every index
        #	3. statistic data volume
        
        echo "start time: " `date`

        perl /ifs9/BC_B2C_01A/B2C_Common/HLA/HST_MGI/bin/raw_reads_filter_v0.2.pl \\
            {fq1} \\
            {fq2} \\
            1 15 \\
            {self.projdir}/{libid}/new_filter_1.fq \\
            {self.projdir}/{libid}/new_filter_2.fq \\
            > {self.projdir}/{libid}/statistic.txt &&\\

        /ifs9/BC_B2C_01A/B2C_Common/HLA/HST_MGI/bin/sample_grouping_gz \\
            -a {self.projdir}/{libid}/new_filter_1.fq \\
            -b {self.projdir}/{libid}/new_filter_2.fq \\
            -i /ifs9/BC_B2C_01A/B2C_Common/HLA/HST_MGI/database/index/index.index \\
            -o {self.projdir}/{libid} &&\\

        perl /ifs9/BC_B2C_01A/B2C_Common/HLA/HST_MGI/bin/statistic_ip.pl \\
            {self.projdir}/{libid}/ip.txt \\
            /ifs9/BC_B2C_01A/B2C_Common/HLA/HST_MGI/database/N.relation.txt \\
            100 6500 \\
            {self.projdir}/{libid}/exon_num.txt \\
            >> {self.projdir}/{libid}/statistic.txt &&\\

        perl /ifs9/BC_B2C_01A/B2C_Common/HLA/HST_MGI/bin/mv_data.pl \\
            /ifs9/BC_B2C_01A/B2C_Common/HLA/HST_MGI/database/N.relation.txt \\
            {self.projdir}/{libid}/fastq 


        echo "end time: " `date`        
        '''.format(**locals()))

        return cmd

    
    def get_step2_shell(self,libid,samid):
        cmd = textwrap.dedent('''
        #$ -S /bin/bash 
        #!/bin/sh
        ##HLA_analysis Pipeline 2010-5-30
        ###################################
        ##This program can be used to call 
        ##the HLA type from solexa sequence
        ## write at: 2010-5-30
        ## Change to PE pipeline at: 2010-6-1 
        ## Change pipeline to A,B,C,D for gene type
        ##################################

        #################################################################
        ## 100 bp snp number statistic
        ##	Exon	Average	Max
        ##	A-E2	8	18
        ##	A-E3	10	14
        ##	A-E4	6	10
        ##	B-E2	11	21
        ##	B-E3	8	13
        ##	B-E4	2	10
        ##	C-E2	7	10
        ## 	C-E3	5	8
        ##  C-E4	4	7
        ##  D-E2	10	16
        ##	Q-E2	16	20
        ##	Q-E3	4	7
        #################################################################
        
        echo "start time: " `date`
        dir={self.projdir}/{libid}
        path=/ifs9/BC_B2C_01A/B2C_Common/HLA/HST_MGI/pipeline
        cd $path
        bin=/ifs9/BC_B2C_01A/B2C_Common/HLA/HST_MGI/bin
        database=/ifs9/BC_B2C_01A/B2C_Common/HLA/HST_MGI/database

        i=$dir/fastq/{samid}
        for j in A-E1 A-E3 A-E4 A-E5 B-E1 B-E3 B-E4 B-E5 C-E1 C-E3 C-E4 C-E5 D-E1 D-E2 D-E3 Q-E2 Q-E3;do
            perl $bin/Reduce_pe_index_primer.pl $i/$j.ip $i/${{j}}_1.fq $i/${{j}}_2.fq $i/${{j}}_1.new.fq $i/${{j}}_2.new.fq
            ############decide which reference should it use ###############
            prefix=`echo $j | awk -F '-' '{{print $1}}'`
            reference=$database/ref/$prefix.fa

            $bin/bwa aln -l 31 -t 2 -k 10 -q 15 -n 25 $reference $i/${{j}}_1.new.fq > $i/${{j}}_1.sai 2>/dev/null
            $bin/bwa aln -l 31 -t 2 -k 10 -q 15 -n 25 $reference $i/${{j}}_2.new.fq > $i/${{j}}_2.sai 2>/dev/null
            $bin/bwa sampe $reference $i/${{j}}_1.sai $i/${{j}}_2.sai $i/${{j}}_1.new.fq $i/${{j}}_2.new.fq > $i/$j.sam 2>/dev/null
            perl $bin/filter_sam_new4.pl $i/$j.sam > $i/$j.sam.filter
            $bin/samtools view -u -b -S -t $reference.fai $i/$j.sam.filter > $i/$j.bam 2>/dev/null
            $bin/samtools sort $i/$j.bam $i/$j.bam 2>/dev/null
            $bin/samtools index $i/$j.bam.bam

            if [[ "$j" =~ "C" ]];then
                java -jar $bin/GenomeAnalysisTK.jar -T RealignerTargetCreator -l INFO -I $i/$j.bam.bam -R $reference -o $i/$j.realign.intervals
                java -jar $bin/GenomeAnalysisTK.jar -T IndelRealigner -l INFO -I $i/$j.bam.bam -R $reference -targetIntervals $i/$j.realign.intervals -o $i/$j.realign.bam
                $bin/samtools sort $i/$j.realign.bam $i/$j.realign.bam 2>/dev/null
                $bin/samtools index $i/$j.realign.bam.bam
                $bin/samtools pileup -c -r 0.15 -T 0.87 -f $reference $i/$j.realign.bam.bam > $i/$j.consence
            else
                $bin/samtools pileup -c -r 0.15 -T 0.87 -f $reference $i/$j.bam.bam > $i/$j.consence
            fi

            perl $bin/abstract_snpV8.pl $i/$j.consence > $i/$j.snp
            perl $bin/HLA_Divider.graph2.pl $i/$j.snp $i/$j.sam.filter
        done

        for j in A-E1 A-E2 A-E3 A-E4 A-E5 A-E6 A-E7 B-E1 B-E2 B-E3 B-E4 B-E5 B-E6 B-E7 C-E1 C-E2 C-E3 C-E4 C-E5 C-E6 C-E7 D-E1 D-E2 D-E3 Q-E2 Q-E3;do
            prefix=`echo $j | awk -F '-' '{{print $1}}'`
            reference=$database/ref/$prefix.fa

            for h in $i/$j.hap*.sam;do
                $bin/samtools view -u -b -S -t $reference.fai $h > $h.bam 2>/dev/null
                $bin/samtools sort $h.bam $h.bam 2>/dev/null
                $bin/samtools index $h.bam.bam

                if [[ "$j" =~ "C" ]];then
                    java -jar $bin/GenomeAnalysisTK.jar -T RealignerTargetCreator -l INFO -I $h.bam.bam -R $reference -o $h.realign.intervals
                    java -jar $bin/GenomeAnalysisTK.jar -T IndelRealigner -l INFO -I $h.bam.bam -R $reference -targetIntervals $h.realign.intervals -o $h.realign.bam
                    $bin/samtools sort $h.realign.bam $h.realign.bam 2>/dev/null
                    $bin/samtools index $h.realign.bam.bam
                    $bin/samtools pileup -c -T 0.87 -N 1 -f $reference $h.realign.bam.bam > $h.consence
                else
                    $bin/samtools pileup -c -T 0.87 -N 1 -f $reference $h.bam.bam > $h.consence
                fi
            done
            
            perl $bin/decide_right_typeV2.pl $reference $database/snp_type/$j.sam.index $i/$j.right.final $i/$j.hap*.consence >$i/$j.type
        done

        perl $bin/Decide_type_3.pl $i/A-E*.type  $i/B-E*.type $i/C-E*.type $i/D-E*.type $i/Q-E2.type $i/Q-E3.type  $database/snp_type > $i/type.result
        perl $bin/recombination_type.pl $database/all_exon_same.type $i/type.result
        perl $bin/validation_type_4.pl -out $i/type.result.check -dir $i
        perl $bin/check.filter.pl $i/type.result.combined $i/type.result.check $i/type.result.check.filter
        perl $bin/Filter_result_add_rare2.pl $database/rare_allele_20180416 $database/Missing_allele_201705 $i/type.result.check.filter $i/type.result.final

        echo "end time:" `date`
        '''.format(**locals()))

        return cmd


    def get_step3_shell(self,libid):
        
        cmd = textwrap.dedent('''
        #! /bin/sh
        #...........................part3 of HLA................................
        # Usage: 1. cat all sample of index to a file
        #	2. validate the hla result (give a tag:TRUE/FALSE)
        #	3. change format
        #	4. remove some intermediate files
        
        echo "start time: " `date`

        tail {self.projdir}/{libid}/fastq/L*/type.result.final > {self.projdir}/{libid}/total.type.result.final &&\\

        perl /ifs9/BC_B2C_01A/B2C_Common/HLA/HST_MGI/bin/name_all_add_id.pl \\
            {self.projdir}/{libid}/total.type.result.final \\
            {self.projdir}/{self.samsfile} \\
            {libid} \\
            {self.projdir}/{libid}/name_all.results \\
            {self.projdir}/{libid}/name_all.temp.results &&\\

        perl /ifs9/BC_B2C_01A/B2C_Common/HLA/HST_MGI/bin/add_tag_on_resultV3.pl \\
            {self.projdir}/{libid}/name_all.temp.results \\
            /ifs9/BC_B2C_01A/B2C_Common/HLA/HST_MGI/database/add_test.txt \\
            {self.projdir}/{libid}/add_tag.result &&\\

        perl /ifs9/BC_B2C_01A/B2C_Common/HLA/HST_MGI/bin/output_split.pl \\
            {self.projdir}/{libid}/add_tag.result \\
            {self.projdir}/{self.samsfile} \\
            {libid} \\
             {self.projdir}/{libid} &&\\
        
        for ty in b c d e;do
            sort +4 -5 {self.projdir}/{libid}/tag_${{ty}}_results > {self.projdir}/{libid}/temp
            mv {self.projdir}/{libid}/temp {self.projdir}/{libid}/tag_${{ty}}_results
        done

        perl /ifs9/BC_B2C_01A/B2C_Common/HLA/HST_MGI/bin/No_result_judge.pl \\
            {self.projdir}/{libid} &&\\

        awk '{{if(NF>17 && $0!~/L01[12]/) print $0}}' {self.projdir}/{libid}/exon_num.txt \\
            > {self.projdir}/figure/{libid}_exom_num
        
        find {self.projdir}/{libid}/fastq/L*/?-E?.consence \\
            > {self.projdir}/figure/{libid}.consence

        perl /ifs9/BC_B2C_01A/B2C_Common/HLA/HST_MGI/bin/depth_sta_V1.pl \\
            {self.projdir}/figure/{libid}.consence \\
            {self.projdir}/figure &&\\

        perl /ifs9/BC_B2C_01A/B2C_Common/HLA/HST_MGI/bin/snp_bias_sta.pl \\
            {self.projdir}/{libid} \\
            {self.projdir}/{libid}/snp_bias_sta.txt \\
            >> {self.projdir}/{libid}/snp_bias.txt
       
        echo "end time: " `date`
        '''.format(**locals()))
        
        return cmd

    
    def get_step4_shell(self):
        libids = self.info_dict.keys()
        all_figures = ['{}/figure/{}'.format(self.projdir,libid) for libid in libids]
        all_figures = " ".join(all_figures)
        libids = " ".join(libids)

        cmd = textwrap.dedent('''
        echo "start time: " `date`

        perl /ifs9/BC_B2C_01A/B2C_Common/HLA/HST_MGI/bin/cat_index_results_V2.pl \\
            {self.projdir} \\
            {libids} &&\\

        perl /ifs9/BC_B2C_01A/B2C_Common/HLA/HST_MGI/bin/C_checkV3.pl \\
            {self.projdir} &&\\

        perl /ifs9/BC_B2C_01A/B2C_Common/HLA/HST_MGI/bin/Check_DRB1.pl \\
            {self.projdir} &&\\

        perl /ifs9/BC_B2C_01A/B2C_Common/HLA/HST_MGI/bin/abstract_InDel2.pl \\
            {self.projdir}/*/fastq/L*/*.consence \\
            {self.samsfile} \\
            > {self.projdir}/result/all.InDel.txt &&\\

        /ifs9/BC_B2C_01A/B2C_Common/HLA/HST_MGI/bin/Rscript /ifs9/BC_B2C_01A/B2C_Common/HLA/HST_MGI/bin/read_num_png.R \\
            {self.projdir}/figure/*.exon_num \\
            {self.projdir}/figure &&\\

        perl /ifs9/BC_B2C_01A/B2C_Common/HLA/HST_MGI/bin/intergratefile.pl \\
            {self.projdir}/*/statistic.txt &&\\

        /ifs9/BC_B2C_01A/B2C_Common/HLA/HST_MGI/bin/Rscript /ifs9/BC_B2C_01A/B2C_Common/HLA/HST_MGI/bin/depth_figure_V2.R \\
            {all_figures} \\
            {self.projdir}/figure

        echo "end time: " `date`
        '''.format(**locals()))

        return cmd

    
    def get_step5_shell(self):

        flowcell = self.projdir.split('/')[-1]
        cmd = textwrap.dedent('''
        echo "start time: " `date`

        python /ifs7/B2C_Cancer/USER/zhougengmin/HLA/get_HLAexomfile.py \\
            -d {self.projdir} &&\\

        /ifs9/BC_B2C_01A/B2C_Cancer/PIPELINE/Software/anaconda3/bin/python /ifs7/B2C_Cancer/USER/zhougengmin/HLA/HLAb2_check.v0.1.py \\
            -i {self.projdir}/result/{flowcell}.xlsx \\
            -d {self.projdir}  &&\\

        cat {self.projdir}/result/all_a_results >> /zfsyt1/B2C_COM_P1/B2C_BACKUP/HLA/HLA2019_lane_result/2019_all_a_results &&\\

        python /ifs7/B2C_Cancer/USER/wanglinlin/python/get_type.result.combined_v0.1.py \\
            -i {self.projdir} &&\\

        python /ifs7/B2C_Cancer/USER/zhougengmin/HLA/HLA_snp.py \\
            -d {self.projdir} &&\\

        mv snp_bias_file {flowcell}_snp_bias_file 
        zip -r {flowcell}_snp_bias_file.zip {flowcell}_snp_bias_file 
        zip -r {flowcell}_exom_file.zip {flowcell}_exom_file
        
        echo "end time: " `date`
        '''.format(**locals()))
        
        return cmd


    def start(self):
        
        jobname1 = []
        jobname2 = []
        jobname3 = []
        jobname4 = []

        mkdir('{self.projdir}/sh'.format(**locals()))
        for libid in self.info_dict.keys():
            subdir = '{self.projdir}/{libid}'.format(**locals())
            mkdir(subdir)
            print('\033[1;32mlibid >>> {libid}\033[0m'.format(**locals()))

            ##step1
            cmd = self .get_step1_shell(libid)
            shellname = '{self.projdir}/p1_{libid}.sh'.format(**locals())
            write_shell(cmd,shellname)
            # os.system('qsub -cwd -l vf=5g,p=1 -P B2C_HLA {shellname}'.format(**locals()))
            jobcmd = 'qsub -cwd -l vf=5g,p=1 -P B2C_HLA {shellname}'.format(**locals())
            HLA.can_qsub_job(jobcmd)

            jobname_tmp1 = os.path.basename(shellname)
            jobname1.append(jobname_tmp1)

            ## step2
            for i in range(1,97):
                samid = str(i).rjust(3,'0')
                samid = 'L' + samid
                print('\033[1;33m\tsamid >>> {samid}\033[0m'.format(**locals()))
                cmd = self.get_step2_shell(libid,samid)
                shellname = '{self.projdir}/sh/p2_{libid}_{samid}_type.sh'.format(**locals())
                write_shell(cmd,shellname) 
                orders = ",".join(jobname1)
                # os.system('qsub -cwd -l vf=2g,p=1 -hold_jid {orders} -P B2C_HLA {shellname}'.format(**locals()))
                jobcmd = 'qsub -cwd -l vf=2g,p=1 -hold_jid {orders} -P B2C_HLA {shellname}'.format(**locals())
                HLA.can_qsub_job(jobcmd)
                
                jobname_tmp2 = os.path.basename(shellname)
                jobname2.append(jobname_tmp2)
            
            ## step3
            cmd = self.get_step3_shell(libid)
            shellname = '{self.projdir}/p3_{libid}.sh'.format(**locals())
            write_shell(cmd,shellname)
            orders = ",".join(jobname1 + jobname2)
            #os.system('qsub -cwd -l vf=2g,p=1 -hold_jid {orders} -P B2C_HLA {shellname}'.format(**locals()))
            jobcmd = 'qsub -cwd -l vf=2g,p=1 -hold_jid {orders} -P B2C_HLA {shellname}'.format(**locals())
            HLA.can_qsub_job(jobcmd)
            jobname_tmp3 = os.path.basename(shellname)
            jobname3.append(jobname_tmp3)

        ## step4
        cmd = self.get_step4_shell()
        shellname = '{self.projdir}/p4_cat_all_result.sh'.format(**locals())
        write_shell(cmd,shellname)

        orders = ",".join(jobname1 + jobname2 + jobname3)
        #os.system('qsub -cwd -l vf=2g,p=1 -hold_jid {orders} -P B2C_HLA {shellname}'.format(**locals()))
        jobcmd = 'qsub -cwd -l vf=2g,p=1 -hold_jid {orders} -P B2C_HLA {shellname}'.format(**locals())
        HLA.can_qsub_job(jobcmd)
        jobname_tmp4 = os.path.basename(shellname)
        jobname4.append(jobname_tmp4)

        # step5
        cmd = self.get_step5_shell()
        shellname = '{self.projdir}/p5_get_additional_result.sh'.format(**locals())
        write_shell(cmd,shellname) 

        orders = ",".join(jobname1 + jobname2 + jobname3 + jobname4)
        #os.system('qsub -cwd -l vf=2g,p=1 -hold_jid {orders} -P B2C_HLA {shellname}'.format(**locals()))
        jobcmd = 'qsub -cwd -l vf=2g,p=1 -hold_jid {orders} -P B2C_HLA {shellname}'.format(**locals())
        HLA.can_qsub_job(jobcmd)

        #print(jobname1)
        #print(jobname2)
        #print(jobname3)
        #print(jobname4)

    

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='HLA pipeline demo')
    
    parser.add_argument('--idfile', help='libid')
    parser.add_argument('--samsfile', help='samsfile info')
    parser.add_argument('--projdir', help='projdir')
    
    args  =vars(parser.parse_args())
    
    ss = HLA(args)
    ss.start()
    
