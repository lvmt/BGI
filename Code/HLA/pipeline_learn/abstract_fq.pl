#!/usr/bin/perl
use Getopt::Long;

# help doc
=head1 DESCRIPTION

   This script is used to abstract target seq according to read name.

=head1 Usage

    perl $0 --name_file name_file --fq_file fq --out_fq out.fq

=head1 Parameters

    --name_file [str] file contain read name.
    --fq_file   [str] input fq file.
    --out_fq    [str] target fq output.
=cut


GetOptions(
    "name_file=s" => \$name_file, # 包含表头信息的文件
    "fq_file=s"   => \$fq_file,
    "out_fq=s"    => \$out_fq, #输出fq的名字.
);

die `pod2text $0` if(!$name_file);


sub get_name_array() {
    $file = shift;
    @name_array = ();
    open(IN, $file);
    while(<IN>){
        chomp($_);
        push @name_array, $_;
    }

    return @name_array;
}


sub in_name_array() {
    # 判断位点是否在name_array里面
    ($str, @name_array) = @_;  # 传递多个函数时, 这样才能正确的依次解包参数.
    # print("str, $str, @name_array\n");
    foreach(@name_array) {
        # print("_: $_\n");
        if($_ =~ /$str/) {
            return True
        }
    }
    return False
}


sub safe_open() {
    ($file_name, $tmp) = @_;
    if($file_name =~ '.gz') {
        open($tmp, "gzip -dc $file_name|") or die $!;
    } else {
        open($tmp, $file_name) or die $!;
    }
    return($tmp);
}


## 文件处理
@name_array = &get_name_array($name_file);
open(OFQ, ">$out_fq") or die;

$FQ = &safe_open($fq_file);
while(<$FQ>) {
    $name = $_;
    $seq = <$FQ>;
    $tag = <$FQ>;
    $qua = <$FQ>;
    $new_name = (split /\//, $name)[0];
    $new_name = (split /\@/, $new_name)[1];

    # print("new_name: $new_name\n");
    if(&in_name_array($new_name, @name_array) =~ True){
        print("\033[1;32min: $new_name\n\033[1;0m");
        print OFQ $name;
        print OFQ $seq;
        print OFQ $tag;
        print OFQ $qua;
    } else {
		#	print("not in: $new_name\n");
        next;
    }
}

# print("name_array: @name_array\n")

