#./ida.sh o0
v=$1
target_dir="/home/qian/code_search/crossarch/coreutil_i386_"$v"_strip"
source_dir="/home/qian/code_search/crossarch/coreutil_i386_$v"
test=/home/qian/code_search/crossarch/coreutil_i386_$v\_strip/*
rm -r $target_dir
cd $source_dir
rm $source_dir/*.id0
rm $source_dir/*.idb
rm $source_dir/*.id1
rm $source_dir/*.til
rm $source_dir/*.nam
mkdir $target_dir
cp $source_dir/* $target_dir/
ida_dir="/home/qian/code_search/ida-6.6"
cd $ida_dir
for f in $test
do
	filename="${f##*/}"
	echo $filename
	mv $f $f\_i386_$v\_strip
	strip -s $f\_i386_$v\_strip
	./idaq -B $f\_i386_$v\_strip
	
done
mv $target_dir/*.idb /home/qian/code_search/crossarch/idb/coreutil_i386_$v\_idb
