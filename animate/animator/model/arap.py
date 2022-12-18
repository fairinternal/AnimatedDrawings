import numpy as np
from collections import defaultdict
from typing import List

class ARAP():
    """ 
    Implementation of:
    
    Takeo Igarashi and Yuki Igarashi. 
    "Implementing As-Rigid-As-Possible Shape Manipulation and Surface Flattening." 
    Journal of Graphics, GPU, and Game Tools, A.K.Peters, Volume 14, Number 1, pp.17-30, ISSN:2151-237X, June, 2009.

    https://www-ui.is.s.u-tokyo.ac.jp/~takeo/papers/takeo_jgt09_arapFlattening.pdf
    """
    
    def __init__(self, pin_v_idxs: np.ndarray, triangles:np.ndarray, vertices: np.ndarray):
        """
        cp_initial_pos: ndarray [N, 2] specifying initial xy positions of N control points
        mesh: the mesh to deformed
        vertices: a list of x,y pairs. A vertex's order in the list is it's vertex ID
        triangles: triplets of vertex IDs that make up a triangles
        """
        # For this to work, we find a new of new vertex coordinates that minimizes, in a least squares sense,
        # the difference between the initial mesh's edges and the deformed mesh's edges
        # We do this in a way that doesn't penalize translation or rotation, but does penalize scaling and shearing

        self.vertices = np.copy(vertices)

        tris = np.copy(triangles)

        self.cp_idxs = [tris[0][0], tris[0][2]]  # this is purely for development
        self.cp_idxs = pin_v_idxs  # this is purely for development

        # build a list of the edges in the mesh
        # edge direction isn't important, but we don't want an edge and it's pair
        # e.g., if we have (v_j - v_i) in list of edges, don't need (v_i - v_j) also

        self.e_v_idxs = []  # edge->vertex IDS
        for v0, v1, v2 in tris:
            # self.e_v_idxs.append(tuple(sorted((v0, v1))))
            # self.e_v_idxs.append(tuple(sorted((v1, v2))))
            # self.e_v_idxs.append(tuple(sorted((v2, v0))))
            self.e_v_idxs.append((v0, v1))
            self.e_v_idxs.append((v1, v2))
            self.e_v_idxs.append((v2, v0))
        #self.e_v_idxs = list(set(self.e_v_idxs))  # remove duplicates

        self.edge_num = len(self.e_v_idxs)
        self.vert_num = len(self.vertices)
        self.pin_num = len(self.cp_idxs)

        # build an array of edge vects
        _edge_vectors: List = []
        for vi_idx, vj_idx in self.e_v_idxs:
            vi = self.vertices[vi_idx]
            vj = self.vertices[vj_idx]
            _edge_vectors.append(vj - vi)
        self.edge_vectors: np.ndarray = np.array(_edge_vectors)

        # TODO: Update this
        #self.cp_initial_pos: np.ndarray = cp_initial_pos
        # for now, randomly choose 2 vertices to be our constraints

        # create list of vertex->vertex neighbors. 
        # Used later to get edge-> vertex neighbors
        from typing import Dict, Set
        v_vnbr_idxs: Dict[int, Set[int]] = defaultdict(set)  # vertex->vertex neighbor indices
        for v0, v1, v2 in tris:
            v_vnbr_idxs[v0] |= {v1, v2}
            v_vnbr_idxs[v1] |= {v2, v0}
            v_vnbr_idxs[v2] |= {v0, v1}

        # Initialize matrix A1. 
        # Rows equal to twice the number of edges plus the number of constraints (separate rows for x and y dimension)
        # Cols equal to twice the number of mesh vertices (separate cols for x and y dimensions)
        A1 = np.zeros([2 * (self.edge_num + self.pin_num), 2 * self.vert_num])

        # Initialize matrix G, which will hold intermediate values needed to calculate rotations in second step
        G = np.zeros([2 * self.edge_num, 2 * self.vert_num])

        for k, (vi_idx, vj_idx) in enumerate(self.e_v_idxs):

            # build a list of edge->vertex neighbors for this edge
            # first positions is vi, second position is vj, third (and fourth if applicable) are vl and vr (order doesn't matter)
            vi_vnbr_idxs: set = v_vnbr_idxs[vi_idx]
            vj_vnbr_idxs: set = v_vnbr_idxs[vj_idx]
            e_vnbr_idxs: list = list(vi_vnbr_idxs.intersection(vj_vnbr_idxs))
            e_vnbr_idxs.insert(0, vi_idx)
            e_vnbr_idxs.insert(1, vj_idx)

            e_vbr_locs: list = [self.vertices[v_idx] for v_idx in e_vnbr_idxs]

            edge_matrix: np.ndarray = np.array([
                [-1, 0, 1, 0, 0, 0],
                [0, -1, 0, 1, 0, 0],
            ])
            if len(e_vnbr_idxs) == 4:
                edge_matrix = np.hstack([edge_matrix, np.zeros([2, 2])])

            _: list = []
            for v in e_vbr_locs:
                _.extend(((v[0], v[1]), (v[1], -v[0])))
            G_k: np.ndarray = np.array(_)

            G_star:np.ndarray = np.linalg.inv(G_k.T @ G_k) @ G_k.T

            e_kx, e_ky = self.edge_vectors[k]
            e = np.array([
                [e_kx, e_ky],
                [e_ky, -e_kx]
            ], np.float32)

            h = edge_matrix - e @ G_star

            for h_offset, vertex_idx in enumerate(e_vnbr_idxs):
                A1[2*k, 2*vertex_idx] = h[0, 2 * h_offset]
                A1[2*k+1, 2*vertex_idx] = h[1, 2 * h_offset]
                A1[2*k, 2*vertex_idx+1] = h[0, 2 * h_offset + 1]
                A1[2*k+1, 2*vertex_idx+1] = h[1, 2 * h_offset + 1]

                G[2*k, 2*vertex_idx] = G_star[0, 2 * h_offset]
                G[2*k+1, 2*vertex_idx] = G_star[1, 2 * h_offset]
                G[2*k, 2*vertex_idx+1] = G_star[0, 2 * h_offset + 1]
                G[2*k+1, 2*vertex_idx+1] = G_star[1, 2 * h_offset + 1]

        # now do the constraints
        w = 1000
        self.w = w
        for c_idx, v_idx in enumerate(self.cp_idxs):
            A1[2*len(self.e_v_idxs) + 2*c_idx, 2*v_idx] = w  # x component
            A1[2*len(self.e_v_idxs) + 2*c_idx + 1, 2*v_idx + 1] = w  # y component


        self.G = G
        self.A_1 = A1
        self.tA_1 = self.A_1.transpose()
        self.tA_1xA_1 = self.tA_1 @ self.A_1
        ########################
        #  self.A2 top
        ########################
        A_2_top = np.zeros([self.edge_num, self.vert_num])
        for k, (vi_idx, vj_idx) in enumerate(self.e_v_idxs):
            A_2_top[k, vi_idx] = -1
            A_2_top[k, vj_idx] = 1
        self.A2_top = A_2_top
        ########################
        #  self.A2 bottom
        ########################
        A_2_bot = np.zeros([self.pin_num, self.vert_num])
        for row, pin_idx in enumerate(self.cp_idxs):
            A_2_bot[row, pin_idx] = 1.0 * w
        self.A2_bot = A_2_bot
        ########################
        #  stack
        ########################
        self.A2 = np.vstack([self.A2_top, self.A2_bot])
        self.tA2 = self.A2.transpose()
        self.tA2xA2 = self.tA2 @ self.A2




        # now do B
        B_1 = np.zeros([2*self.edge_num + 2*self.pin_num])
        for c_idx, v_idx in enumerate(self.cp_idxs):
            c_x, c_y = self.vertices[v_idx]
            B_1[2*len(self.e_v_idxs) + 2*c_idx] = w * c_x
            B_1[2*len(self.e_v_idxs) + 2*c_idx+1] = w * c_y
        
        self.A_1 = A1
        self.B_1 = B_1

        #v1 = np.linalg.lstsq(A_1.T @ A_1, A_1.T @ B_1)
        x = 2


    def solve(self, pin_poses):
        # pin_poses should be a set of xy positions of the pin locations
        assert len(pin_poses) == self.pin_num
        self.pin_poses = np.asarray(pin_poses)

        #############
        # create b1
        #############
        # TODO: speed this up by just creating zero array, reshape pin_positions in Nx1 vector, then vstack
        b1 = np.zeros([2 * self.edge_num + 2 * self.pin_num])
        for idx, (pin_x, pin_y) in enumerate(self.pin_poses):
            row_idx = 2 * self.edge_num + 2 * idx
            b1[row_idx] = self.w * pin_x
            b1[row_idx + 1] = self.w * pin_y
        self.b1 = b1

        v1 = np.linalg.solve(self.tA_1xA_1, self.tA_1 @ self.b1)
        # IT WORKS!
        x = 2

        T1 = self.G @ v1
        b2 = []
        for idx, edge in enumerate(self.e_v_idxs):
            #e0 = self.vertices[edge[1]] - self.vertices[edge[0]]  # TODO:this works, but why does edge need to go in opposite direction?
            e0 = self.vertices[edge[1]] - self.vertices[edge[0]]  
            c = T1[2*idx]
            s = T1[2*idx + 1]
            rScale = 1.0 / np.sqrt(c * c + s * s)  # compute scale
            c *= rScale;  # scale
            s *= rScale  # scale
            T2 = np.asarray(((c, s), (-s, c)))  # compute new rotation matrix
            #e1 = np.dot(T2.T, e0)  # multiply to get values within b
            e1 = np.dot(T2, e0)  # multiply to get values within b
            b2.extend(e1)  # add it in
        for idx, pin_pose in enumerate(self.pin_poses):  # for each pin
            #pinPos = pinPoses[row, :]  # get both x and y
            b2.extend(self.w * pin_pose)  # multiply by weight and extend
        b2 = np.asarray(b2).reshape(-1, 2)  # reshape and return
        #return b2

        v2x = np.linalg.solve(self.tA2xA2, self.tA2 @ b2[:, 0])
        v2y = np.linalg.solve(self.tA2xA2, self.tA2 @ b2[:, 1])
        v2 = np.vstack((v2x, v2y)).T

        return v2



        # for handle in handle_positions:
        #     self.pinPoses.append((handle[0], handle[1]))
        # self.pinPoses = np.asarray(self.pinPoses)

        pass
            # now we need to add them back into the top of the A matrix
            # we store results in h in the kth row,
            # we use the colum corresponding to vertex's idx, 
            # and put at even loc for x coordiante, odd loc of y coordinate

        # get a collection of triangles vertex locations
        # use them to generate half edges
        # get the barycentric coordinates for each handle


