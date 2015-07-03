import cPickle as pickle
import networkx as nx
import pdb


class Context:

	def __init__(self, name, callgraph, depth, type_):
		self.func_name = name
		self.hoods = self.gen_hoods(name, callgraph, depth, type_)

	def gen_hoods(self, name, callgraph, t, type_):
		context = []
		if type_ == "predecessors":
			#self.obtain_predecessors(name, context, t, callgraph)
			#self.obtain_predecessorOnLevel(name, context, callgraph, {}, t)
			context = callgraph.predecessors(name)
		if type_ == "successors":
			#self.obtain_successors(name, context, t, callgraph)
			#self.obtain_successorOnLevel(name, context, callgraph, t)
			context = callgraph.successors(name)
		#if type_ == "all":
		#	self.obtain_predecessorOnLevel(name, context, callgraph, {}, t)
		#	self.obtain_successorOnLevel(name, context, callgraph, {}, t)
		return context

			
	def obtain_predecessors(self, name, context, t, callgraph):
		stack = [name]
		visited = {}
		depth = 0
		while len(stack) != 0 and depth <= t:
				node = stack.pop()
				visited[node] = 1
				depth += 1
				parents = callgraph.predecessors(node)
				for n in parents:
					if n not in visited:
						stack.append(n)
						context.add_edge(n, node)

	def obtain_successors(self, name, context, t):
		visited = {}
		depth = 0
		stack = [name]
		while len(stack) != 0 and depth <= t:
			node = stack.pop()
			visited[node] = 1
			depth += 1
			parents = callgraph.successors(node)
			for n in parents:
				if n not in visited:
					stack.append(n)
					context.add_edge(n, node)
	'''
	def obtain_successorOnLevel(self, node, context, callgraph, visited, t):
		if t == 0:
			return 
		else:
			parents = callgraph.successors(node)
			for n in parents:
				if n not in visited:
					context.add_edge(node, n)
					visited[n] = 1
					t = t -1
					self.obtain_successorOnLevel(n, context, callgraph, visited, t)
	'''

	def obtain_predecessorOnLevel(self, node, context, callgraph, visited, t):
		if t == 0:
			return 
		else:
			parents = callgraph.predecessors(node)
			for n in parents:
				if n not in visited:
					context.add_edge(n, node)
					visited[n] = 1
					t = t -1
					self.obtain_predecessorOnLevel(n, context, callgraph, visited, t)

	def obtainLevelNodes(self):
		levels = {}
		levels[0] = [self.func_name]
		leaf = False
		leaf_nodes = []
		stop = False
		level = 1
		while not stop:
			prev_level = level - 1
			leaf_nodes = []
			for cname in levels[prev_level]:
				try:
					nodes = self.context.successors(cname)
					if len(nodes) == 0:
						leaf_nodes.append(True)
					else:
						leaf_nodes.append(False)
						if level not in levels:
							levels[level] = nodes
						else:
							levels[level] += nodes
				except:
					leaf_nodes.append(True)
			if len(set(leaf_nodes)) == 1 and True in leaf_nodes:
				stop = True
			else:
				level += 1
		return levels

	def obtain_successorOnLevel(self, rootnode, context, callgraph, depth):
		levels = {}
		levels[0] = [rootnode]
		ls = 1
		context.add_node(rootnode)
		while depth != ls:
			prev_level = ls - 1
			for cname in levels[prev_level]:
				try:
					nodes = callgraph.successors(cname)
					for node in nodes:
						if node != cname:
							context.add_edge(cname, node)
					if ls not in levels:
						levels[ls] = nodes
					else:
						levels[ls] += nodes
				except:
					continue
			ls += 1


