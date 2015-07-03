import copy
import networkx as nx
from idautils import *
from idaapi import *
from idc import *

import copy
import networkx as nx
from idautils import *
from idaapi import *
from idc import *


def cfg_construct(func):
	func_start = func.startEA
	func_end = func.endEA
	cfg = nx.DiGraph()
	seq_blocks, main_blocks = obtain_block_sequence(func)
	i = 0
	visited = {}
	for bl in seq_blocks:
		start = seq_blocks[bl][0]
		end = seq_blocks[bl][1]
		src_node = (start, end)
		if end in seq_blocks and GetMnem(PrevHead(end)) != 'jmp':
                        next_start = seq_blocks[end][0]
                        next_end = seq_blocks[end][1]
                        next_node = (next_start, next_end)
                        cfg.add_edge(src_node, next_node)
		if start == func_start:
			cfg.add_node(src_node, c='start')
			start_node = src_node
		if end == func_end:
			cfg.add_node(src_node, c='end')
		refs = CodeRefsFrom(PrevHead(end), 0)
		
		for ref in refs:
                        #print ref
                        if ref in seq_blocks:
                                dst_node = (seq_blocks[ref][0], seq_blocks[ref][1])
                                cfg.add_edge(src_node, dst_node)
	return cfg, start_node


def obtain_allpaths( cfg, node, path, allpaths):
	path.append(node)
	if 'c' in cfg.node[node] and cfg.node[node]['c'] == 'end':
		allpaths.append(path)
		return
	else:
		for suc in cfg.successors(node):
                        if suc not in path:
                                path_copy = copy.copy(path)
                                obtain_allpaths(cfg, suc, path_copy, allpaths)


def obtain_block_sequence(func):
	seq_blocks = {}
	main_blocks = {}
	blocks = [(v.startEA, v.endEA) for v in FlowChart(func)]
	for bl in blocks:
		base = bl[0]
		seq_blocks[base] = bl
		if func.startEA <=base <= func.endEA:
                        main_blocks[base] = bl
        x=sorted(main_blocks)
	return seq_blocks, x
