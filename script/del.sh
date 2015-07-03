#!/bin/bash
sample_dir="/home/qian/data/mcsema/IR/*"
cd /home/qian/data/mcsema/IR
SIZE=12
for file in $sample_dir
do
	CHECK=$(du -sb $file | cut -f1)
	filename="${file##*/}"
	if [ "$CHECK" -lt "12289" ]; then
		 if [[ `echo $filename||grep 'o0'` ]];then
   			echo rm -r $file
 		 fi
	fi

done
