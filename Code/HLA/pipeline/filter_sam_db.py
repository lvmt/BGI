#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @Author lvmengting
# @Time   2020/12/23 16:27
# @Email  13554221497@163.com
# @File   filter_sam_db.py


region = {
    'A-E1': [75, 861],
    'A-E3': [989, 1391],
    'A-E4': [1819, 2223],
    'A-E5': [2203, 3136],

}

sub SNP_NUMBER()
{
	my $MD = shift;
	my $N = 0;
	my @field = split //,$MD;
	for(my $i=0;$i<@field;$i++)
	{
		if($field[$i]=~/\d/) ## number
		{
			next;
		}
		elsif($field[$i]=~/\^/)
		{
			while($i+1 <@field && $field[$i+1]=~/\w/)
			{
				$i++;
			}
		}
		else
		{
			$N++;
		}
	}
	return $N;
}