from sngram import *
from Context import Context
from Config import Config
import cPickle as pickle
import distance
import numpy
import hungarian
import sys
import pdb
import copy
import math
import argparse
from evl import *
from graph_edit_distance import *
class Context_based_match:
	def __init__(self, config_path, output_path):
		self.callgraph = None
		self.feature_db = None
		self.funcontex = None
		self.contextls = {}
		self.matched = {}
		self.funclevels = {}
		self.contextlevels = {}
		self.scorelist_path = output_path
	
	def data_preparing(self, config_path, matchtype):
		config = Config(config_path, 'match', matchtype)
		self.src_db = config.src_db
		self.dst_db = config.dst_db


	def searchAll(self, start, lenth):
		scorelist = {}
		visited = {}
		src_name = self.src_db['name']
		dst_name = self.dst_db['name']
		self.src_llvm_to_strip = convert_llvmtostrip(src_name, self.src_db['dugs'])
		#pdb.set_trace()
		self.dst_llvm_to_strip = convert_llvmtostrip(dst_name, self.dst_db['dugs'])
		i = 0
		
		tomatches = self.src_db['seqs'].keys()
		pdb.set_trace()
		for i in xrange(len(tomatches)):
			i = i + start
			if i <100000:
				matched_name = tomatches[i]
				scorelist[matched_name] = {}
				i += 1
				j = 0
				for cname in self.dst_db['seqs'].keys():
					print j 
					j += 1
					if (cname, matched_name) not in visited:
						visited[(matched_name, cname)] = 1
						if matched_name == 'sub_8049700' and cname == 'sub_8049763':
							pdb.set_trace()
							print 's'
						#pdb.set_trace()
						c_score = self.match_score(matched_name, cname)
						if matched_name not in scorelist:
							scorelist[matched_name] = {}
						scorelist[matched_name][cname] = c_score
				#pdb.set_trace()
				print "Finish one function match " + str(i)
		pdb.set_trace()
		
		pickle.dump(scorelist, open(self.scorelist_path + "base641.scorelist", 'wb'))
		pdb.set_trace()
		
		scorelist = pickle.load(open(self.scorelist_path + "base641.scorelist", 'r'))
		src_indexes = self.src_db['seqs'].keys()
		dst_indexes = self.dst_db['seqs'].keys()
		accuracy(scorelist, src_name, dst_name, src_indexes, dst_indexes)
		print 'found'


	def match_score1(self, src_name, dst_name):
		matrix = {}
		src_dug = self.src_db['dugs'][src_name]
		dst_dug = self.dst_db['dugs'][dst_name]
		#pdb.set_trace()
		if src_dug == 0 or dst_dug ==0 or len(src_dug) == 0 or len(dst_dug) == 0:
			if src_name in self.src_llvm_to_strip:
				src_name = self.src_llvm_to_strip[src_name]
			else:
				return 1000
			if dst_name in self.dst_llvm_to_strip:
				dst_name = self.dst_llvm_to_strip[dst_name]
			else:
				return 1000
			src_seqs = self.src_db['seqs'][src_name]
			dst_seqs = self.dst_db['seqs'][dst_name]
			cost = ngramD(src_seqs, dst_seqs)
		else:
			#pdb.set_trace()
			cost = graph_edge_distance(src_dug, dst_dug)
		return cost
	def match_score(self, src_name, dst_name):
		src_seqs = self.src_db['seqs'][src_name]
		dst_seqs = self.dst_db['seqs'][dst_name]
		cost = ngramD(src_seqs, dst_seqs)
		return cost

	def xdot1(dug, path):
		#nx.write_gml(dug, path + "old_dug.gml")
		#nx.write_gml(refined_dug_dic["sub_8049699"], "/home/qian/svn/code_search/LLVM_feature/new_dug.gml")
		#os.system("gml2gv -o " + path  + "old_dug.dot " + path + "old_dug.gml")
		#os.system("xdot /home/qian/svn/code_search/LLVM_feature/new_dug.dot")
		#x=nx.read_gml(path + "old_dug.gml")
		nx.write_dot(dug, path + "old_dug.dot")
		#nx.write_gml(refined_dug_dic["sub_8049699"], "/home/qian/svn/code_search/LLVM_feature/new_dug.gml")
		#os.system("gml2gv -o " + path  + "old_dug.dot " + path + "old_dug.gml")
		#os.system("xdot /home/qian/svn/code_search/LLVM_feature/new_dug.dot")
		x=nx.read_dot(path + "old_dug.dot")
		return x


if __name__=="__main__":
	parser = argparse.ArgumentParser(description='Match codes!')
	# Add arguments
	parser.add_argument(
	'--configpath', type=str, help='Config path...', required=True)
	parser.add_argument(
	'--matchtype', type=str, help='Match Type', required=True)
	parser.add_argument(
	'--start', type=int, help='the process start length when paralleling', required=False)
	parser.add_argument(
	'--lenth', type=int, help='the process end length when paralleling', required=False)
	parser.add_argument(
	'--scorelist_path', type=str, help='the process end length when paralleling', required=False)
	args = parser.parse_args()
	config_path = args.configpath
	start = args.start
	lenth = args.lenth
	matchtype = args.matchtype
	scorelist_path = args.scorelist_path
	cmatch = Context_based_match(config_path, scorelist_path)
	cmatch.data_preparing(config_path, matchtype)
	#cmatch.context_preparing()
	#cmatch.levels_preparing()
	cmatch.searchAll(start, lenth)

