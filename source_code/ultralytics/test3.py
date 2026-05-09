import numpy as np
from scipy.sparse import csr_matrix

# 节点数量
num_nodes = 5

# 边的列表，表示节点之间的连接
edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 4), (2, 3), (2, 4), (3, 4)]

# 创建一个邻接矩阵
row = np.array([edge[0] for edge in edges])
col = np.array([edge[1] for edge in edges])
data = np.ones(len(edges), dtype=int)

# 创建CSR格式的邻接矩阵
adj_matrix = csr_matrix((data, (row, col)), shape=(num_nodes, num_nodes))

# 打印邻接矩阵
print(adj_matrix.toarray())