from idautils import *
from idaapi import *
from idc import *
import argparse
def obtainExternFunctions():
	exfunclist = []
	for n in xrange(idaapi.get_segm_qty()):
		seg = idaapi.getnseg(n)
		start = seg.startEA
		segname = idc.SegName(start)
		if segname == 'extern':
			cur = start
			end = seg.endEA
			while cur <= end:
				externfunc = getFunctionName(cur)
				if '@' in externfunc:
					externfunc = externfunc.split('@')[0]
					exfunclist.append(externfunc)
	return exfunclist

def writeStd_defs(filepath):
	fp = open(filepath, 'w')
	exfunclist = obtainExternFunctions()
	for funcname in exfunclist:
		fp.write(funcname + ' 3 C N\n')
	fp.close()

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Process some integers.')
	parser.add_argument('--path', metavar='N', type=str, nargs='+',
                   help='the std_defs filepath')

	args = parser.parse_args()
	filepath = args.path
	writeStd_defs(filepath)
	
