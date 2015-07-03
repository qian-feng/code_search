import cPickle as pickle
import sys
import os
import pdb
import hungarian
import numpy
import matplotlib.pylab as plt
from db.db import *
def accuracy1(ddir):
	FP = {}
	hit = []
	miss = []
	total = 0
	datas = {}
	false = {}
	for exeName in os.listdir(ddir):
		if '.match' in exeName:
			print exeName
			data = pickle.load(open(os.path.join(ddir,exeName),'r'))
			datas[exeName] = data
			total += len(data)
			for funname in data:
				allnames = [v[0] for v in data[funname] if funname == v[0]]
				if len(allnames) == 0:
					false[funname] = 1
					continue
				m=min([v[1][0] for v in data[funname]])
				re=[v[0] for v in data[funname] if v[1][0] == m]
				if funname in re:
					hit.append(funname)
				else:
					miss.append((exeName,funname))
				if len(set(re)) != 1:
					FP[funname] = (exeName,[v for v in re if funname != v])
	fp1= {}
	for funname in FP:
		re=FP[funname][1]
		x=[v for v in re if v not in false]
		fp1[funname] = (FP[funname][0], len(x))

	pdb.set_trace()
	fp = sum([fp1[v][1] for v in fp1])
	print len(hit)
	print len(miss)
	print (len(hit)-len(miss))*1.0 / total
	print fp


def convert_llvmtostrip(strip_name, llvm_indexes):
	llvm_to_strip = {}
	src_name, src_version = split(strip_name)
	strip_indexes = obtain_stripindexes(strip_name, src_version)
	strip_bases = obtain_stripbases(src_name, src_version)
	for name in llvm_indexes:
		base = obtain_base(name, strip_indexes)
		if base in strip_bases:
			llvm_to_strip[name] = strip_bases[base]
	return llvm_to_strip

def accuracy(scorelist, matrix,  src_indexes, dst_indexes, bname):
	matrix = []
	#src_indexes = scorelist.keys()
	#dst_indexes = scorelist[scorelist.keys()[0]].keys()
	gt = obtain_addr_name_gt()
	individual_evl(matrix, src_indexes, dst_indexes, gt, bname)
	BGM_evl(matrix, src_indexes, dst_indexes, gt, bname)

def individual_evl(matrix, src_indexes, dst_indexes, gt, bname):
	total = len(gt)
	mid = 0
	hit = 0
	fp = 0
	gt_ea_pairs = gt['pair'][bname]['ea'].keys()
	for row in matrix:
		min_score = min(row)
		for column_id in xrange(len(row)):
			cost = row[column_id]
			if cost == min_score:
				if mid < len(src_indexes):
					src_name = src_indexes[mid]
				else:
					src_name = 'src_dummy'
				if column_id < len(dst_indexes):
					dst_name = dst_indexes[column_id]
				else:
					dst_name = 'dst_dummy'
				src = obtain_base(src_name, gt['mapping'][bname]['o0'])
				dst = obtain_base(dst_name, gt['mapping'][bname]['o3'])
				if (src, dst) in gt_ea_pairs:
					hit += 1
				else:
					fp += 1
		mid += 1
	pdb.set_trace()
	print "Individual matching false positives = " + str((fp) * 1.0/(fp+hit))
	print "Individual matching accuracy rate =" + str(hit*1.0/total)

def BGM_evl(matrix, src_indexes, dst_indexes, gt, bname):
	mapping = hungarian.lap(matrix)
	distance = caldistance(mapping, matrix)
	hit = 0
	gt_ea_pairs = gt['pair'][bname]['ea'].keys()
	print "Binary Similarity Socre is = " + str(distance)
	pdb.set_trace()
	index = -1
	miss = []
	for i in mapping[0]:
		index += 1
		try:
			src_name = src_indexes[index]
			dst_name = dst_indexes[i]
			src = obtain_base(src_name, gt['mapping'][bname]['o0'])
			dst = obtain_base(dst_name, gt['mapping'][bname]['o3'])
		except:
			continue
		if (src, dst) in gt_ea_pairs:
			hit += 1
		else:
			#pdb.set_trace()
			miss.append((src,dst))
			print "s"
	re = st(gt_ea_pairs, miss)
	pdb.set_trace()
	print "The BGM matching recall rate =" + str(hit*1.0/len(gt))

def st(gt_ea_pairs, miss):
	t = []
	for src, dst in miss:
		for x, y in gt_ea_pairs:
			if src == x:
				t.append((hex(src), (hex(src), hex(dst)), (hex(x),hex(y))))

	return t


def obtain_base(name, indexes):
	if 'sub_' in name:
		name = name.split('sub_')[1]
		base = int(name, 16)
		return base
	else:
		if 'driver_' in name:
			name = name.split('driver_')[1]
			if name == 'start':
				name = '_start'
			if name in indexes:
				return indexes[name]
			base = int(name, 16) 
			return base
		if name in indexes:
			return indexes[name]
	return False

def caldistance(mapping, node_matrix):
	cost = 0 
	for i in xrange(len(mapping[0])):
		cost += node_matrix[i][mapping[0][i]]
	return cost



if __name__=="__main__":
	ddir = sys.argv[-1]
	accuracy(ddir)