from idautils import *
from idaapi import *
from idc import *
import copy
import networkx as nx
import cPickle as pickle
import cfg_constructor as cc

def forward_tracing(func_ea, root_reg):
    root_addr = 0
    insts = {}
    dug = {}
    dugs = {}
    dfgs = {}
    func = get_func(func_ea)
    cfg, start_node= cc.cfg_construct(func)
    bbs = pinpoint(root_reg, cfg)
    for bb, root_addr in bbs:
        #print root_addr
        #print root
        dug = gen_DUG(bb, root_reg, root_addr, cfg)
        dfg = gen_DFG(dug)
        #format_dot(dfg)
        insts = obtain_insts(dfg)
        #dugs[root_addr] = insts
        dfgs[root_addr] = dfg
    return dfgs
    #pickle.dump(insts, open('E:xp3.inst','w'))
    #pickle.dump(dug, open('E:xp3.dug','w'))

def obtain_insts(dfg):
    insts = {}
    for node in dfg:
        if type(0x80000000) != type(node) and type(4651009) != type(node):
        #if type(4651009) != type(node):
            insts[node] = node
        else:
            insts[node] = GetDisasm(node)
    return insts
        

def gen_DFG(dug):
    dfg = nx.DiGraph()
    for define in dug:
       for use in dug[define]:
            use_id = use[0]
            use_opcode = use[1]
            if define != use_id:
                dfg.add_edge(define, use_id, op = use_opcode)
    
    return dfg

def format_dot(dfg):
    fp =open('E:func1.dot','w')
    edges = dfg.edges(data=True)
    fp.write('digraph{\n')
    visited = {}
    for e in edges:
        #print e[0]
        if type(0x804F888A) != type(e[0]) and type(0x0062DA30) !=  type(e[0]):
            src_in = e[0]
        else:
            src_in = GetDisasm(e[0])
        src_out = GetDisasm(e[1])
        try:
            fp.write('"' + src_in + '"' + ' -> ' + '"' + src_out+ '"' + '[label=' + e[2]['op'] + '];\n')
        except:
            fp.write('"' + str(src_in) + '"' + ' -> ' + '"' + src_out+ '"' + '[label=' + e[2]['op'] + '];\n')
        #fp.write(str(e[0]) + ' -> ' + str(e[1]) + '[label=' + '"'+ e[2]['op'] + '"];\n')
    fp.write('}\n')
    fp.close()

def pinpoint(taint_v, cfg):
    bblist = []
    for bb in cfg:
        addr = bb[0]
        while addr <bb[1]:
            inst = GetDisasm(addr)
            if taint_v in inst:
                opcode = GetMnem(addr)
                src_reg, src_offset, src_type = parseInst(addr, 1)
                dst_reg_o, dst_offset, dst_type = parseInst(addr, 0)
                if opcode == 'call' or taint_v in inst:
                    bblist.append((bb, addr))
                if opcode == 'mov' and taint_v in GetOpnd(addr, 1):
                    bblist.append((bb, addr))
            addr = NextHead(addr)
    return list(set(bblist))


def gen_DUG(bb, root_reg, root_addr, cfg):
    UD_dic = initial_dic(root_addr)
    #taint_addr = NextHead(root_addr)
    forward_tainting(UD_dic, root_addr, bb, cfg, 0)
    return DU_dic

def initial_dic(addr):
    global DU_dic
    global UD_dic
    DU_dic = {}
    UD_dic = {}
    src_reg, src_offset, src_type = parseInst(addr, 1)
    dst_reg_o, dst_offset, dst_type = parseInst(addr, 0)
    if src_offset:
        #UD_dic[dst_reg_o] = addr
        UD_dic[src_reg] = src_offset
    else:
        src_offset = src_reg
        UD_dic[src_reg] = src_reg
    DU_dic[src_offset] = [(addr, 'mov', 'src')]
    return UD_dic


def forward_tainting(UD_dic, taint_addr, bb, cfg, depth):
        depth += 1
        do_block_forward(UD_dic, taint_addr, bb, cfg)
        if len(UD_dic) == 0:
                return
        if depth == 5:
                return
        else:
                suc_bbs = cfg.successors(bb)
                for sbb in suc_bbs:
                        cud_dic = copy.deepcopy(UD_dic)
                        forward_tainting(cud_dic, sbb[0], sbb, cfg, depth)



