import os
import cPickle as pickle
import networkx as nx
import random
import copy
import argparse
import sys
sys.path.append("/home/qian/code_search/ida-6.6/python");
sys.path.append("/home/qian/code_search/ida-6.6/loaders");
sys.path.append('/home/qian/code_search')
try:
	import func
	from idautils import *
	from idaapi import *
	from idc import *
	import callgraph
except ImportError:
	pass

try:
	import distance
	import hungarian
	import pdb
except ImportError:
	pass

# Experiment II Design
#/home/qian/workspace/code_retriever/code_based/vmi/
class callgraph_based_matching:

	def __init__(self, exename, mode, dir_path):
		self.indexes = {}
		self.mode = mode
		self.funcbodylist = {}
		self.funccfglist = {}
		self.funccfgseqlist = {}
		self.funcs = {}
		self.home_dir = dir_path
		self.callgraphs = {}
		self.callgraph = nx.DiGraph()
		self.callgraph_dirpath =self.home_dir
		#self.funcbody_path = "E:/vmi/data/output/funcbody.list"
		#self.index_path = "E:/vmi/data/output/index.list"
		self.funcbody_dirpath = self.home_dir
		self.index_dirpath = self.home_dir
		self.funccfglist_dirpath = self.home_dir
		self.funcdatarefs_dirpath = self.home_dir
		self.func_dirpath = self.home_dir

	def feature_generating(self, ea, version):
			if self.mode != 'cache':

				self.funcbodylist = func.get_func_sequences(ea)
				self.funcs = func.get_func_bases(ea)
				self.index = self.funcbodylist.keys()
				self.callgraph = callgraph.callgraph_constructor(ea)
				self.funccfglist = func.get_func_cfgs(ea)
				self.funccfgseqlist = func.get_func_cfg_sequences(self.funccfglist)
				self.funcdatarefs = func.obtainDataRefs(self.callgraph)
				self.dumpObj(self.funcbodylist, self.funcbody_dirpath, version, 'funcbody')
				self.dumpObj(self.index, self.index_dirpath, version, 'index')
				#self.constraint_generation(callgraph)
				self.dumpObj(self.funcs, self.func_dirpath, version, 'func')
				self.dumpObj(self.callgraph, self.callgraph_dirpath, version, 'callgraph')
				self.dumpObj(self.funccfglist, self.funccfglist_dirpath, version, 'cfg')
				self.dumpObj(self.funccfgseqlist, self.funccfglist_dirpath, version, 'cfgsq')
				self.dumpObj(self.funcdatarefs, self.funcdatarefs_dirpath, version, 'dataref')

			else:

				self.loadObj(self.funcbody_dirpath, self.funcbodylist, 'funcbody')
				self.loadObj(self.index_dirpath, self.indexes, 'index')
				self.loadObj(self.callgraph_dirpath, self.callgraphs, 'callgraph')
				self.loadObj(self.funccfglist_dirpath, self.funccfglist, 'cfg')
				self.loadObj(self.funccfglist_dirpath, self.funccfgseqlist, 'cfgsq')
				self.loadObj(self.funcdatarefs_dirpath, self.funcdatarefs, 'dataref')
				self.collecting_groundTruth()

				#matrix = self.matrix_generating()
				#self.dump(matrix, version_src, version_dst)
				#print version + '\'s data is prepared!'
				#self.dump(matrix, version_src, version_dst)

	def collecting_groundTruth(self):
		for type_ in self.version:
			version = self.version[type_]
			self.indexes[version]=self.funcbodylist[version]
		x = [v for v in self.indexes[self.version['src']] if v in self.indexes[self.version['dst']]]
		self.indexes[self.version['src']] = x
		self.indexes[self.version['dst']] = x



	def dumpObj(self, obj, dirpath, version, type_):
		print dirpath
		print version
		print type_
		path = dirpath + '/' + version + '.' + type_
		if type_ == 'index' or type_ == 'funcbody' or type_ == 'dataref':
			pickle.dump(obj, open(path,'w'))
		else:
			nx.write_gpickle(obj,path)

	def dumpMatrix(self, obj, path):
		pickle.dump(obj, open(path,'w'))

	def loadObj(self, path, obj, surfix):
		filelist = [filename for filename in os.listdir(path) if filename.endswith(surfix)]
		print filelist
		for f in filelist:
			filep = path + '/' + f
			version = f.split(surfix)[0]
			if version == self.version['src'] or version == self.version['dst']:
				obj[version] = {}
				if surfix == 'index' or surfix == 'funcbody':
					obj[version] = pickle.load(open(filep,'r'))
				else:
					obj[version] = nx.read_gpickle(filep)
		#print obj

	#[0, 2, 3, 4, 5]
	#[0, 4, 5, 6, 7]
	#[0, 7, 9, 5, 6, 3, 8, 2, 4, 1]
	def matrix_generating(self, version_src, version_dst):
			matrix = []
			index_row = self.indexes[version_src]
			index_column = self.indexes[version_dst]
			print "src # of nodes = " + str(len(self.indexes[version_src]))
			print "dst # of nodes = " + str(len(self.indexes[version_dst]))

			if len(index_row) <= len(index_column):
				matrix_len = len(index_column)
			else:
				matrix_len = len(index_row)

			#matrix_len = 1000
			self.cfg_seqdb_row =  {}
			self.cfg_seqdb_column =  {}
			#pdb.set_trace()
			for row_name in range(matrix_len):
				matrix_row = []
				#print row_name*1.0/matrix_row_len
				for colum_name in range(matrix_len):
					#try:
					#pdb.set_trace()race()
					
					#if colum_name != 10:
					#	continue
					
					#pdb.set_trace()
					cost = self.obtain_cost(row_name, colum_name, version_src, version_dst, 3, 'ngram')
					print colum_name, row_name
					matrix_row.append(cost)
					#except:
					#	matrix_row.append(1)
				#pdb.set_trace()
				matrix.append(matrix_row)
			#pdb.set_trace()
			return matrix

	def obtain_cost(self, row_id, colum_id, version_src, version_dst, c_depth, costtype):
		if costtype == 'ngram':
			cost = self.ngram(row_id, colum_id, version_src, version_dst, c_depth)
		if costtype == 'graphlet':
			cost = self.graphlet(row_id, colum_id, version_src, version_dst, c_depth)
		if costtype == 'tracelet':
			cost = self.tracelet(row_id, colum_id, version_src, version_dst, c_depth)
		if costtype == 'callgraphlet':
			cost = self.callgraphlet(row_id, colum_id, version_src, version_dst, c_depth)

		return cost

	# ###################
	# ###################
	#************************* ngram ******************************************************
	def ngram(self, row_id, colum_id, version_src, version_dst, c_n):
		index_row = self.indexes[version_src]
		index_column = self.indexes[version_dst]
		src_seq = self.funcbodylist[version_src]
		dst_seq = self.funcbodylist[version_dst]
		row_name = index_row[row_id]
		colum_name = index_column[colum_id]
		src_seqlist = src_seq[row_name]
		dst_seqlist = dst_seq[colum_name]
		#pdb.set_trace()
		cost = self.cal_ngram_cost(src_seqlist, dst_seqlist, c_n)
		#cost = self.cal_nperm_cost(src_seqlist, dst_seqlist, c_n)
		return cost

	def cal_ngram_cost(self, src_seqlist, dst_seqlist, c_n):
		src_ngrams = self.obtain_allgrams(src_seqlist, c_n)
		dst_ngrams = self.obtain_allgrams(dst_seqlist, c_n)
		common_grams = [v for v in src_ngrams if v in dst_ngrams]
		cost = 1 - ((2*len(common_grams)) * 1.0 / (len(src_ngrams) + len(dst_ngrams)))
		return cost

	def obtain_allgrams(self, seqlist, c_n):
		ngrams = []
		for i in range(len(seqlist)):
			if (i+c_n - 1) < len(seqlist):
				gram = [seqlist[i + j] for j in range(c_n)]
				ngrams.append(gram)

		return ngrams
	#*************************END ngram******************************************************
	# ###################
	# ###################
	#************************* graphlet ******************************************************
	def graphlet(self, row_id, colum_id, version_src, version_dst, c_k):
		index_row = self.indexes[version_src]
		index_column = self.indexes[version_dst]
		try:
			row_name = index_row[row_id]
			colum_name = index_column[colum_id]
			cfg_row, row_start = self.funccfglist[version_src][row_name]
			cfg_column, column_start = self.funccfglist[version_dst][colum_name]
		except:
			return 1

		cost = self.cal_graphlet_cost(cfg_row, cfg_column, row_start, column_start, row_name, colum_name, c_k)
		return cost
		

	def cal_graphlet_cost(self, cfg_row, cfg_column, row_start, column_start, c_k):
		src_graphlet = nx.DiGraph()
		dst_graphlet = nx.DiGraph()
		src_graphlets = []
		dst_graphlets = []
		src_graphlet.add_node(row_start)
		dst_graphlet.add_node(column_start)
		src_graphlets = self.obtain_allgraphlets(cfg_row, row_start, c_k, src_graphlet, src_graphlets)
		dst_graphlets = self.obtain_allgraphlets(cfg_column, column_start, c_k, dst_graphlet, dst_graphlets)
		return 0

	def obtain_allgraphlets(self, cfg, start, c_k, graphlet, graphlets):
		if  len(graphlet) == c_k:
			graphlets.append(graphlet)
			return 
		else:
			successors = cfg.successors(start)
			for suc in successors:
				update_graphlet = copy.copy(graphlet)
				update_graphlet.add_edge(start, suc)
				self.obtain_allgraphlets(cfg, suc, c_k, update_graphlet, graphlets)



	#*************************END graphlet ******************************************************
	# ###################
	# ###################
	#************************* tracelet ******************************************************
	def tracelet(self, row_id, colum_id, version_src, version_dst, c_depth):
		return 0

	def cal_tracelet_cost(self, row_id, colum_id, version_src, version_dst, c_depth):
		return 0

	#*************************END tracelet ******************************************************
	# ###################
	# ###################
	#************************* callgraphlet ******************************************************
	def callgraphlet(self, row_id, colum_id, version_src, version_dst, c_depth):
		return 0

	def cal_callgraphlet_cost(self, row_id, colum_id, version_src, version_dst, c_depth):
		return 0

	#*************************END callgraphlet ******************************************************


	def obtain_cost1(self, row_id, colum_id, version_src, version_dst, c_depth):
			index_row = self.indexes[version_src]
			index_column = self.indexes[version_dst]
			callgraph_src = self.callgraphs[version_src]
			callgraph_dst = self.callgraphs[version_dst]
			try:
				row_name = index_row[row_id]
				colum_name = index_column[colum_id]
				cfg_row, row_start = self.funccfglist[version_src][row_name]
				cfg_column, column_start = self.funccfglist[version_dst][colum_name]
			except:
				return 1
			cost = self.ngram()
			cost = self.graphlet()
			cost = self.tracelet()
			cost = self.callgraphlet()
			# callgraph based
			#cost = self.cal_cgcost(callgraph_src, callgraph_dst, row_name, colum_name, c_depth)
			# cfg base
			#cost = self.cal_cfgcost(cfg_row, cfg_column, row_start, column_start, row_name, colum_name, c_depth)
			#pdb.set_trace()
			#cost = self.cal_seqcost(cfg_row, cfg_column, row_start, column_start, row_name, colum_name)
			return cost

	def cal_cfgcost(self, cfg_row, cfg_column, row_start, column_start, row_name, colum_name, c_depth):
		src_constraint_set = self.obtain_successors(cfg_row, row_start, c_depth, {c_depth:[row_start]})
		dst_constraint_set = self.obtain_successors(cfg_column, column_start, c_depth, {c_depth:[column_start]})
		cost = self.cal_diff(src_constraint_set, dst_constraint_set, self.funccfgseqlist, row_name, colum_name, c_depth)
		ncost = self.normalizing(src_constraint_set, dst_constraint_set, cost)
		return ncost


	def cal_cgcost(self, callgraph_src, callgraph_dst, row_name, column_name, c_depth):
		difflist = {}

		if row_name in self.cfg_seqdb_row:
			src_constraint_set = self.cfg_seqdb_row[row_name]
		else:
			src_constraint_set = self.obtain_successors(callgraph_src, row_name, c_depth, {c_depth:[row_name]})
			self.cfg_seqdb_row[row_name] = src_constraint_set

		if column_name in self.cfg_seqdb_column:
			dst_constraint_set = self.cfg_seqdb_column[column_name]
		else:
			pdb.set_trace()
			dst_constraint_set = self.obtain_successors(callgraph_dst, column_name, c_depth, {c_depth:[column_name]})
			self.cfg_seqdb_column[column_name] = dst_constraint_set

		cost = self.cal_diff(src_constraint_set, dst_constraint_set, self.funcbodylist,row_name, column_name, c_depth)
		ncost = self.normalizing(src_constraint_set, dst_constraint_set, cost)
		return ncost

	def cal_seqcost(self, cfg_row, cfg_column, row_start, column_start, row_name, colum_name):
		if len(cfg_row)*1.0/len(cfg_column) > 2 or len(cfg_row)*1.0/len(cfg_column) < 0.5:
			return 100
		src_seqlist = self.obtain_sequences(cfg_row, row_start, row_name, 'src')
		dst_seqlist = self.obtain_sequences(cfg_column, column_start, colum_name, 'dst')
		cost = self.cal_diff_seq(src_seqlist, dst_seqlist)
		return cost

	def obtain_sequences(self, cfg, start, name, type_):
		if len(cfg) == 1:
			return  self.funccfgseqlist[self.version[type_]][name][start]
		'''
		try:
			end = [v for v in cfg if len(cfg.successors(v)) == 0][0]
		except:
			x = sorted(cfg.nodes(), reverse = True)
			end = x[0]
		'''
		paths = []
		self.obtain_pathsWithin(3, cfg, start, {start:1}, paths)
		#pdb.set_trace()
		seqlist = []
		i = 0
		for path in paths:
			#pdb.set_trace()
			seq = self.seqences(path, name, type_)
			seqlist.append(seq)

		return seqlist

	def obtain_pathsWithin(self, depth_old, cfg, start, path, paths):
		if depth_old == 0:
			paths.append(path)
			return

		successors = cfg.successors(start)
		if len(successors) == 0:
			paths.append(path)
			return
		for suc in successors:
			if suc not in path:
				path1 = copy.copy(path)
				path1[suc] = 1
				depth = depth_old - 1
				self.obtain_pathsWithin(depth, cfg, suc, path1, paths)
			else:
				paths.append(path)

				

	def seqences(self, path, name, type_):
		seq = []
		for node in path:
			try:
				seq_node = self.funccfgseqlist[self.version[type_]][name][node]
				seq = seq + seq_node
			except:
				pass

		return seq

	def cal_diff_seq(self, src_seqlist, dst_seqlist):
		if len(src_seqlist) > len(dst_seqlist):
			matrix_len = len(dst_seqlist)
		else:
			matrix_len = len(src_seqlist)
		matrix = []
		for src_id in range(matrix_len):
			row = []
			src_node = src_seqlist[src_id]
			for dst_id in range(matrix_len):
				dst_node = dst_seqlist[dst_id]
				#pdb.set_trace()
				cost = distance.nlevenshtein(src_node, dst_node)
				row.append(cost)
			matrix.append(row)
		mapping = hungarian.lap(matrix)
		cost = self.cal_mapping_cost(mapping[0], matrix, src_seqlist, dst_seqlist)
		return cost




	def normalizing(self, src_constraint_set, dst_constraint_set, cost):
		total_cost = sum(cost.values())
		src_total_num = sum([len(v) for v in src_constraint_set.values()])
		dst_total_num = sum([len(v) for v in dst_constraint_set.values()])
		total = src_total_num + dst_total_num
		#pdb.set_trace()
		return total_cost*1.0/total

		

	def obtain_successors(self, callgraph, name, depth, successors):
		if depth == 0:
			return successors
		else:
			depth = depth -1
			try:
				sucs = callgraph.successors(name)
			except:
				return successors
			if depth not in successors:
				successors[depth] = sucs
			else:
				successors[depth] = successors[depth] + sucs
			for suc in sucs:
				self.obtain_successors(callgraph, suc, depth, successors)
		return successors



	def cal_diff(self, src_constraint_set, dst_constraint_set, bodylist, row_name, colum_name, c_depth):
		difflist = {}
		for i in range(c_depth+1):
			matrix = []
			if i in src_constraint_set:
				src_set = src_constraint_set[i]
			else:
				src_set = []
			if i in dst_constraint_set:
				dst_set = dst_constraint_set[i]
			else:
				dst_set = []

			if len(src_set) > len(dst_set):
				matrix_len = len(src_set)
			else:
				matrix_len = len(dst_set)

			for src_id in range(matrix_len):
				row = []
				for dst_id in range(matrix_len):
					try:
						dst_name = dst_set[dst_id]
						src_name = src_set[src_id]
						src_body = bodylist[self.version['src']][row_name][src_name]
						dst_body = bodylist[self.version['dst']][colum_name][dst_name]
						cost = distance.jaccard(src_body, dst_body)
						row.append(cost)
					except:
						row.append(1)
				matrix.append(row)
			#pdb.set_trace()
			if len(matrix) != 0:
				mapping = hungarian.lap(matrix)
				cost = self.cal_mapping_cost(mapping[0], matrix, src_set, dst_set)
			else:
				cost = 0
			difflist[i] = cost

		return difflist



	def cal_mapping_cost(self, mapping, matrix, src_set, dst_set):
		cost = 0
		for i in range(len(mapping)):
			j = mapping[i]
			if i < len(src_set) and j < len(dst_set):
				c = matrix[i][j]
				cost += c

		return cost



	def dump(self, kernel_matrix, version_src, version_dst):
		fp = open(self.home_dir + '/data/output/' + version + '.cost_matrix', 'w')
		index_row = self.indexes[version_src]
		index_column = self.indexes[version_dst]
		for row_name in range(len(index_row)):
			for colum_name in range(len(index_column)):
				value = kernel_matrix[row_name][colum_name]
				fp.write(str(value) + '\t')
			fp.write('\n')

		fp.close()

	'''
	def matching_evluation(self, mapping, version_src, version_dst, cost_matrix):
		hit = []
		miss = []
		TN = []
		errlist = []
		matched = []
		row_mapping = mapping[0]
		index_row = self.indexes[version_src]
		index_column = self.indexes[version_dst]
		costlist = []
		for i in range(len(row_mapping)):
			if i >= len(index_row):
				src_name = 'fake'
			else:
				src_name = index_row[i]
			dst_index = row_mapping[i]
			costlist.append(cost_matrix[i][dst_index])
			if dst_index >= len(index_column):
				dst_name = 'fake'
			else:
				dst_name = index_column[dst_index]
			if src_name == dst_name:
				hit.append(i)
				matched.append((src_name, dst_name))
			else:
				miss.append(i)
				try:
					id_ = index_column.index(src_name)
					errlist.append((src_name, dst_name, i, id_))
				except:
					TN.append(i)
				
		pdb.set_trace()
		print "Total # = " + str(len(row_mapping))
		print "Total hit # = " + str(len(hit))
		print "Total miss # = " + str(len(miss))
		print "Total true negatives # = " + str(len(TN))
		TP = len(hit)
		FP = len(miss) - len(TN)
		TN = len(TN)
		print "Recall #= " + str(len(hit)*1.0 / (len(hit) + len(FP)))
		print "Accuracy #= " + str(len(hit)*1.0 / len(row_mapping))
		pdb.set_trace()
		return matched
	'''

	def random_evaluation(self, seed, mapping, cost_matrix):
		index_row = self.indexes[self.version['src']]
		index_column = self.indexes[self.version['dst']]
		accracy_table = {}
		for i in range(seed):
			num = random.randint(0, len(mapping))
			cost = cost_matrix[num]
			min_cost = min(cost)
			indexes = [v for v in range(len(cost)) if cost[v] == min_cost]
			src_name = index_row[i]
			hit  = 0
			miss = 0
			for index in indexes:
				dst_name = index_column[index]
				if src_name == dst_name:
					hit += 1
				else:
					miss += 1
			accracy_table[src_name] = hit * 1.0 / len(indexes)
		total = sum(accracy_table.values())
		avg = total * 1.0 / len(accracy_table)
		print '(Type I random similarity) --- average accracy is = ' + str(avg)



	def individual_evaluation(self, mapping, cost_matrix):
		index_row = self.indexes[self.version['src']]
		index_column = self.indexes[self.version['dst']]
		accracy_table = {}
		for i in range(len(mapping)):
			cost = cost_matrix[i]
			min_cost = min(cost)
			indexes = [v for v in range(len(cost)) if cost[v] == min_cost]
			try:
				src_name = index_row[i]
			except:
				src_name = 'fake'
			hit = 0
			miss = 0
			for index in indexes:
				try:
					dst_name = index_column[index]
				except:
					dst_name = 'fake'
				if src_name == dst_name:
					hit += 1
				else:
					miss += 1
			accracy_table[src_name] = hit * 1.0 / len(indexes)
		total = sum(accracy_table.values())
		avg = total * 1.0 / len(accracy_table)
		print '(Type II individual similarity) --- average accracy is = ' + str(avg)


	def PGM_evaluation(self, mapping, cost_matrix):
		index_row = self.indexes[self.version['src']]
		index_column = self.indexes[self.version['dst']]
		accracy_table = {}
		hit = []
		miss = []
		for i in range(len(mapping)):
			j = mapping[i]
			try:
				src_name = index_row[i]
			except:
				src_name = 'fake'
			try:
				dst_name = index_column[j]
			except:
				dst_name = 'fake'
			if src_name == dst_name:
				hit.append(i)
			else:
				cost = cost_matrix[i][j]
				#if cost < 0.5:
				miss.append((i,j))
		#pdb.set_trace()
		pickle.dump(hit, open("/media/sf_qian/vmi/data/evaluation/winxp3/BGM.hit",'w'))
		pickle.dump(self.indexes['xp3.'], open("/media/sf_qian/vmi/data/evaluation/winxp3/BGM.index",'w'))
		hit_num = len(hit)
		miss_num = len(miss)
		avg = hit_num * 1.0 / (hit_num + miss_num)
		pdb.set_trace()
		print '(Type III PGM matching_evluation) --- average accracy is = ' + str(avg)



if __name__=="__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--exename", help="matched program name")
	parser.add_argument("--mod", help="matched program name")
	parser.add_argument("--home-dir", help="matched program name")
	# ***************Experiment II: Bipartite Graph Matching ***************************
	args = parser.parse_args(args=idc.ARGV[1:])
	analysis_flags = idc.GetShortPrm(idc.INF_START_AF)
	analysis_flags &= ~idc.AF_IMMOFF
	# turn off "automatically make offset" heuristic
	idc.SetShortPrm(idc.INF_START_AF, analysis_flags)
	idaapi.autoWait()
	ea = FirstSeg()
	exename = args.exename
	mod = args.mod
	home_dir = args.home_dir
	fg = callgraph_based_matching(exename, mod, home_dir)
	
	# 1. matrix generation
	if mod == 'start':
		fg.feature_generating(ea, exename)
		idc.Exit(0)
	else:
		fg.feature_generating(ea, exename)