def plot_mesh(vertices, triangles, pins_idxs):
    import matplotlib.pyplot as plt
    x_points = []  # vertices[:,0]
    y_points = []  # vertices[:,1]

    for tri in triangles:
        v0, v1, v2 = tri.tolist()
        x_points.append(vertices[v0][0])
        y_points.append(vertices[v0][1])
        x_points.append(vertices[v1][0])
        y_points.append(vertices[v1][1])
        x_points.append(vertices[v2][0])
        y_points.append(vertices[v2][1])
        x_points.append(vertices[v0][0])
        y_points.append(vertices[v0][1])

    plt.plot(x_points, y_points)
    plt.ylim((-10, 10))
    plt.xlim((-10, 10))

    for pin in pins_idxs:
        plt.plot(vertices[pin][0], vertices[pin][1], color='red', marker='o')

    plt.show()




# from model import halfedge
# import scipy.sparse as sp
# import scipy.sparse.linalg as spla
# import scipy.linalg as la
# class old_ARAP():
# 
#     def __init__(self, pin_idxs, vertices, triangles):
#         self.vertices = vertices
#         self.triangles = triangles
#         self.pins = []
#         for pin_idx in pin_idxs:
#             self.pins.append([[pin_idx, 1.0]])
#         self.pins = np.array(self.pins)
#         #self.pins = np.expand_dims(np.array(self.pins), axis=0)
#         # np.asarray([
#         #     [[0, 1.0], [1, 0.0], [2, 0.0]],
#         #     [[0, 0.0], [1, 0.0], [2, 1.0]],
#         # ])
# 
#         self._arap_setup()
# 
#     def _arap_setup(self):
#         """ Called once during object construction to generate the reusable parts of the ARAP matrices"""
#         self.xy = self.vertices  # self.triangle_mesh['vertices']
#         #self.halfedges = halfedge.build(self.triangle_mesh['triangles'])  # builds the halfedge structure from triangles
#         self.halfedges = halfedge.build(self.triangles)  # builds the halfedge structure from triangles
#         self.heVectors = np.asarray([self.xy[he.ivertex, :] - self.xy[he.prev().ivertex, :] for he in self.halfedges])
#         # self.pins = []
#         # for handle in self.arap_handles:
#         #     self.pins.append(handle.v_idx)
#         #self.pins = np.asarray(self.pins)
# 
#         self.w = 1000.0
#         self.nVertices = self.xy.shape[0]
#         self.edges, self.heIndices = halfedge.toEdge(self.halfedges)
#         self.nEdges = self.edges.shape[0]
#         self.A1top, self.G = self._buildA1top(self.heVectors, self.halfedges, self.edges, self.heIndices, self.nVertices)
#         self.A1bottom = self._buildA1bottom(self.pins, self.w, self.nVertices)
# 
#         self.A1 = sp.vstack((self.A1top, self.A1bottom))
#         self.tA1 = self.A1.transpose()
#         self.tA1xA1 = self.tA1 * self.A1
# 
#         self.A2top = self._buildA2top(self.edges, self.nVertices)
#         self.A2bottom = self._buildA2bottom(self.pins, self.w, self.nVertices)
# 
#         self.A2 = sp.vstack((self.A2top, self.A2bottom))
#         self.tA2 = self.A2.transpose()
#         self.tA2xA2 = self.tA2 * self.A2
# 
#     def _buildA1top(self, heVectors, halfedges, edges, heIndices, nVertices):
# 
#             threeVertices2twoEdges = np.asarray(((-1., 0., 1., 0., 0., 0.),
#                                                 (0., -1., 0., 1., 0., 0.),
#                                                 (-1., 0., 0., 0., 1., 0.),
#                                                 (0., -1., 0., 0., 0., 1.)))
#             fourVertices2threeEdges = np.asarray(((-1., 0., 1., 0., 0., 0., 0., 0.),
#                                                 (0., -1., 0., 1., 0., 0., 0., 0.),
#                                                 (-1., 0., 0., 0., 1., 0., 0., 0.),
#                                                 (0., -1., 0., 0., 0., 1., 0., 0.),
#                                                 (-1., 0., 0., 0., 0., 0., 1., 0.),
#                                                 (0., -1., 0., 0., 0., 0., 0., 1.)))
# 
#             # initialize lists
#             Arows = []
#             Acols = []
#             Adata = []
#             Grows = []
#             Gcols = []
#             Gdata = []
#             
#             #for every edge in edges
#             for row in range(0, edges.shape[0]):  # edges are directed, but inverses aren't included
#                 v0, v1 = edges[row, :]  # v0, v1 are index of start, end edge vertices
#                 Arows.append(2 * row);  # for vector v0 x coord, set row indices...
#                 Acols.append(2 * v0);   # col indices
#                 Adata.append(-1.0)      # value of -1
#                 Arows.append(2 * row);  # Do the same for v1
#                 Acols.append(2 * v1);
#                 Adata.append(1.0)
#                 Arows.append(2 * row + 1);  # now do it for the y coord of v0
#                 Acols.append(2 * v0 + 1);
#                 Adata.append(-1.0)
#                 Arows.append(2 * row + 1);  # and the y coord of v1
#                 Acols.append(2 * v1 + 1);
#                 Adata.append(1.0)
# 
#                 vertices = [v0, v1]
#                 he = halfedges[heIndices[row]]  # get a half edge corresponding to this row (edge)
#                 edgeVectors = [heVectors[he.iself], ]  # create array with delta xy representing half edge vector
#                 vertices.append(halfedges[he.inext].ivertex)  # add the vertex idx of next half edge's vertex
#                 edgeVectors.append(-heVectors[he.prev().iself])  # add the previous half edge's vector info
#                 verts2edges = threeVertices2twoEdges
#                 if he.ipair != -1:  # if this isn't a boundary half edge
#                     pair = halfedges[he.ipair]
#                     vertices.append(halfedges[pair.inext].ivertex)
#                     edgeVectors.append(heVectors[pair.inext])
#                     verts2edges = fourVertices2threeEdges
# 
#                 # this creates the final line of matrices bottom of page 22
#                 g = []
#                 for v in edgeVectors:  # edge vector now contains current halfedge vertex xy and previous halfedge vertex xy
#                     g.extend(((v[0], v[1]), (v[1], -v[0])))
#                 g = np.asarray(g)
#                 e = heVectors[heIndices[row], :]  # the x y location of edge (starting?) vertex
#                 e = np.asarray(((e[0], e[1]), (e[1], -e[0])))
#                 g = np.dot(la.inv(np.dot(g.T, g)), g.T)
#                 g = np.dot(g, verts2edges)
#                 h = - np.dot(e, g)
#                 rows = []
#                 cols = []
#                 for i in range(0, len(vertices)):
#                     rows.append(2 * row);
#                     cols.append(2 * vertices[i])
#                     rows.append(2 * row);
#                     cols.append(2 * vertices[i] + 1)
#                 for i in range(0, len(vertices)):
#                     rows.append(2 * row + 1);
#                     cols.append(2 * vertices[i])
#                     rows.append(2 * row + 1);
#                     cols.append(2 * vertices[i] + 1)
# 
#                 data = h.flatten()
#                 Arows.extend(rows)
#                 Acols.extend(cols)
#                 Adata.extend(data)
#                 Grows.extend(rows)
#                 Gcols.extend(cols)
#                 Gdata.extend(g.flatten())
#             spA1top = sp.csr_matrix((Adata, (Arows, Acols)), shape=(edges.size, nVertices * 2))
#             spG = sp.csr_matrix((Gdata, (Grows, Gcols)), shape=(edges.size, nVertices * 2))
#             return spA1top, spG
# 
#     def _buildA1bottom(self, pins, w, nVertices):
#             Arows = []
#             Acols = []
#             Adata = []
#             for row in range(0, len(pins)):
#                 for pin in pins[row]:
#                     pin_idx = pin[0]
#                     pin_weight = pin[1] * w
#                     # pin = pins[row]
#                     Arows.append(2 * row)
#                     Acols.append(2 * pin_idx)
#                     Adata.append(pin_weight)
#                     Arows.append(2 * row + 1)
#                     Acols.append(2 * pin_idx + 1)
#                     Adata.append(pin_weight)
#             spA1bottom = sp.csr_matrix((Adata, (Arows, Acols)), shape=(pins.shape[0] * 2, nVertices * 2))
#             return spA1bottom
# 
#     def _buildB1(self, pinPositions, w, nEdges):
#         brows = range(nEdges * 2, nEdges * 2 + pinPositions.size)
#         bcols = [0 for i in range(0, len(brows))]
#         bdata = (w * pinPositions).flatten()
#         bshape = (nEdges * 2 + pinPositions.size, 1)
#         b1 = sp.csr_matrix((bdata, (brows, bcols)), shape=bshape)
#         return b1
# 
#     def _buildA2top(self, edges, nVertices):
#         Arow = []
#         Acol = []
#         Adata = []
#         for row in range(0, edges.shape[0]):
#             v0, v1 = edges[row, :]
#             Arow.append(row);
#             Acol.append(v0);
#             Adata.append(-1)
#             Arow.append(row);
#             Acol.append(v1);
#             Adata.append(1)
#         shape = (edges.shape[0], nVertices)
#         spA2top = sp.csr_matrix((Adata, (Arow, Acol)), shape=shape)
#         return spA2top
# 
#     def _buildA2bottom(self, pins, w, nVertices):
#         Arow = []
#         Acol = []
#         Adata = []
#         for row in range(0, pins.shape[0]):
#             for pin in pins[row]:
#                 pin_idx = pin[0]
#                 pin_weight = pin[1] * w
#                 Arow.append(row)
#                 Acol.append(pin_idx)
#                 Adata.append(pin_weight)
#         shape = (pins.shape[0], nVertices)
#         spA2bottom = sp.csr_matrix((Adata, (Arow, Acol)), shape=shape)
#         return spA2bottom
# 
#     def _buildB2(self, heVectors, heIndices, edges, pinPoses, w, G, v1):
#         T1 = G * v1
#         b2 = []
#         for row in range(0, edges.shape[0]):
#             e0 = heVectors[heIndices[row], :]
#             c = T1[2 * row];
#             s = T1[2 * row + 1]
#             rScale = 1.0 / np.sqrt(c * c + s * s)
#             c *= rScale;
#             s *= rScale
#             T2 = np.asarray(((c, s), (-s, c)))
#             e1 = np.dot(T2, e0)
#             b2.extend(e1)
#         for row in range(0, pinPoses.shape[0]):
#             pinPos = pinPoses[row, :]
#             b2.extend(w * pinPos)
#         b2 = np.asarray(b2).reshape(-1, 2)
#         return b2
# 
#     def _arap_solve(self, handle_positions):
# 
#         self.pinPoses = []
#         for handle in handle_positions:
#             self.pinPoses.append((handle[0], handle[1]))
#         self.pinPoses = np.asarray(self.pinPoses)
#         # for handle in self.arap_handles:
#         #     self.pinPoses.append((handle.cx, 1 - handle.cy))
#         # self.pinPoses = np.asarray(self.pinPoses)
# 
#         b1 = self._buildB1(self.pinPoses, self.w, self.nEdges)
#         v1 = spla.spsolve(self.tA1xA1, self.tA1 * b1)
# 
#         b2 = self._buildB2(self.heVectors, self.heIndices, self.edges, self.pinPoses, self.w, self.G, v1)
#         v2x = spla.spsolve(self.tA2xA2, self.tA2 * b2[:, 0])
#         v2y = spla.spsolve(self.tA2xA2, self.tA2 * b2[:, 1])
#         v2 = np.vstack((v2x, v2y)).T
# 
#         return v2
#         # for idx in range(self.mesh_vertices.shape[0]):
#         #     self.mesh_vertices[idx, 0] = v2[idx][0]
#         #     self.mesh_vertices[idx, 1] = 1 - v2[idx][1]
#     #######################
#     # End ARAP functions
#     ######################