#
# Reference Lister
#
# List all functions and all references to them in the current section.
#
# Implemented with the idautils module
#
from idautils import *
from idaapi import *
from idc import *
import pdb
import argparse
#import wingdbstub
#wingdbstub.Ensure()

def get_funcnames(ea, name):
        fp = open(name, 'w')
	externs = obtainExtern()
        for funcea in Functions(SegStart(ea)):
		print funcea
		if contains(funcea, externs):
			continue
		print "out"
                funcname = GetFunctionName(funcea)
		fp.write(funcname + '\n')

def contains(funcea, externs):
	for ea in externs:
		end = externs[ea]
		if ea <= funcea <= end:
			return True
	return False

def obtainExtern():
	externs = {}
	for n in xrange(idaapi.get_segm_qty()):
        	seg = idaapi.getnseg(n)
		name = SegName(seg.startEA)
		if name == "extern" or name == ".plt":
			externs[seg.startEA] = seg.endEA
	return externs
    
if __name__ == "__main__":
	ea = FirstSeg()
	parser = argparse.ArgumentParser()
	parser.add_argument('--name', type=str, help='Match Type', required=True)
	parser.add_argument("--batch", help="Indicate the script is running in batch mode",action="store_true", default=False)
	args = parser.parse_args(args=idc.ARGV[1:])
	# Assign args to variables
	name = args.name
	#name = "/code_search/mcsema-master/build/mc-sema/bin_descend/funclist/basename"
	get_funcnames(ea,name)
	if args.batch:
        	idc.Exit(0)
