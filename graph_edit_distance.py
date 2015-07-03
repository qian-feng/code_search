import hungarian
def graph_node_distance(g1, g2):
	cost_matrix = []
	g1_indexs = g1.nodes()
	g2_indexs = g2.nodes()
	matrix_len = max(len(g1), len(g2))
	min_len = min(len(g1), len(g2))
	diff = min_len *1.0 / matrix_len
	if diff < 0.5:
		return 100
	for row_id in xrange(matrix_len):
		row = []
		for column_id in xrange(matrix_len):
			src = obtain_node(g1, g1_indexs, row_id)
			dst = obtain_node(g2, g2_indexs, column_id)
			cost = cal_nodecost(src, dst)
			row.append(cost)
		cost_matrix.append(row)
	if len(cost_matrix) == 0:
		return 10
	mapping = hungarian.lap(cost_matrix)
	distance = caldistance(mapping, cost_matrix)
	return distance

def graph_edge_distance(g1, g2):
	cost_matrix = []
	g1_indexs = g1.edges()
	g2_indexs = g2.edges()
	matrix_len = max(len(g1), len(g2))
	min_len = min(len(g1), len(g2))
	diff = min_len *1.0 / matrix_len
	if diff < 0.5:
		return 100
	for row_id in xrange(matrix_len):
		row = []
		for column_id in xrange(matrix_len):
			src = obtain_edge(g1, g1_indexs, row_id)
			dst = obtain_edge(g2, g2_indexs, column_id)
			cost = cal_edgecost(src, dst)
			row.append(cost)
		cost_matrix.append(row)
	if len(cost_matrix) == 0:
		return 10
	mapping = hungarian.lap(cost_matrix)
	distance = caldistance(mapping, cost_matrix)
	return distance

def cal_edgecost(edge1, edge2):
	src_cost = cal_nodecost(edge1[0], edge2[0])
	dst_cost = cal_nodecost(edge1[1], edge2[1])
	return src_cost + dst_cost

def cal_nodecost(node1, node2):
	if node1 == node2:
		return 0
	else:
		return 1

def obtain_edge(g, g_indexes, edge_id):
	g_len = len(g_indexes)
	if edge_id < (g_len - 1):
		edge = g_indexes[edge_id]
		if 'label' in g.node[edge[0]]:
			src = g.node[edge[0]]['label']
		else:
			src = 'src_dummy_node'
		if 'label' in g.node[edge[1]]:
			dst = g.node[edge[1]]['label']
		else:
			dst = 'dst_dummy_node'
		return (src, dst)
	else:
		return "src_dummy_node"

def obtain_node(g, g_indexes, node_id):
	g_len = len(g_indexes)
	if node_id < (g_len - 1):
		return g.node[g_indexes[node_id]]['label']
	else:
		return "src_dummy_node"

def caldistance(mapping, cost_matrix):
	cost = 0 
	for i in xrange(len(mapping[0])):
		cost += cost_matrix[i][mapping[0][i]]
	return cost

