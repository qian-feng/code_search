//===- Hello.cpp - Example code from "Writing an LLVM Pass" ---------------===//
//
//                     The LLVM Compiler Infrastructure
//
// This file is distributed under the University of Illinois Open Source
// License. See LICENSE.TXT for details.
//
//===----------------------------------------------------------------------===//
//
// This file implements two versions of the LLVM "Hello World" pass described
// in docs/WritingAnLLVMPass.html
//
//===----------------------------------------------------------------------===//

#include "llvm/ADT/Statistic.h"
#include "llvm/IR/Function.h"
#include "llvm/Pass.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/InstIterator.h"
#include "llvm/IR/CFG.h"
#include "llvm/Support/FileSystem.h"
#include <igraph.h>
#include <stack> 
#include <iostream>
#include <fstream> 
using namespace llvm;

#define DEBUG_TYPE "hello"

STATISTIC(HelloCounter, "Counts number of functions greeted");

namespace {
  // Hello - The first implementation, without getAnalysisUsage.
  struct Hello : public FunctionPass {
    static char ID; // Pass identification, replacement for typeid
    Hello() : FunctionPass(ID) {}

    bool runOnFunction(Function &F) override {

      errs() << "Generating cfg for the function \t: " << F.getName() << ":\n";
      cfg_attr.clear();
      inst_map.clear();
      inst_dic.clear();
      igraph_vector_init(&v1, 0);
      igraph_create(&cfg, &v1, 0, 1);
      generateCFG(F);
      generateDUchin(F);
      //dumpOpseq(F);
      // The BB graph has a single entry vertex from which the other BBs should
      // be discoverable - the function entry block.
    }
private:
  enum Color {WHITE, GREY, BLACK};
  // Color marks per vertex (BB).
  typedef DenseMap<const BasicBlock *, Color> BBColorMap;
  // Collects vertices (BBs) in "finish" order. The first finished vertex is
  // first, and so on.
  typedef std::map<const Value *, igraph_integer_t> INST_map;
  typedef std::map<igraph_integer_t, const Value *> INST_dic;
  typedef DenseMap<const BasicBlock *, int> CFG_Attr;
  //typedef DenseMap<igraph_integer_t, const BasicBlock *> CFG_Index;
  typedef DenseMap<int, igraph_t *> BB_DU;
  typedef std::pair<const Value *, igraph_integer_t> inst_pair;
  typedef std::pair<igraph_integer_t, const Value *> dic_pair;
  typedef DenseMap<igraph_integer_t, BasicBlock *> CFG_Index;
  INST_map inst_map; 
  INST_dic inst_dic;
  igraph_t dug;
  igraph_vector_t mv;
  BBColorMap ColorMap;
  CFG_Attr cfg_attr;
  CFG_Index CFG_node_index;
  BB_DU bb_du;
  igraph_t cfg;
  igraph_vector_t v1;

  // Helper function to recursively run topological sort from a given BB.
  // Returns true if the sort succeeded and false otherwise; topological sort
  // may fail if, for example, the graph is not a DAG (detected a cycle).
  bool linkNeighbors(const BasicBlock *BB, raw_fd_ostream &stat_ostream) {
      ColorMap[BB] = Hello::GREY;
      // For demonstration, using the lowest-level APIs here. A BB's successors
      // are determined by looking at its terminator instruction.
      const TerminatorInst *TInst = BB->getTerminator();
      stat_ostream << *BB << "\n";
      stat_ostream << TInst->getNumSuccessors() <<"\n";
      for (unsigned I = 0, NSucc = TInst->getNumSuccessors(); I < NSucc; ++I) {
          BasicBlock *Succ = TInst->getSuccessor(I);
          Color SuccColor = ColorMap[Succ];
          igraph_integer_t dst_id;
          if (SuccColor == Hello::WHITE){
              igraph_add_vertices(&cfg, 1, 0);
              dst_id = igraph_vcount(&cfg) - 1;
              cfg_attr[Succ] = dst_id;
              CFG_node_index[dst_id] = Succ;
              ColorMap[Succ] = Hello::BLACK;
              linkNeighbors(Succ, stat_ostream);
          }
          else{
            dst_id = cfg_attr[Succ];
          }
          igraph_integer_t srt_id = cfg_attr[BB];
          igraph_add_edge(&cfg, srt_id, dst_id);
          if (SuccColor == Hello::GREY) {
            continue;
          }
      }
      ColorMap[BB] = Hello::BLACK;
      return true;
    }

