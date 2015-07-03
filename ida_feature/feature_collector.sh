#!/bin/bash

version=$1
gt=$2
_base="/home/qian/code_search/crossarch/$version"
ida_dir="/home/qian/code_search/ida-6.6"
cd $ida_dir
for f in $_base/*
do
	filename="${f##*/}"
	echo $f
	./idaq -A -S"/home/qian/svn/code_search/ida_feature/callgraph_based_matching.py \
	--exename $filename --mod start \
	--home-dir /home/qian/code_search/crossarch/$gt/" $f
	
done
