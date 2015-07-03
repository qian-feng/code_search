#!/bin/bash
_base="/home/qian/data/mcsema/IR/*"
ida_dir="/home/qian/code_search/ida-6.6"
cd $ida_dir
for f in $_base
do
	filename="${f##*/}"
	rm /home/qian/code_search/crossarch/idb/coreutil_i386_o0_idb/$filename
	
done

