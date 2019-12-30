uname=$1
pass=$2
ext=$3
out=$4

mkdir -p $out

scrapy crawl ibit_problems -a username=$uname -a password=$pass -a out_file=$out/ibit_problems.csv
scrapy crawl ibit_codes -a username=$uname -a password=$pass -a in_file=$out/ibit_problems.csv -a out_dir=$out -a ext=$ext