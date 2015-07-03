#import DFG_generator as dfg
import cfg_constructor as cfg
import networkx as nx
from idautils import *
from idaapi import *
from idc import *
import cPickle as pickle
import func as f

def callgraph_constructor(start_ea):
	callgraph = nx.DiGraph()
	funcs = f.get_func_names(start_ea)
	for func_name in funcs:
		funcea = funcs[func_name]
		ff = get_func(funcea)
		start = ff.startEA
		end = ff.endEA
		callers = CodeRefsTo(funcea, 1)
		inline_refs = CodeRefsFromInline(start, end)
		for cller in callers:
			cller_name = GetFunctionName(cller)
			callgraph.add_edge(cller_name, func_name)
		for cller in inline_refs:
			if cller in funcs:
				callgraph.add_edge(func_name, cller)
                        '''
			else:
				try:
					x=int(cller,16)
                                        if x > start_ea:
                                                callgraph.add_edge(x, func_name)
				except:
					pass
                        '''

	return callgraph


def CodeRefsFromInline(start, end):
	cur = start
	refs = []
	while cur <= end:
		opand2 = GetOpnd(cur, 1)
		if 'offset' in opand2:
			target = opand2.split(" ")[1]
			refs.append(target)
		cur = NextHead(cur)
	return refs


def callgraph_featuring(funcea, callgraph):
	feature_dic = {}
	for func_name in callgraph:
		pres = callgraph.predecessors(func_name)
		sucs = callgraph.successors(func_name)
		pre_f = filter(lambda x: 'sub' not in x, pres)
		suc_f = filter(lambda x: 'sub' not in x, sucs)
		if 'pre' not in feature_dic[func_name]:
			feature_dic[func_name]['pre'] = pre_f
		if 'suc' not in feature_dic[func_name]:
			feature_dic[func_name]['suc'] = suc_f

	return feature_dic

def similarity_comparision(callgraph, feature_dic):
	sim_dic = {}
	for node in callgraph:
		sim_dic[node] = {}
		for dnode in callgraph:
			score = compute_score(node, dnode, feature_dic)
			sim_dic[node][dnode] =  score

	return sim_dic

def compute_score(node, dnode, feature_dic):
	f1 = feature_dic[node]
	f2 = feature_dic[dnode]
	if len(f1) > len(f2):
		diff = set(f1).difference(f2)
	else:
		diff = set(f2).difference(f1)

	return len(diff)



#def feature_assessing(feature):
#	similarity_score = {}
if __name__=="__main__":
	s = callgraph_constructor()
