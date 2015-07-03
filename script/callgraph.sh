#!/bin/bash

#./callgraph.sh /home/qian/code_search/crossarch/idb/coreutil_i386_o3_idb/
sample_dir=$1
echo $sample_dir
cd $sample_dir
rm $sample_dir/*.id0
rm $sample_dir/*.id1
rm $sample_dir/*.til
rm $sample_dir/*.nam
for file in $sample_dir/*
do
	filename="${file##*/}"
	echo $filename
	cd /home/qian/data/mcsema/
	opt -dot-callgraph /home/qian/data/mcsema/$filename".bc"
	mv /home/qian/data/mcsema/callgraph.dot /home/qian/data/mcsema/$filename.dot
done
