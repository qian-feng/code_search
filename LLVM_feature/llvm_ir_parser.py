import cPickle as pickle
import networkx as nx
import os
import argparse
import pdb
import copy
from xdot import *
from feature_selection import *
#pdb /home/qian/svn/code_search/LLVM_feature/llvm_ir_parser.py --dug_path=/home/qian/data/mcsema/IR/dug0 
#--target_path=/home/qian/data/BGM/IR/db/ --dot_path=/home/qian/data/mcsema/basename_i386_o0_strip.idb.dot 
#--exename=basename
feature = ['ESP', 'EBP',  "EBX", 'call']
debug = True
def opseq_parser(path):
	funcbody = {}
	for filename in os.listdir(path):
		funcbody[filename] = []
		fullpath = os.path.join(path, filename)
		fp = open(fullpath, 'r')
		for x in fp:
			item = x.split("\n")
			opcode = item[0]
			funcbody[filename].append(opcode)
	return funcbody


def dug_parser(path, target_path):
	dug_dic = {}
	if not debug:
		for filename in os.listdir(path):
			if 'driver_' in filename:
				continue
			if '.gml' in filename:
				name = filename.split(".gml")[0]
			else:
				name = filename.split(".index")[0]
			if name not in dug_dic:
				dug_dic[name] = {}
			fullpath = os.path.join(path, filename)
			if '.gml' in filename:
				try:
					print filename
					dug = nx.read_gml(fullpath)
					dug_dic[name]['gml'] = dug 
				except:
					continue
			else:
				label_list = {}
				fp = open(fullpath, 'r')
				for x in fp:
					if ':' in x:
						try:
							item = x.split(":")
							id_ = int(item[0])
							label = item[1].split('\n')[0]
							label_list[id_] = label
						except:
							continue
				dug_dic[name]['label'] = label_list
	
	#dug_dic = pickle.load(open("/home/qian/data/BGM/IR/db/chown.dugs",'r'))
	refined_dug_dic = refine(dug_dic)
	#nx.write_gml(dug_dic["sub_8049699"]['gml'], "/home/qian/svn/code_search/LLVM_feature/old_dug.gml")
	#nx.write_gml(refined_dug_dic["sub_8049699"], "/home/qian/svn/code_search/LLVM_feature/new_dug.gml")
	#os.system("gml2gv -o new_dug.dot new_dug.gml")
	#os.system("xdot /home/qian/svn/code_search/LLVM_feature/new_dug.dot")
	#x=nx.read_gml("new_dug.gml")
	#pdb.set_trace()
	pickle.dump(refined_dug_dic, open(target_path,'w'))
	return refined_dug_dic

def callgraph_parser(dotpath, target_path):
	callgraph = nx.read_dot(dotpath)
	graph = nx.DiGraph()
	for src, dst in callgraph.edges():
		try:
			src_name = str(callgraph.node[src]['label'].split('{')[1].split('}')[0])
			dst_name = str(callgraph.node[dst]['label'].split('{')[1].split('}')[0])
			graph.add_edge(src_name, dst_name)
		except:
			continue
	#pdb.set_trace()
	pickle.dump(graph, open(target_path,"w"))
	return graph

def obtain_node(dug, node, label_list):
	if node in label_list:
		name = label_list[node]
	else:
		print "out of label_list"
		return node
	return name


def refine(dug_dic):
	refined_dug_dic = {}
	if not debug:
		pickle.dump(dug_dic, open('mytest','w'))
	dug_dic = pickle.load(open('mytest', 'r'))
	for name in dug_dic:
		dug = dug_dic[name]['gml']
		label_list = dug_dic[name]['label']
		re = [v for v in label_list if 'unreachable' in label_list[v]]
		if len(re) != 0:
			refined_dug_dic[name] = 0
			print 'unreachable'
			continue
		print name, str(len(dug))
		
		if False:
			if name == 'sub_8049763':
				#pdb.set_trace()
				nx.write_gml(dug, "/home/qian/svn/code_search/LLVM_feature/old_dug.gml")
				#nx.write_gml(refined_dug_dic["sub_8049699"], "/home/qian/svn/code_search/LLVM_feature/new_dug.gml")
				os.system("gml2gv -o /home/qian/svn/code_search/LLVM_feature/old_dug.dot /home/qian/svn/code_search/LLVM_feature/old_dug.gml")
				#os.system("xdot /home/qian/svn/code_search/LLVM_feature/new_dug.dot")
				#x=nx.read_gml("/home/qian/svn/code_search/LLVM_feature/old_dug.gml")
				#pdb.set_trace()
				print 's'
			else:
				continue

		#pdb.set_trace()
		simple_dug = simplification(dug, label_list)
		print "after", str(len(simple_dug))
		graph = nx.DiGraph()
		#pdb.set_trace()
		'''
		for src, dst in simple_dug.edges():
			src_name = obtain_node(dug, src, label_list)
			dst_name = obtain_node(dug, dst, label_list)
			graph.add_edge(src, dst)
			graph.node[src]['label'] = src_name
			graph.node[dst]['label'] = dst_name
		'''
		refined_dug_dic[name] = simple_dug
		#x = xdot(simple_dug, "/home/qian/svn/code_search/LLVM_feature/")
		#pdb.set_trace()
		print 's'
		
	return refined_dug_dic

def simplification(dug, label_list):
	roots = obtain_argmentInput(dug, label_list, feature)
	simple_dug = nx.DiGraph()
	visited = {}
	for rt in roots:
		path = []
		visited[rt] = 1
		add_node(rt, dug, simple_dug, path, label_list, visited)
	#pdb.set_trace()
	extendDUG(dug, simple_dug, label_list)
	lifting(simple_dug, label_list)
	#pdb.set_trace()
	simplify(simple_dug, label_list)
	#pdb.set_trace()
	return simple_dug




if __name__=="__main__":
	parser = argparse.ArgumentParser(description='Match codes!')
	# Add arguments
	parser.add_argument(
	'--opseq_path', type=str, help='the directory storing opcode sequences for each function', required=False)
	parser.add_argument(
	'--dug_path', type=str, help='the directory storing dug for each function', required=True)
	parser.add_argument(
	'--target_path', type=str, help='the target path for parsed data including callgraph, func sequences, as well as dugs', required=True)
	#parser.add_argument(
	#'--dot_path', type=str, help='the directory storing dug for each function', required=True)
	parser.add_argument(
	'--exename', type=str, help='the directory storing dug for each function', required=True)
	args = parser.parse_args()
	opseq_path = args.opseq_path
	dug_path = args.dug_path
	target_path = args.target_path
	#dotpath = args.dot_path
	exename = args.exename
	#seqpath = os.path.join(target_path, exename, '.funcbody')
	#opseq = opseq_parser(opseq_path, seqpath)
	#pdb.set_trace()
	dug_tar = os.path.join(target_path, exename + '.dugs')
	dugs = dug_parser(dug_path, dug_tar)
	#callpath = os.path.join(target_path, exename +'.callgraph')
	#callgraph = callgraph_parser(dotpath, callpath)
	#pdb.set_trace()
	print "s"
