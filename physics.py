import math
from cage import generate_cage
from geometry import generate_chassis
import numpy as np

density = 0.00125  # g/mm^3 PLA CF
young_modulus = 3000.0  # MPa (N/mm^2) Young's Modulus for PLA CF



# calculates the total mass of the body
def mass(chassis, cage):   
    cell_area = 100.0  # mm^2
    chassis_mass = np.sum(chassis) * cell_area * density

    cage_volume = 0.0
    for (start, end), thickness in zip(cage.active_edges, cage.active_thicknesses):

        edge_length = np.linalg.norm(cage.nodes[start] - cage.nodes[end])
        edge_area = pow(thickness / 2.0, 2) * math.pi
        cage_volume += edge_length * edge_area

    return chassis_mass + cage_volume * density


#given an edge returns the local stiffness matrix for that edge
def edge_stiffness_3d(p1, p2, area):

    delta = np.array(p2) - np.array(p1)     # delta X
    L = np.linalg.norm(delta)               # euclidean norm of delta X  

    if L < 1e-6 or area <= 0.0:
        return np.zeros((6, 6))

    c = delta / L                           # unit vector of direction cosines for the edge
    k_sub = np.outer(c, c)                  # 3x3 matrix, outer product of c with itself, how any force on the edge gets decomposed along each axis
    coeff = (young_modulus * area) / L      #elastic constant for Hooke's law

    # k local is the matrix of how each force affects the edge relating each force to the movement of the two nodes
    k_local = coeff * np.block([[k_sub, -k_sub], [-k_sub, k_sub]])    

    return k_local


# transforms the chassis from a 2d matrix to a graph connecting the nodes
def get_chassis_elements(chassis, cell_size=10.0, z_height=15.0):
    n_rows, n_cols = chassis.shape

    # converting the chassis indexing to mm
    floor_nodes = []             
    for r in range(n_rows):
        for c in range(n_cols):
            x = r * cell_size
            y = c * cell_size
            z = z_height
            floor_nodes.append([x, y, z])
    floor_nodes = np.array(floor_nodes, dtype=float)

    def node_idx(r, c):         #transform the indexing row-column in a single vector 0-239
        return r * n_cols + c

    edges = []
    areas = []
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]      #directions to avoid duplicates

    for r in range(n_rows):
        for c in range(n_cols):
            t1 = chassis[r, c]
            if t1 <= 0.0:
                continue
            idx1 = node_idx(r, c)            #first node index

            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < n_rows and 0 <= nc < n_cols:
                    t2 = chassis[nr, nc]
                    if t2 > 0.0:                       # checks the neighbors to find one that still exists
                        t_eff = min(t1, t2)            # effective thickness is the bottleneck
                        area = t_eff * cell_size       # approximation of the chassis as a graph 
                        idx2 = node_idx(nr, nc)
                        edges.append([idx1, idx2])
                        areas.append(area)

    floor_edges = (
        np.array(edges, dtype=int) if edges else np.empty((0, 2), dtype=int)
    )
    floor_areas = (
        np.array(areas, dtype=float) if areas else np.empty((0,), dtype=float)
    )

    return floor_nodes, floor_edges, floor_areas      # returns the list of all nodes, all edges between them and their thicknesses



# puts the chassis and cage toghether in a single structure

