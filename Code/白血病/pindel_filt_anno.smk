#!/usr/bin/python3
# -*- coding:utf-8 -*-

rule Pindel_filt_anno:
    input:
        case_vcf = "{product}__{sample}/Cancer/4.MarkDup/Pindel/{product}__{sample}_FLT3_TD.vcf",
        control_vcf = "{product}__{sample}/Normal/4.MarkDup/Pindel/{product}__{sample}_FLT3_TD.vcf",
    output:
        case_pindel_filt = "{product}__{sample}/Cancer/4.MarkDup/Pindel/{product}__{sample}_FLT3_TD.filter.vcf",
        control_pindel_filt = "{product}__{sample}/Normal/4.MarkDup/Pindel/{product}__{sample}_FLT3_TD.filter.vcf",
        case_pindel_anno = "{product}__{sample}/Cancer/4.MarkDup/Pindel/{product}__{sample}_FLT3_TD.filter.vcf.vepanno",
        control_pindel_anno = "{product}__{sample}/Normal/4.MarkDup/Pindel/{product}__{sample}_FLT3_TD.filter.vcf.vepanno",
    resources:
        mem_mb = 2000
    params:
        state = "{product}__{sample}.state"
    shell:
        """
        echo -e "`date +"%Y-%m-%d %H:%M:%S"`\tCall_Pindel_filt_anno\tstart" >> {params.state}
        ## case pindel filt and anno
        {config[conda][python]} FLT3_ITD_Filter.py --tag filter --vcf {input.case_vcf} 
        
        ## control pindel filt and anno
        {config[conda][python]} FLT3_ITD_Filter.py --tag filter --vcf {input.control_vcf} 
        
        # case anno
        {config[conda][python]} FLT3_ITD_Filter.py --tag anno --vcf {input.case_vcf}
        
        # control anno
        {config[conda][python]} FLT3_ITD_Filter.py --tag anno --vcf {input.control_vcf}
        
        echo -e "`date +"%Y-%m-%d %H:%M:%S"`\tCall_Pindel_filt_anno\tfinish" >> {params.state}
        """