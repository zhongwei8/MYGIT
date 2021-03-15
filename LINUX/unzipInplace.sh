#!/bin/bash
###
 # @Author       :
 # @Date         : 2021-03-10 10:31:10
 # @LastEditors  :
 # @LastEditTime : 2021-03-10 10:31:33
 # @FilePath     : /my_github/LINUX/unzipInplace.sh
###
#Program
#Unzip from root
#Author: tzw
#History
# 2020/12/19 tzw first release

#PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
#export PATH

# 1) 参数检查
if [ $# -ne 1 ]; then
        echo "Please input a directory!"
        exit 1
fi

# 2) 接收路径参数，去除前后空格
root=$1
root=$(echo $root | awk '$1=$1')                        # 去掉前后空格

# 3) 检查目录是否存在
if [ ! -d "${root}" ]; then                             # -o 或运算符；-a 与运算符
        echo "The ${root} is NOT exist in your system."
        exit 1
fi

# 4) 搜索目录 root 下的所有 zip 文件，然后原地解压
zips=$(find ${root} -type f | grep -v .zip.zip | grep .zip)
for zip in ${zips}
do
        dir=$(dirname $zip)
        base=$(basename $zip .zip)                      # 以 zip 名为文件夹
        path=$dir/$base
        if [ ! -d $path ]; then
                mkdir $path
        fi
        unzip -o $zip -d $path > mylog.log              # -o 不必先询问用户，unzip 执行后覆盖原有文件；-j 不处理压缩文件中原有的目录路径
done

echo "succeed"
