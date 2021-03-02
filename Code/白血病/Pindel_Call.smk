#!/usr/bin/python3
# -*- coding:utf-8 -*-

rule Pindel_Call:
    input:
        Cbam = "{product}__{sample}/Cancer/4.MarkDup/{product}__{sample}__Cancer.markdup.bam",
        Nbam = "{product}__{sample}/Normal/4.MarkDup/{product}__{sample}__Normal.markdup.bam",
    output:
        case_pindel = "{product}__{sample}/Cancer/4.MarkDup/Pindel/{product}__{sample}_FLT3_TD.vcf",
        control_pindel = "{product}__{sample}/Normal/4.MarkDup/Pindel/{product}__{sample}_FLT3_TD.vcf",
    params:
        state = "{product}__{sample}.state"
        case_dir = "{product}__{sample}/Cancer/4.MarkDup/Pindel",
        control_dir = "{product}__{sample}/Normal/4.MarkDup/Pindel"
    resources:
        mem_mb = 2000
    shell:
        """
        echo -e "`date +"%Y-%m-%d %H:%M:%S"`\tCall_Pindel\tstart" >> {params.state}
        ## case pindel calling
        mkdir -p {params.case_dir}
        {config[conda][python]} pindel_sv.py --bam {input.Cbam}
        
        ## control pindel calling 
        mkdir -p {params.control_dir}
        {config[conda][python]} pindel_sv.py --bam {input.Nbam}
        
        echo -e "`date +"%Y-%m-%d %H:%M:%S"`\tCall_Pindel\tfinish" >> {params.state}
        """


