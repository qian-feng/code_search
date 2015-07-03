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
		self.obtainConfig(config_path)
		if config_type == 'sig':
			if matchtype == 'matchone':
				self.testConfig()
			if matchtype == 'matchall':
				self.testsetConfig()
		if config_type == 'match':
			if matchtype == 'matchdug':
				self.matchall_preparing()
			if matchtype == 'matchseq':
				self.matchall_preparing()

	def obtainConfig(self, config_path):
		for entry in self.fp:
			if 'testfunc' in entry:
				self.testfunc = entry.split(":= ")[1].split("\n")[0]
			if 'testpogram' in entry:
				self.testpogram = entry.split(":= ")[1].split("\n")[0]
			if 'testdir' in entry:
				self.testdir = entry.split(":= ")[1].split("\n")[0]
			if 'dbprogram' in entry:
				self.dbprogram = entry.split(":= ")[1].split("\n")[0]
			if 'dbdir' in entry:
				self.dbdir = entry.split(":= ")[1].split("\n")[0]
			if 'depth' in entry:
				self.depth = int(entry.split(":= ")[1].split("\n")[0])
			if 'type' in entry:
				self.type = entry.split(":= ")[1].split("\n")[0]
			if 'testpogram' in entry:
				self.sharename = entry.split(":= ")[1].split("\n")[0]
			


	def testsetConfig(self):

		testset_path = self.testdir + self.sharename + '.share'
		pdb.set_trace()
		self.testset = pickle.load(open(testset_path, 'r'))

		testcallgraph_path = self.testdir + self.testpogram + '.callgraph'
		self.testcallgraph = pickle.load(open(testcallgraph_path, 'r'))

		feature_db_path = self.testdir + self.testpogram + '.funcbody'
		self.func_feature_db = pickle.load(open(feature_db_path, 'r'))

		feature_db_path = self.testdir + self.testpogram + '.dugs'
		self.func_dug_db = pickle.load(open(feature_db_path, 'r'))

		self.func_datarefs = {}
		self.datarefs = {}

		'''
		feature_datarefs_path = self.testdir + self.testpogram + '.dataref'
		self.func_datarefs = pickle.load(open(feature_datarefs_path, 'r'))

		feature_db_path = self.dbdir + self.dbprogram + '.dataref'
		self.datarefs = pickle.load(open(feature_db_path, 'r'))
		'''


	def testConfig(self):
		try:
			funcontex_path = self.testdir + self.testfunc + '.context'
			if len(funcontex_path) != 0:
				self.funcontex = pickle.load(open(funcontex_path, 'r'))
		except:
			self.funcontex = {}

		feature_db_path = self.testdir + self.testpogram + '.funcbody'
		self.func_feature_db = pickle.load(open(feature_db_path, 'r'))

		self.testname = self.testfunc
		
		testcallgraph_path = self.testdir + self.testpogram + '.callgraph'
		self.testcallgraph = pickle.load(open(testcallgraph_path, 'r'))
		'''
		feature_datarefs_path = self.testdir + self.testpogram + '.dataref'
		self.func_datarefs = pickle.load(open(feature_datarefs_path, 'r'))
		'''

	def matchone_preparing(self):

		self.testname = self.testfunc
		try:
			funcontex_path = self.testdir + self.testfunc + '.context'
			if len(funcontex_path) != 0:
				self.funcontex = pickle.load(open(funcontex_path, 'r'))
		except:
			self.funcontex = {}

		feature_db_path = self.testdir + self.testpogram + '.funcbody'
		self.func_feature_db = pickle.load(open(feature_db_path, 'r'))


		feature_datarefs_path = self.testdir + self.testpogram + '.dataref'
		self.func_datarefs = pickle.load(open(feature_datarefs_path, 'r'))


		feature_db_path = self.dbdir + self.dbprogram + '.dataref'
		self.datarefs = pickle.load(open(feature_db_path, 'r'))


		callgraph_path = self.dbdir + self.dbprogram + '.callgraph'
		self.callgraph = pickle.load(open(callgraph_path, 'r'))


		feature_db_path = self.dbdir + self.dbprogram + '.funcbody'
		self.feature_db = pickle.load(open(feature_db_path, 'r'))

		testcallgraph_path = self.testdir + self.testpogram + '.callgraph'
		self.testcallgraph = pickle.load(open(testcallgraph_path, 'r'))

	def matchall_preparing(self):

		testset_path = self.testdir + self.sharename + '.share'
		self.testset = pickle.load(open(testset_path, 'r'))

		testcontextls_path = self.testdir + self.sharename + '.contextls'
		self.testcontextls = pickle.load(open(testcontextls_path, 'r'))


		feature_db_path = self.testdir + self.testpogram + '.funcbody'
		self.func_feature_db = pickle.load(open(feature_db_path, 'r'))

		feature_db_path = self.testdir + self.testpogram + '.dugs'
		self.func_dug_db = pickle.load(open(feature_db_path, 'r'))

		feature_db_path = self.testdir + self.testpogram + '.dugs'
		self.dug_db = pickle.load(open(feature_db_path, 'r'))
		
		'''
		feature_datarefs_path = self.testdir + self.testpogram + '.dataref'
		self.func_datarefs = pickle.load(open(feature_datarefs_path, 'r'))

		feature_db_path = self.dbdir + self.dbprogram + '.dataref'
		self.datarefs = pickle.load(open(feature_db_path, 'r'))
		'''
		self.func_datarefs = {}
		self.datarefs = {}

		callgraph_path = self.dbdir + self.dbprogram + '.callgraph'
		self.callgraph = pickle.load(open(callgraph_path, 'r'))
		
		feature_db_path = self.dbdir + self.dbprogram + '.funcbody'
		self.feature_db = pickle.load(open(feature_db_path, 'r'))


	def prepare_test(self):
		test_context_path = self.testdir + self.testname + '.context'
		pdb.set_trace()
		test_context = Context(self.testname, self.testcallgraph, self.depth, self.type)
		pdb.set_trace()
		pickle.dump(test_context, open(test_context_path, 'wb'))

	def prepare_testset(self):
		testcontextls = {}
		test_context_path = self.testdir + self.testset['casename'] + '.contextls'
		pdb.set_trace()
		for testname in self.testset['data']:
			test_context = Context(testname, self.testcallgraph, self.depth, self.type)
			testcontextls[testname] = test_context
		pdb.set_trace()
		pickle.dump(testcontextls, open(test_context_path, 'wb'))