  bool generateCFG(Function &F){
      // Initialize the color map by marking all the vertices white.
      for (Function::const_iterator I = F.begin(), IE = F.end(); I != IE; ++I) 
      {
        ColorMap[I] = Hello::WHITE;
        //errs() << *I;
      }
      std::string fname = F.getName();
      std::string path = "/home/qian/statistic/" + fname;
      std::string errorMessage = ""; 
      raw_fd_ostream stat_ostream(path.c_str(), errorMessage, llvm::sys::fs::F_None);
      BasicBlock *entryBB = &F.getEntryBlock();
      igraph_add_vertices(&cfg, 1, 0);
      igraph_integer_t id = igraph_vcount(&cfg) - 1;
      cfg_attr[entryBB] = id;
      CFG_node_index[id] = entryBB;
      bool success = linkNeighbors(entryBB, stat_ostream);
      if (success) {
          typedef DenseMap<const BasicBlock *, igraph_integer_t>::iterator it_type;
          igraph_vector_t neis;
          for(it_type iterator = cfg_attr.begin(); iterator != cfg_attr.end(); iterator++) {
                const BasicBlock * BB = iterator->first;
                igraph_integer_t id = iterator->second;
                igraph_vector_init(&neis, 0);
                /*
                errs() << " Test BB " << *BB << "\n";
                
                int re = igraph_neighbors(&cfg, &neis, id, IGRAPH_OUT);
                for (int i=0; i<igraph_vector_size(&neis); i++) {
                    errs() << " \t\tNeighbors-----> " <<  *CFG_node_index[VECTOR(neis)[i]] << "\n";
                }
                */
                
          }
      } else {
            errs() << " Sorting failed\n";
            return false;
      }
      return true;
  }

  bool generateDUchin(Function &F){
      std::stack<BasicBlock *> bb_stack;
      CFG_Attr visited;
      std::ofstream outfile;
      igraph_vector_t neis;
      std::string ErrInfo = "";
      std::string fname = F.getName();
      std::string path = "/home/qian/data/mcsema/IR/dug0/" + fname + ".index";
      std::string errorMessage = ""; 
      raw_fd_ostream example_ostream(path.c_str(), errorMessage, llvm::sys::fs::F_None);
      igraph_vector_init(&neis, 0);
      igraph_vector_init(&mv, 0);
      igraph_create(&dug, &mv, 0, 1); //Create dug graph for the current function.
      BasicBlock *entryBB = &F.getEntryBlock();
      igraph_integer_t id = cfg_attr[entryBB];
      std::string dir = "/home/qian/data/mcsema/IR/seq0/";
      std::string name = F.getName();
      std::string filepath = dir + name ;
      outfile.open(filepath.c_str());
      //bb_du[id] = duc;
      bb_stack.push(entryBB);
      while(!bb_stack.empty()){
          BasicBlock * BB = bb_stack.top();
          genBBchain(BB, example_ostream);
          dumpOpseq(BB, outfile);
          visited[BB] = 1;
          bb_stack.pop();
          id = cfg_attr[BB];
          igraph_neighbors(&cfg, &neis, id, IGRAPH_OUT);
          for (int i=0; i<igraph_vector_size(&neis); i++) {
              //errs() << " -----> " <<  *CFG_node_index[VECTOR(neis)[i]] << "\n";
              BasicBlock * neiBB = CFG_node_index[VECTOR(neis)[i]];
              if (! iscontainBB(&visited, neiBB)){
                  bb_stack.push(neiBB);
              }
          }
      }
      dumpDUG(F);
      //dumpGML();
      
      
  }

  void dumpOpseq(BasicBlock * BB, std::ofstream &outfile ){
      for (BasicBlock::iterator i = BB->begin(), e=BB->end(); i != e; ++i ) {
          Instruction *inst = i;
          outfile<< inst->getOpcodeName() << '\n';
      }

  }

  void dumpDUG(Function &f){
      std::string fname = f.getName();
      std::string path = "/home/qian/data/mcsema/IR/dug0/" + fname + ".gml";
      const char * pathc = path.c_str();
      FILE * fp = fopen(pathc,"w");
      igraph_write_graph_gml(&dug, fp, 0, "test");
  }
  /*
      CFG_Attr visited;
    igraph_vector_t neis;
    std::ofstream outfile;
    std::string dir = "/home/qian/code_search/IR/seq/";
    std::string name = F.getName();
    std::string filepath = dir + name ;
    outfile.open(filepath.c_str());
    std::stack<BasicBlock *> bb_stack;
    BasicBlock *entryBB = &F.getEntryBlock();
    igraph_vector_init(&neis, 0);
    //bb_du[id] = duc;
    bb_stack.push(entryBB);
    while(!bb_stack.empty()){
  void dumpDUG(){
    //dug, instruction id list
    visited[BB] = 1;
            bb_stack.pop();
            igraph_integer_t id = cfg_attr[BB];
            igraph_neighbors(&cfg, &neis, id, IGRAPH_OUT);
            for (int i=0; i<igraph_vector_size(&neis); i++) {
                //errs() << " -----> " <<  *CFG_node_index[VECTOR(neis)[i]] << "\n";
                BasicBlock * neiBB = CFG_node_index[VECTOR(neis)[i]];
                if (! iscontainBB(&visited, neiBB)){
                    bb_stack.push(neiBB);
                }
            }
  }
  */

