from idautils import *
from idaapi import *
from idc import *
def processDataSegs():
	funcdata = {}
	datafunc = {}
	for n in xrange(idaapi.get_segm_qty()):
		seg = idaapi.getnseg(n)
		ea = seg.startEA
		segtype = idc.GetSegmentAttr(ea, idc.SEGATTR_TYPE)
		if segtype in [idc.SEG_DATA, idc.SEG_BSS]:
			start = idc.SegStart(ea)
			end = idc.SegEnd(ea)
			cur = start
			while cur <= end:
				refs = [v for v in DataRefsTo(cur)]
				for fea in refs:
					name = GetFunctionName(fea)
					if name not in funcdata:
						funcdata[name] = [cur]
					else:
						funcdata[name].append(cur)
					if cur not in datafunc:
						datafunc[cur] = [name]
					else:
						datafunc[cur].append(name)
				cur = NextHead(cur)
	return funcdata, datafunc
