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
import networkx as nx
import cfg_constructor as cfg
import cPickle as pickle
import pdb
#import wingdbstub
#wingdbstub.Ensure()

def get_funcs(ea):
        funcs = {}
        # Get current ea
        # Loop from start to end in the current segment
	for funcea in Functions(SegStart(ea)):
		funcname = GetFunctionName(funcea)
		func = get_func(funcea)
		blocks = FlowChart(func)
		funcs[funcname] = []
		for bl in blocks:
		        start = bl.startEA
		        end = bl.endEA
		        funcs[funcname].append((start, end))
        return funcs

def get_func_names(ea):
    funcs = {}
    for funcea in Functions(SegStart(ea)):
            funcname = GetFunctionName(funcea)
            funcs[funcname] = funcea
    return funcs

def get_func_bases(ea):
        funcs = {}
        for funcea in Functions(SegStart(ea)):
                funcname = GetFunctionName(funcea)
                funcs[funcea] = funcname
        return funcs

def get_func_range(ea):
        funcs = {}
        for funcea in Functions(SegStart(ea)):
                funcname = GetFunctionName(funcea)
		func = get_func(funcea)
                funcs[funcname] = (func.startEA, func.endEA)
        return funcs

def get_func_sequences(ea):
	funcs_bodylist = {}
	funcs = get_funcs(ea)
	for funcname in funcs:
		if funcname not in funcs_bodylist:
			funcs_bodylist[funcname] = []
		for start, end in funcs[funcname]:
			inst_addr = start
			while inst_addr <= end:
				opcode = GetMnem(inst_addr)
				funcs_bodylist[funcname].append(opcode)
				inst_addr = NextHead(inst_addr)
        return funcs_bodylist

def get_func_cfgs(ea):
    func_cfglist = {}
    i = 0
    for funcea in Functions(SegStart(ea)):
        funcname = GetFunctionName(funcea)
        func = get_func(funcea)
        print i
        i += 1
        try:
            icfg = cfg.cfg_construct(func)
            func_cfglist[funcname] = icfg
        except:
            pass
            
    return func_cfglist

def get_func_cfg_sequences(func_cfglist):
    func_cfg_seqlist = {}
    for funcname in func_cfglist:
        func_cfg_seqlist[funcname] = {}
        cfg = func_cfglist[funcname][0]
        for start, end in cfg:
            codesq = get_sequences(start, end)
            func_cfg_seqlist[funcname][(start,end)] = codesq

    return func_cfg_seqlist


def get_sequences(start, end):
    seq = []
    inst_addr = start
    while inst_addr <= end:
        opcode = GetMnem(inst_addr)
        seq.append(opcode)
        inst_addr = NextHead(inst_addr)
    return seq

def get_stack_arg(func_addr):
    print func_addr
    args = []
    stack = GetFrame(func_addr)
    if not stack:
            return []
    firstM = GetFirstMember(stack)
    lastM = GetLastMember(stack)
    i = firstM
    while i <=lastM:
        mName = GetMemberName(stack,i)
        mSize = GetMemberSize(stack,i)
        if mSize:
                i = i + mSize
        else:
                i = i+4
        if mName not in args and mName and ' s' not in mName and ' r' not in mName:
            args.append(mName)
    return args

        #pickle.dump(funcs, open('C:/Documents and Settings/Administrator/Desktop/funcs','w'))
        
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
                    if len(name)== 0:
                        continue
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

def obtainDataRefs(callgraph):
    datarefs = {}
    funcdata, datafunc = processDataSegs()
    for node in callgraph:
        if node in funcdata:
            datas = funcdata[node]
            for dd in datas:
                refs = datafunc[dd]
                refs = list(set(refs))
                if node in datarefs:
                    print refs
                    datarefs[node] += refs
                    datarefs[node] = list(set(datarefs[node]))
                else:
                    datarefs[node] = refs
    return datarefs


