#
# Reference Lister
#
# List all functions and all references to them in the current section.
#
# Implemented with the idautils module
#
try:
    from idautils import *
    from idaapi import *
    from idc import *
except:
    pass
import networkx as nx
import cPickle as pickle
import pdb
import sqlite3
import argparse
import os
#import wingdbstub
#wingdbstub.Ensure()

def get_func_bases(filename):
        funcs = {}
        ea = FirstSeg()
        for funcea in Functions(SegStart(ea)):
                funcname = GetFunctionName(funcea)
                funcs[funcname] = funcea
        pickle.dump(funcs, open("./" + filename,'wb'))
        return funcs

def load_funcs(funname):
    funcs = pickle.load(open(funname, 'r'))
    return funcs

def mapping(filename1, filename2):
    mapping = {}
    fp = open('./opensshl.share','w')
    funcs1 = load_funcs(filename1)
    funcs2 = load_funcs(filename2)
    #pdb.set_trace()
    for name1 in funcs1:
        if name1 in funcs2:
            addr1 = funcs1[name1]
            addr2 = funcs2[name1]
            mapping[name1] = (addr1, addr2)
    for v in mapping:
        fp.write(v + '\n')
    fp.close()
    #pickle.dump(mapping, open("./" + mappingname,'wb'))
    return mapping, funcs1, funcs2

def load_diffdb(filepath):
    conn = sqlite3.connect(filepath)
    cur = conn.cursor()
    cur.execute("select address1,address2 from function;")
    rows = cur.fetchall()
    return rows, cur

def bindiff_evaluation(filename1, filename2, bindiff_path):
    maps, funcs1, funcs2 = mapping(filename1, filename2)
    match_result, cur = load_diffdb(bindiff_path)
    miss = {}
    hit = []
    for func_name in maps:
	if '@' in func_name:
		continue
        pair = maps[func_name]
        if pair in match_result:
            hit.append(func_name)
        else:
            miss[func_name] = pair
    #pdb.set_trace()
    if len(match_result) == 0:
        print  0
        #print len(maps)
    else:
        #print "accuracy " + str(len(hit)*1.0/len(match_result))
        print str(len(hit) * 1.0 / len(maps))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--srcdir", help="matched program name")
    parser.add_argument("--dstdir", help="matched program name")
    parser.add_argument("--diff_dir", help="matched program name")
    # ***************Experiment II: Bipartite Graph Matching ***************************
    args = parser.parse_args()
    src_dir = args.srcdir
    dst_dir = args.dstdir
    diff_dir = args.diff_dir
    for sfile in os.listdir(src_dir):
        if sfile.endswith(".func"):
            sname = sfile.split('_')[0]
            spath = os.path.join(src_dir, sfile)
            for dfile in os.listdir(dst_dir):
                if dfile.endswith('.func'):
                    dname = dfile.split('_')[0]
                    if sname == dname:
                        dpath = os.path.join(dst_dir, dfile)
                        for diff in os.listdir(diff_dir):
                            diffname= diff.split('_')[0]
                            if sname == diffname and dname ==diffname:
                                diffpath = os.path.join(diff_dir, diff)
                                bindiff_evaluation(spath, dpath, diffpath)


        
