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
        for funcea in Functions(SegStart(ea)):
                funcname = GetFunctionName(funcea)
                if 'sub_' in funcname:
			fp.write(funcname + '\n')
    
if __name__ == "__main__":
	ea = FirstSeg()
	parser = argparse.ArgumentParser()
	parser.add_argument('--name', type=str, help='Match Type', required=True)
	args = parser.parse_args(args=idc.ARGV[1:])
	# Assign args to variables
	name = args.name
	get_funcnames(ea,name)
