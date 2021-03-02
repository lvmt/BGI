#!/usr/bin/perl

=pod
利用函数, 批量处理文件的读取工作
=cut

# use strict;
sub read_file{
    $file_name = @_[0];
    $tmp = @_[1];

    print "argument: \033[1;32m$file_name, $tmp\n\033[0m";

    if($file_name =~ 'gz$'){
        open($tmp, "gzip -dc $file_name|") or die $!;
    } else{
        open($tmp, $file_name) or die $!;
    }

    return $tmp;
}


$read1 = &read_file('test1.fq', 'tmp1');  # 返回句柄文件
$read2 = &read_file('test2.fq', 'tmp2');

@file1 = <$read1>;
@file2 = <$read2>;

print "文件1的内容：@file1\n";
print "文件2的内容：@file2\n";

