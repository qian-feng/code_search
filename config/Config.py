from Context import Context
import cPickle as pickle
import pdb
class Config:
	def __init__(self, config_path, config_type, matchtype):
		self.fp = open(config_path, 'r')
		self.callgraph = None
		self.feature_db = None
		self.funcontex = None
		self.Contextls = {}
		self.testset = {}
		self.testcontextls = {}
		self.src_db = {}
		self.dst_db = {}
		self.matchtype = matchtype
		self.obtainConfig(config_path)
		self.matchall_preparing()

	def obtainConfig(self, config_path):
		for entry in self.fp:
			if '**' in entry:
				break
			if 'src' in entry:
				if 'srcfunc' in entry:
					self.srcfunc = entry.split(":= ")[1].split("\n")[0]
				if 'srcname' in entry:
					self.srcname = entry.split(":= ")[1].split("\n")[0]
				if 'srcdir' in entry:
					self.srcdir = entry.split(":= ")[1].split("\n")[0]
				if 'srcbname' in entry:
					sbname = entry.split(':= ')[1].split("\n")[0]


			if "dst" in entry:
				if 'dstfunc' in entry:
					self.dstfunc = entry.split(":= ")[1].split("\n")[0]
				if 'dstname' in entry:
					self.dstname = entry.split(":= ")[1].split("\n")[0]
				if 'dstdir' in entry:
					self.dstdir = entry.split(":= ")[1].split("\n")[0]
				if 'dstbname' in entry:
					dbname = entry.split(':= ')[1].split("\n")[0]
			if 'depth' in entry:
				self.depth = int(entry.split(":= ")[1].split("\n")[0])
			if 'type' in entry:
				self.type = entry.split(":= ")[1].split("\n")[0]
		self.src_db['name'] = self.srcname
		self.dst_db['name'] = self.dstname
		self.src_db['bname'] = sbname
		self.dst_db['bname'] = dbname
			

	def matchall_preparing(self):
		#feature_db_path = self.srcdir + self.srcname + '.dugs'
		#func_dug_db = pickle.load(open(feature_db_path, 'r'))
		#self.src_db['dugs'] = func_dug_db

		feature_db_path = self.srcdir + self.srcname + '.func_seqs'
		func_dug_db = pickle.load(open(feature_db_path, 'r'))
		self.src_db['seqs'] = func_dug_db
		
		callgraph_path = self.srcdir + self.srcname + '.callgraph'
		callgraph = pickle.load(open(callgraph_path, 'r'))
		callgraph.remove_node('')
		self.src_db['callgraph'] = callgraph
		self.src_db['type'] = self.type
		self.src_db['depth'] = self.depth


		##  dst feature extractions
		#feature_db_path = self.dstdir + self.dstname + '.dugs'
		#func_dug_db = pickle.load(open(feature_db_path, 'r'))
		#self.dst_db['dugs'] = func_dug_db
		
		feature_db_path = self.dstdir + self.dstname + '.func_seqs'
		func_dug_db = pickle.load(open(feature_db_path, 'r'))
		self.dst_db['seqs'] = func_dug_db
		callgraph_path = self.dstdir + self.dstname + '.callgraph'
		callgraph = pickle.load(open(callgraph_path, 'r'))
		callgraph.remove_node('')
		self.dst_db['callgraph'] = callgraph
		print "finishing callgraph, seqs and other basic information collecting..."
		self.gen_callgraphlets()
		self.src_db['context'] = self.src_graphlets
		self.dst_db['context'] = self.dst_graphlets
		print "finishing the edgehood collecting..."
		'''
		if self.matchtype == 'start':
			self.gen_callgraphlets()
		testcontextls_path = self.srcdir + self.srcname + '.graphlets'
		self.testcontextls = pickle.load(open(testcontextls_path, 'r'))

		testcontextls_path = self.srcdir + self.srcname + '.graphlets'
		self.testcontextls = pickle.load(open(testcontextls_path, 'r'))
		self.dst_db['type'] = self.type
		self.dst_db['depth'] = self.depth
		'''



	def gen_callgraphlets(self):
		# for src callgraphlets
		self.src_graphlets = {}
		test_context_path = self.srcdir + self.srcname + '.graphlets'
		src_callgraph = self.src_db['callgraph']
		type_ = self.src_db['type']
		depth = self.src_db['depth']
		for node in src_callgraph:
			src_context = Context(node, src_callgraph, depth, type_)
			self.src_graphlets[node] = src_context

		pickle.dump(self.src_graphlets, open(test_context_path, 'wb'))

		self.dst_graphlets = {}
		test_context_path = self.dstdir + self.dstname + '.contextls'
		dst_callgraph = self.dst_db['callgraph']
		for node in dst_callgraph:
			dst_context = Context(node, dst_callgraph, depth, type_)
			self.dst_graphlets[node] = dst_context

		pickle.dump(self.dst_graphlets, open(test_context_path, 'wb'))

