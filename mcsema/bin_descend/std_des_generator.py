from idautils import *
from idaapi import *
from idc import *
import argparse
def obtainExternFunctions():
	exfunclist = []
	for n in xrange(idaapi.get_segm_qty()):
		print n
		seg = idaapi.getnseg(n)
		start = seg.startEA
		segname = idc.SegName(start)
		if segname == 'extern':
			cur = start
			end = seg.endEA
			while cur <= end:
				externfunc = GetFunctionName(cur)
				if '@' in externfunc:
					externfunc = externfunc.split('@')[0]
					exfunclist.append(externfunc)
				else:
					exfunclist.append(externfunc)
				cur = NextHead(cur)
	return exfunclist

def writeStd_defs(fp):
	exfunclist = obtainExternFunctions()
	for funcname in exfunclist:
		fp.write(funcname + ' 12 C N\n')
	fp.close()

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
    	parser.add_argument("--batch", help="Indicate the script is running in batch mode", action="store_true",default=False)
    	parser.add_argument("-o", "--path", type=argparse.FileType('wb'),default=None, help="The output control flow graph recovered from this file")
	args = parser.parse_args(args=idc.ARGV[1:])
	fp = args.path
	writeStd_defs(fp)
	idc.Exit(0)
	
