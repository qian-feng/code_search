#!/bin/bash
sample_dir="/home/qian/code_search/crossarch/idb/coreutil_i386_o3_idb/*"
echo $sample_dir
cd /home/qian/code_search/crossarch/idb/coreutil_i386_o3_idb
rm /home/qian/code_search/crossarch/idb/coreutil_i386_o3_idb/*.id0
rm /home/qian/code_search/crossarch/idb/coreutil_i386_o3_idb/*.id1
rm /home/qian/code_search/crossarch/idb/coreutil_i386_o3_idb/*.til
rm /home/qian/code_search/crossarch/idb/coreutil_i386_o3_idb/*.nam
for file in $sample_dir
do
	mkdir /home/qian/data/mcsema/IR/dug
	mkdir /home/qian/data/mcsema/IR/seq
	
	echo $file
	filename="${file##*/}"
	cd /home/qian/code_search/ida-6.6
	./idaq -S"/home/qian/svn/code_search/mcsema/bin_descend/func_extractor.py --batch --name=/home/qian/data/mcsema/funclist/$filename" $file
	./idaq -S"/home/qian/code_search/mcsema-master/mc-sema/bin_descend/get_cfg.py --batch --std-defs /home/qian/std_defs.txt --exports-to-lift /home/qian/data/mcsema/funclist/$filename --output /home/qian/data/mcsema/$filename.cfg" $file
	rm /home/qian/code_search/crossarch/idb/coreutil_i386_idb/*.id0
	rm /home/qian/code_search/crossarch/idb/coreutil_i386_idb/*.id1
	rm /home/qian/code_search/crossarch/idb/coreutil_i386_idb/*.til
	rm /home/qian/code_search/crossarch/idb/coreutil_i386_idb/*.nam
	cd /home/qian/code_search/mcsema-master/build/mc-sema/bitcode_from_cfg
	./cfg_to_bc -i /home/qian/data/mcsema/$filename".cfg" -o /home/qian/data/mcsema/$filename".bc" -ignore-unsupported
	cd /home/qian/code_search/mcsema-master/build/llvm-3.5/bin
	opt -load /home/qian/code_search/mcsema-master/build/Hello/libLLVMPassname.so -mem2reg -dce -die -dse -memcpyopt -loop-simplify -indvars  -constmerge -constprop -instcombine -hello < /home/qian/data/mcsema/$filename".bc" > /dev/null
	cd /home/qian/data/mcsema/IR
	mkdir $filename
	mv dug ./$filename
	mv seq ./$filename
done
