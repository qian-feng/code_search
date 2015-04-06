#!/bin/bash

_base="/home/qian/code_search/crossarch/coreutil_mips_g"
ida_dir="/home/qian/code_search/ida-6.6"
cd $ida_dir
for f in $_base/*
do
	filename="${f##*/}"
	echo $f
	./idaq -A -S"/home/qian/code_search/callgraph_based_matching.py \
	--exename $filename --mod start \
	--home-dir /home/qian/code_search/crossarch/coreutil_mips_gt/" $f
	
done