  bool iscontain(const char * opname, char * test){
      if(strcmp(opname,test) == 0){
          return true;
      }
      return false;
  }

  bool iscontainBB(CFG_Attr * visited, const BasicBlock * BB){
      DenseMap<const BasicBlock *, int>::iterator search = visited->find(BB);
      if (search == visited->end()){
        return false;
      }
      return true;
  }

  void genBBchain(BasicBlock *BB, raw_fd_ostream &example_ostream){
      //errs() << "BB: " << *BB << "\n";
      int index = 0;
      char * store = "store";
      char * br = "br";
      char * call = "call";
      //example_ostream << "digraph  {" << "\n";
      //llvm::raw_ostream *out = new llvm::raw_fd_ostream(path.c_str(), ErrInfo, llvm::sys::fs::F_None);
      for (BasicBlock::iterator i = BB->begin(), e=BB->end(); i != e; ++i ) {
          Instruction *inst = i;
          igraph_integer_t dst_id;
          //inst->print(example_ostream);

          //char * x= inst->print(errs());
          //fprintf(fp, "%s\n", x);
          if (iscontain(i->getOpcodeName(),br))
              continue;
          /*
          if (iscontain(i->getOpcodeName(),store)){
              Value *v1 = i->getOperand(0);
              Value *v2 = i->getOperand(1);
              src_id = graph_search_node(v1);
              int dst_id = graph_search_node(v2);
              igraph_add_edge(&dug, src_id, dst_id);
              //errs() << *v1 << "->" << *v2<< "\n";
              index += 1;
              errs() << *v1 << "->" << *v2 << "\n";
              //example_ostream << src_id <<"[label=\""<< *v1 <<"\"]\n";
              example_ostream << dst_id <<"[label=\""<< *v2 <<"\"]\n";
              continue;
          }
          */
          if (index == 0){
              index += 1;
              igraph_add_vertices(&dug, 1, 0);
              dst_id = igraph_vcount(&dug) - 1;
              inst_map[inst] = dst_id;
              inst_dic[dst_id] = inst;
          }
          else{
              dst_id = graph_search_node(inst); 
          }
          example_ostream << dst_id << ":" << inst->getOpcodeName() <<"\n";
          if (iscontain(i->getOpcodeName(),store)){
              Value *v1 = i->getOperand(0);
              Value *v2 = i->getOperand(1);
              int src_id = graph_search_node(v1);
              igraph_add_edge(&dug, src_id, dst_id);
              continue;
          }
          if (iscontain(i->getOpcodeName(), call)){
              continue;
          }
          for (Use &U : inst->operands()) {
              Value *v = U.get();
              //errs() << "\t\t\t\tUse:--> \t\t" << *v << "\n";
              int src_id = graph_search_node(v);
              if (src_id > dst_id){
                if (dyn_cast<Instruction>(v)){
                    Instruction *I = dyn_cast<Instruction>(v);
                    example_ostream << src_id << ":" << I->getOpcodeName() <<"\n";
                  }
                else
                    {example_ostream << src_id << ":" << *v <<"\n";}
              }
              igraph_add_edge(&dug, src_id, dst_id);
              //errs() << *inst << "->" << *v << "\n";
          }
      }
  }


  int graph_search_node(Value *inst){
    std::map<const Value *, igraph_integer_t>::iterator search = inst_map.find(inst);
    if (search == inst_map.end()){
        igraph_add_vertices(&dug, 1, 0);
        igraph_integer_t src_id = igraph_vcount(&dug) - 1;
        inst_map.insert(inst_pair(inst, src_id));
        inst_dic.insert(dic_pair(src_id, inst));
        return src_id;
    }
    else{
      if (inst_map.size()==0){
          igraph_add_vertices(&dug, 1, 0);
          igraph_integer_t src_id = igraph_vcount(&dug) - 1;
          inst_map.insert(inst_pair(inst, src_id));
          inst_dic.insert(dic_pair(src_id, inst));
          return src_id;
      }
      else{
          return search->second;
      }
    }
  }
};
}
char Hello::ID = 0;
static RegisterPass<Hello> X("hello0", "Hello World Pass");