def assemble_vehicle(chassis, cage, cell_size=10.0):
    n_rows, n_cols = chassis.shape
    floor_nodes, floor_edges, floor_areas = get_chassis_elements(
        chassis, cell_size=cell_size
    )
    n_floor_nodes = floor_nodes.shape[0]  # 240 nodes

    upper_cage_nodes = cage.nodes[8:]       # nodes that are not connected to the chassis just get appended to the nodes
    all_nodes = np.vstack([floor_nodes, upper_cage_nodes])     

    cage_to_global = {}
    for i in range(8):
        x, y, _ = cage.nodes[i]
        r = int(x // cell_size)
        c = int(y // cell_size)
        cage_to_global[i] = r * n_cols + c

    for i in range(8, cage.nodes.shape[0]):
        cage_to_global[i] = n_floor_nodes + (i - 8)

    translated_cage_edges = []
    for start, end in cage.active_edges:
        translated_cage_edges.append(
            [cage_to_global[start], cage_to_global[end]]
        )

    translated_cage_edges = (
        np.array(translated_cage_edges, dtype=int)
        if len(translated_cage_edges) > 0
        else np.empty((0, 2), dtype=int)
    )
    cage_areas = (
        np.pi * (cage.active_thicknesses / 2.0) ** 2
        if len(cage.active_thicknesses) > 0
        else np.empty((0,), dtype=float)
    )

    if len(floor_edges) > 0 and len(translated_cage_edges) > 0:
        all_edges = np.vstack([floor_edges, translated_cage_edges])
        all_areas = np.concatenate([floor_areas, cage_areas])
    elif len(floor_edges) > 0:
        all_edges = floor_edges
        all_areas = floor_areas
    else:
        all_edges = translated_cage_edges
        all_areas = cage_areas

    return all_nodes, all_edges, all_areas


# calulates the global stiffness matrix for the whole body
def build_global_stiffness(all_nodes, all_edges, all_areas):
    n_nodes = all_nodes.shape[0]             # 250 nodes
    n_dofs = n_nodes * 3                     # total degrees of freedom: 750
    K = np.zeros((n_dofs, n_dofs), dtype=float)           

    for (start, end), area in zip(all_edges, all_areas):
        if area <= 0.0:
            continue

        p1 = all_nodes[start]
        p2 = all_nodes[end]
        delta = p2 - p1
        L = np.linalg.norm(delta)
        if L < 1e-6:
            continue

        k_local = edge_stiffness_3d(p1, p2, area)

        if abs(p1[2] - 15.0) < 1e-3 and abs(p2[2] - 15.0) < 1e-3:         # if the node is part of the chassis
            t_local = area / 10.0
            k_flex_z = (young_modulus * 10.0 * (t_local**3)) / (L**3)     # calculates the vertical stiffness with the Eulero-Bernoulli formula

            k_local[2, 2] += k_flex_z               # and adds it to the vertical component of the local matrix
            k_local[5, 5] += k_flex_z
            k_local[2, 5] -= k_flex_z
            k_local[5, 2] -= k_flex_z

        dofs = [                # global indexes of the 6 degrees of freedom in the global matrix
            3 * start,
            3 * start + 1,
            3 * start + 2,
            3 * end,
            3 * end + 1,
            3 * end + 2,
        ]

        K[np.ix_(dofs, dofs)] += k_local    # sums the 36 entries in the global matrix

    return K           # returns the full matrix



# solves the linear systems for various forces applied in key points blocking the car in certain other points
def solve_load_cases(K, n_cols=12):
    n_dofs = K.shape[0]

    K_reg = K + np.eye(n_dofs) * 1e-3

    front_screws = [0 * n_cols + 4, 0 * n_cols + 7]  # [0, 4]  [0, 7]
    rear_screws = [19 * n_cols + 4, 19 * n_cols + 7]  # [19, 4]  [19, 7]
    cage_front_wide = [5 * n_cols + 0, 5 * n_cols + 11]  # [5, 0]  [5, 11]
    cage_rear_wide = [13 * n_cols + 0, 13 * n_cols + 11]  # [13, 0]  [13, 11]

    total_flection = 0.0
    total_torsion = 0.0

    # tests 1-4 are performed keeping the rear  screws fixed
    fixed_rear = []
    for node in rear_screws:
        fixed_rear.extend([3 * node, 3 * node + 1, 3 * node + 2])
    fixed_rear = np.unique(fixed_rear)
    free_rear = np.setdiff1d(np.arange(n_dofs), fixed_rear)
    K_free_rear = K_reg[np.ix_(free_rear, free_rear)]

    try:
        # Test 1: applying a downward force of -100 N on [0,4] e [0,7]
        F1 = np.zeros(n_dofs)
        for n in front_screws:
            F1[3 * n + 2] = -100.0
        u1 = np.zeros(n_dofs)
        u1[free_rear] = np.linalg.solve(K_free_rear, F1[free_rear])
        total_flection += abs(
            (u1[3 * front_screws[0] + 2] + u1[3 * front_screws[1] + 2]) / 2.0
        )

        # Test 2: applying an upward force of +100 N on [0,4] e [0,7]
        F2 = np.zeros(n_dofs)
        for n in front_screws:
            F2[3 * n + 2] = +100.0
        u2 = np.zeros(n_dofs)
        u2[free_rear] = np.linalg.solve(K_free_rear, F2[free_rear])
        total_flection += abs(
            (u2[3 * front_screws[0] + 2] + u2[3 * front_screws[1] + 2]) / 2.0
        )

        # Test 3: appling two opposite forces to create torsion +100 N on [5,0], -100 N on [5,11]
        F3 = np.zeros(n_dofs)
        F3[3 * cage_front_wide[0] + 2] = +100.0
        F3[3 * cage_front_wide[1] + 2] = -100.0
        u3 = np.zeros(n_dofs)
        u3[free_rear] = np.linalg.solve(K_free_rear, F3[free_rear])
        total_torsion += abs(
            u3[3 * cage_front_wide[0] + 2] - u3[3 * cage_front_wide[1] + 2]
        )

        # Test 4: applying two opposite forces to create torsion -100 N on [5,0], +100 N su [5,11]
        F4 = np.zeros(n_dofs)
        F4[3 * cage_front_wide[0] + 2] = -100.0
        F4[3 * cage_front_wide[1] + 2] = +100.0
        u4 = np.zeros(n_dofs)
        u4[free_rear] = np.linalg.solve(K_free_rear, F4[free_rear])
        total_torsion += abs(
            u4[3 * cage_front_wide[0] + 2] - u4[3 * cage_front_wide[1] + 2]
        )

    except np.linalg.LinAlgError:
        return 100.0, 100.0

    # tests 5-8 are performed applying the same type of forces on the back of the car keeping the front screws fixed
    fixed_front = []
    for node in front_screws:
        fixed_front.extend([3 * node, 3 * node + 1, 3 * node + 2])
    fixed_front = np.unique(fixed_front)
    free_front = np.setdiff1d(np.arange(n_dofs), fixed_front)
    K_free_front = K_reg[np.ix_(free_front, free_front)]

    try:
        F5 = np.zeros(n_dofs)
        for n in rear_screws:
            F5[3 * n + 2] = -100.0
        u5 = np.zeros(n_dofs)
        u5[free_front] = np.linalg.solve(K_free_front, F5[free_front])
        total_flection += abs(
            (u5[3 * rear_screws[0] + 2] + u5[3 * rear_screws[1] + 2]) / 2.0
        )

        F6 = np.zeros(n_dofs)
        for n in rear_screws:
            F6[3 * n + 2] = +100.0
        u6 = np.zeros(n_dofs)
        u6[free_front] = np.linalg.solve(K_free_front, F6[free_front])
        total_flection += abs(
            (u6[3 * rear_screws[0] + 2] + u6[3 * rear_screws[1] + 2]) / 2.0
        )

        F7 = np.zeros(n_dofs)
        F7[3 * cage_rear_wide[0] + 2] = +100.0
        F7[3 * cage_rear_wide[1] + 2] = -100.0
        u7 = np.zeros(n_dofs)
        u7[free_front] = np.linalg.solve(K_free_front, F7[free_front])
        total_torsion += abs(
            u7[3 * cage_rear_wide[0] + 2] - u7[3 * cage_rear_wide[1] + 2]
        )

        F8 = np.zeros(n_dofs)
        F8[3 * cage_rear_wide[0] + 2] = -100.0
        F8[3 * cage_rear_wide[1] + 2] = +100.0
        u8 = np.zeros(n_dofs)
        u8[free_front] = np.linalg.solve(K_free_front, F8[free_front])
        total_torsion += abs(
            u8[3 * cage_rear_wide[0] + 2] - u8[3 * cage_rear_wide[1] + 2]
        )

    except np.linalg.LinAlgError:
        return 100.0, 100.0

    return total_flection, total_torsion   



# calculates mass and deflection of a given body
def evaluate_vehicle(chassis, cage, cell_size=10.0):
    total_mass = mass(chassis, cage)
    all_nodes, all_edges, all_areas = assemble_vehicle(
        chassis, cage, cell_size=cell_size
    )
    K = build_global_stiffness(all_nodes, all_edges, all_areas)
    def_torsione, def_flessione = solve_load_cases(K, n_cols=chassis.shape[1])
    total_deflection = def_torsione + def_flessione
    return total_mass, total_deflection


if __name__ == "__main__":
    from cage import edges, nodes
    from geometry import mask

    raw_heights = np.full(mask.shape, 2.0)
    test_chassis = generate_chassis(raw_heights, mask)

    test_thicknesses = np.full(edges.shape[0], 0.3)
    test_cage = generate_cage(nodes, edges, test_thicknesses, min_thickness=0.5)

    test_mass, test_deflection = evaluate_vehicle(test_chassis, test_cage)

    print("=" * 40)
    print(f"Total Mass:        {test_mass:.2f} g")
    print(f"Total Deflection:  {test_deflection:.4f} mm")
    print("=" * 40)