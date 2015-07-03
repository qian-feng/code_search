import cPickle as pickle
import sys
import os
import pdb
import hungarian
import numpy
import matplotlib.pylab as plt
from db import *
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


def obtain_groundtruth(src_bname, dst_bname):
	src_bname, blevel, bsymbol, barch = parse_binary_name(src_name)
	dst_bname, dlevel, dsymbol, darch = parse_binary_name(dst_name)
	conn, cur = connect()




def accuracy(scorelist, src_name, dst_name, src_indexes, dst_indexes):
	matrix = []
	#src_indexes = scorelist.keys()
	#dst_indexes = scorelist[scorelist.keys()[0]].keys()
	gt, src_strip_indexes, dst_strip_indexes = obtain_node_indexes(src_name,dst_name,src_indexes,dst_indexes)
	src_len = len(src_indexes)
	dst_len = len(dst_indexes)
	matrix_len = max(src_len, dst_len)
	for row_id in xrange(matrix_len):
		row = []
		if row_id >= src_len:
			src_name = 'src_dummy'
		else:
			src_name = src_indexes[row_id]
		for column_id in xrange(matrix_len):
			if column_id >= dst_len:
				dst_name = 'dst_dummy'
			else:
				dst_name = dst_indexes[column_id]
			if row_id == 15 and column_id == 9:
				pdb.set_trace()
				print "s"
			try:
				if src_name == 'src_dummy' or dst_name == 'dst_dummy':
					cost = 1000
				else:
					cost = scorelist[src_name][dst_name]
			except:
				cost = scorelist[dst_name][src_name]
			row.append(cost)
		matrix.append(row)
	individual_evl(matrix, src_indexes, dst_indexes, gt, src_strip_indexes, dst_strip_indexes)
	BGM_evl(matrix, src_indexes, dst_indexes, gt, src_strip_indexes, dst_strip_indexes)

def individual_evl(matrix, src_indexes, dst_indexes, gt, src_strip_indexes, dst_strip_indexes):
	
	total = len(gt)
	mid = 0
	hit = 0
	fp = 0

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
				src = obtain_base(src_name, src_strip_indexes)
				dst = obtain_base(dst_name, dst_strip_indexes)
				if (src, dst) in gt:
					hit += 1
				else:
					fp += 1
		mid += 1

	print "Individual matching false positives = " + str((fp) * 1.0/(fp+hit))
	print "Individual matching accuracy rate =" + str(hit*1.0/total)

def BGM_evl(matrix, src_indexes, dst_indexes, gt, src_strip_indexes, dst_strip_indexes):
	mapping = hungarian.lap(matrix)
	distance = caldistance(mapping, matrix)
	hit = 0
	print "Binary Similarity Socre is = " + str(distance)
	pdb.set_trace()
	index = -1
	miss = []
	for i in mapping[0]:
		index += 1
		try:
			src = obtain_base(src_indexes[index], src_strip_indexes)
			dst = obtain_base(dst_indexes[i], dst_strip_indexes)
		except:
			continue
		if (src, dst) in gt:
			hit += 1
		else:
			#pdb.set_trace()
			miss.append((src,dst))
			print "s"
	re = st(gt, miss)
	pdb.set_trace()
	print "The BGM matching recall rate =" + str(hit*1.0/len(gt))

def st(gt, miss):
	t = []
	for src, dst in miss:
		for x, y in gt:
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