def do_block_forward(UD_dic, taint_addr, bb, cfg):
    inst_addr = taint_addr
    while inst_addr < bb[1] and len(UD_dic) != 0:
        #print inst_addr
        inst = GetDisasm(inst_addr)
        opcode = GetMnem(inst_addr)
        src_reg, src_offset, src_type = parseInst(inst_addr, 1)
        dst_reg_o, dst_offset, dst_type = parseInst(inst_addr, 0)
        #print inst_addr, src_reg, dst_reg_o
        if opcode == 'mov' and GetOpType(inst_addr, 0) == 1:
        #if opcode == 'mov':
            #print src_reg
            #print src_offset
            #print UD_dic
            #print DU_dic
            if src_reg in UD_dic:
                d_addr = UD_dic[src_reg]
                DU_dic[d_addr].append((inst_addr, opcode, 'src'))
                if dst_reg_o in UD_dic:
                    del UD_dic[dst_reg_o]
                    UD_dic[dst_reg_o] = inst_addr
                else:
                    UD_dic[dst_reg_o] = inst_addr
                DU_dic[inst_addr] = [(inst_addr, opcode, 'dst')]
            else:
                if dst_reg_o in UD_dic:
                    del UD_dic[dst_reg_o]
            #print DU_dic

        if opcode == 'call':
            if 'eax'in UD_dic:
                del UD_dic['eax']
        if opcode == 'push' and src_reg in UD_dic:
            d_addr = UD_dic[src_reg]
            DU_dic[d_addr].append((inst_addr, opcode))
            del UD_dic[src_type]
        if opcode == 'retn':
            return
        else:
            if src_reg in UD_dic:
                d_addr = UD_dic[src_reg]
                DU_dic[d_addr].append((inst_addr, opcode, 'src'))
            if dst_reg_o in UD_dic:
                d_addr = UD_dic[dst_reg_o]
                DU_dic[d_addr].append((inst_addr, opcode, 'dst'))
        inst_addr = NextHead(inst_addr)

def parseInst(addr, index):
	reg_o = GetOpnd(addr, index)
	if len(reg_o) == 0:
		return False, False, False
	if GetOpType(addr,index) in [3,4]:
		value = GetOpnd(addr, index)
		#print value
		if '+' in value:
			reg = value.split('[')[1].split('+')[0]
			offset_type = reg_o.split('+')[1].split(']')[0]
		elif '-' in value:
			reg = value.split('[')[1].split('-')[0]
			offset_type = reg_o.split('-')[1].split(']')[0]
		elif '[' in value:
			reg = value.split('[')[1].split(']')[0]
			offset_type = 0
		offset = hex(GetOperandValue(addr, index))
		offset_str = str(offset)[2:].upper()
		if '-' in value:
    			offset = hex(GetOperandValue(addr, index))
			if '+' not in value:
                            offset = changeNegative(offset)
                            offset_str = str(offset)[3:len(offset) - 1].upper()
		if offset_str in GetOpnd(addr, index):
			return reg, offset, 'c'
		else:
			return reg, offset_type, 'v'
	elif GetOpType(addr,index) in [5,6,7]:
		return reg_o, 0, 'cn'
	else:
		return reg_o, False, False

def changeNegative(value):
        value = value[0:len(value)-1]
        t = lambda x: int(x, 16) - ((int(x, 16) >> 31) * (2**32-1))
        return hex(t(value)-1)

def get_stack_arg(func_addr):
    args = []
    stack = GetFrame(func_addr)
    firstM = GetFirstMember(stack);
    lastM = GetLastMember(stack);
    i = firstM
    while i <=lastM:
        mName = GetMemberName(stack,i)
        mSize = GetMemberSize(stack,i)
        i = i + mSize
        if mName not in args:
            args.append(mName)
    return args

# extract offsets of obj from dug for statistic
def extract_offsets(dfgs):
    global data
    data = []
    for root_addr in dfgs:
        src_reg, src_offset, src_type = parseInst(root_addr, 1)
        dfg = dfgs[root_addr]
        taint_reg = src_reg
        print taint_reg, root_addr
        find_offsets(root_addr, dfg, [], taint_reg)

def find_offsets(root_addr, dfg, root_offsets, taint_reg):
        src_reg, src_offset, src_type = parseInst(root_addr, 1)
        dst_reg_o, dst_offset, dst_type = parseInst(root_addr, 0)
        opcode = GetMnem(root_addr)
        #print taint_reg, root_addr
        if taint_reg == src_reg and opcode == 'mov':
            #print root_offsets
            #if root_addr == 0xC107637B:
            #    print data
            #    print root_offsets
            data.append(root_offsets)
            taint_reg = dst_reg_o
            root_offsets.append(src_offset)
            sucs = dfg.successors(root_addr)
            print sucs, root_addr
            for s in sucs:
                if s == 0xC107637B:
                    print data
                    print root_offsets
                root_offsets_copy = copy.copy(root_offsets)
                root_addr = s
                find_offsets(root_addr, dfg, root_offsets_copy, taint_reg)
        else:
            if taint_reg == dst_reg_o:
                return




if __name__=="__main__":
    func_pattern = pickle.load(open('C:/Documents and Settings/Administrator/Desktop/func_patterns','r'))
    #func_ea = 0x8050AF1D
    #roots =[('DriverObject', 0x8050AF6D)]
    #func_ea = 0x804F14E1
    #roots = [('arg_0', 0x8057B444)]
    #func_ea = 0xC1049BC0
    #roots = [('large fs:124h', 4651009)]
    '''
    results = {}
    for func_name in func_pattern:
        func_ea = funcs[func_name]
        results[func_name] = {}
        for obj in func_pattern:
            results[func_name][obj] = {}
            for root in func_pattern[func_name][obj]:
                reg = root[0][0]
                dugs, root_addr = forward_tracing(func_ea, reg)
                results[func_name][obj] = (dugs, root_addr)
    '''
    dfgs = forward_tracing(0xC1076330, 'fs:current_task-3E671090h')
    extract_offsets(dfgs)
    #results[func_name][obj] = (dugs, root_addr)