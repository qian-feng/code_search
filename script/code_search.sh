exeg1="coreutil_i386_o3"
exeg2="coreutil_i386_o0"
g1="coreutil_i386_o3_gt"
g2="coreutil_i386_o0_gt"
sg1="coreutil_i386_o3_strip_gt"
sg2="coreutil_i386_o0_strip_gt"
strip1_idb="base64_i386_o3_strip.idb"
strip2_idb="base64_i386_o0_strip.idb"
strip1="coreutil_i386_o3_strip"
strip2="coreutil_i386_o0_strip"
sample_dir1="/home/qian/code_search/crossarch/idb/coreutil_i386_o3_idb/*"
sample_dir2="/home/qian/code_search/crossarch/idb/coreutil_i386_o0_idb/*"

rm /home/qian/code_search/crossarch/coreutil_i386_o3/*.id0
rm /home/qian/code_search/crossarch/coreutil_i386_o3/*.id1
rm /home/qian/code_search/crossarch/coreutil_i386_o3/*.til
rm /home/qian/code_search/crossarch/coreutil_i386_o3/*.nam
rm /home/qian/code_search/crossarch/coreutil_i386_o3/*.asm
rm /home/qian/code_search/crossarch/coreutil_i386_o3/*.idb

rm /home/qian/code_search/crossarch/coreutil_i386_o0/*.id0
rm /home/qian/code_search/crossarch/coreutil_i386_o0/*.id1
rm /home/qian/code_search/crossarch/coreutil_i386_o0/*.til
rm /home/qian/code_search/crossarch/coreutil_i386_o0/*.nam
rm /home/qian/code_search/crossarch/coreutil_i386_o0/*.asm
rm /home/qian/code_search/crossarch/coreutil_i386_o0/*.idb

rm /home/qian/code_search/crossarch/coreutil_i386_o3_strip/*.id0
rm /home/qian/code_search/crossarch/coreutil_i386_o3_strip/*.id1
rm /home/qian/code_search/crossarch/coreutil_i386_o3_strip/*.til
rm /home/qian/code_search/crossarch/coreutil_i386_o3_strip/*.nam
rm /home/qian/code_search/crossarch/coreutil_i386_o3_strip/*.asm
rm /home/qian/code_search/crossarch/coreutil_i386_o3_strip/*.idb

rm /home/qian/code_search/crossarch/coreutil_i386_o0_strip/*.id0
rm /home/qian/code_search/crossarch/coreutil_i386_o0_strip/*.id1
rm /home/qian/code_search/crossarch/coreutil_i386_o0_strip/*.til
rm /home/qian/code_search/crossarch/coreutil_i386_o0_strip/*.nam
rm /home/qian/code_search/crossarch/coreutil_i386_o0_strip/*.asm
rm /home/qian/code_search/crossarch/coreutil_i386_o0_strip/*.idb


#groundtruth collector
#/home/qian/svn/code_search/ida_feature/./feature_collector.sh $exeg1 $g1
#/home/qian/svn/code_search/ida_feature/./feature_collector.sh $exeg2 $g2
#/home/qian/svn/code_search/ida_feature/./feature_collector.sh $strip1 $sg1
#/home/qian/svn/code_search/ida_feature/./feature_collector.sh $strip2 $sg2

#generate idb for callgraph use
#/home/qian/svn/code_search/script/./idb.sh o0
#/home/qian/svn/code_search/script/./idb.sh o3

#generate callgraph.dot
#/home/qian/svn/code_search/script/./callgraph.sh /home/qian/code_search/crossarch/idb/coreutil_i386_o3_idb/
#/home/qian/svn/code_search/script/./callgraph.sh /home/qian/code_search/crossarch/idb/coreutil_i386_o0_idb/

#feature generation
for file in $sample_dir1
do
strip1_idb="${file##*/}"
echo $strip1_idb
python /home/qian/svn/code_search/LLVM_feature/llvm_ir_parser.py --dug_path=/home/qian/data/mcsema/IR/$strip1_idb/dug --target_path=/home/qian/data/BGM/IR/db/ --dot_path=/home/qian/data/mcsema/$strip1_idb.dot --exename=$strip1_idb
done
for file in $sample_dir2
do
strip2_idb="${file##*/}"
echo $strip2_idb
python /home/qian/svn/code_search/LLVM_feature/llvm_ir_parser.py --dug_path=/home/qian/data/mcsema/IR/$strip2_idb/dug0 --target_path=/home/qian/data/BGM/IR/test/ --dot_path=/home/qian/data/mcsema/$strip2_idb.dot --exename=$strip2_idb
done
#graph matching
#python /home/qian/svn/code_search/Context_based_match.py --configpath=/home/qian/svn/code_search/config --matchtype=start --start=0 --lenth=149 --scorelist_path=/home/qian/data/BGM/IR/output/

#cd /home/qian/code_search/ida-6.6
#./idaq -B -S"/home/qian/code_search/mcsema-master/mc-sema/bin_descend/get_cfg.py --batch --std-defs /home/qian/std_defs.txt --output /home/qian/data/mcsema/chown.cfg" /home/qian/code_search/crossarch/coreutil_i386_strip/chown_i386_strip
#cd /home/qian/code_search/mcsema-master/build/mc-sema/bitcode_from_cfg

