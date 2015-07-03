from Config import Config
import cPickle as pickle
import sys
import argparse
import pdb
class func_sig:
	def __init__(self):
		pass

	def func_sigGen(self, config_path, configtype, matchtype):
		config = Config(config_path, configtype, matchtype)
		config.obtainConfig(config_path)
		if matchtype == 'matchall':
			config.prepare_testset()
		else:
			config.prepare_test()

	def genTestSet(self, src, dst):
		testcase = {}
		src_funcs = pickle.load(open(src, 'r'))
		dst_funcs = pickle.load(open(dst, 'r'))
		shared = [v for v in src_funcs if v in dst_funcs]
		testcase['casename'] = 'chown'
		testcase['data'] = shared
		pickle.dump(testcase, open("/home/qian/data/BGM/IR/test/chown.share", 'wb'))

if __name__=="__main__":
	parser = argparse.ArgumentParser(description='Generate sigs for Contexted_based_match!')
	# Add arguments
	parser.add_argument(
	'--sig', type=bool, help='Sig', required=True)
	parser.add_argument(
	'--matchtype', type=str, help='Match Type', required=True)
	parser.add_argument(
	'--configtype', type=str, help='Config Type: match or sig', required=True)
	parser.add_argument(
	'--src', type=str, help='File directory 1, To generate shared functions ', required=False)
	parser.add_argument(
	'--dst', type=str, help='File directory 2, To generate shared functions', required=False, default=None)
	parser.add_argument(
	'--configpath', type=str, help='Conigure file path', required=True, default=None)
	# Array for all arguments passed to script
	args = parser.parse_args()
	# Assign args to variables
	sig = args.sig
	matchtype = args.matchtype
	configtype = args.configtype
	config_path = args.configpath
	src = args.src
	dst = args.dst
	f = func_sig()
	if matchtype == 'matchall':
		f.genTestSet(src, dst)
	f.func_sigGen(config_path, configtype, matchtype)
