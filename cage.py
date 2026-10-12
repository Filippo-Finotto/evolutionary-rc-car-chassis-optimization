#This module generates a cage from a set of fixed nodes and edges, and variable thicknesses


import numpy as np
import matplotlib
import matplotlib.pyplot as plt

nodes = np.array([[30, 30, 15],      #nodi di attacco allo chassis  0
                  [30, 80, 15],      #nodi di attacco allo chassis  1
                  [50, 0, 15],       #nodi di attacco allo chassis  2
                  [50, 110, 15],     #nodi di attacco allo chassis  3
                  [130, 0, 15],      #nodi di attacco allo chassis  4
                  [130, 110, 15],    #nodi di attacco allo chassis  5
                  [160, 30, 15],     #nodi di attacco allo chassis  6
                  [160, 80, 15],     #nodi di attacco allo chassis  7
                  [50, 0, 45],          #primo layer                8
                  [50, 110, 45],        #primo layer                9
                  [130, 0, 45],         #primo layer                10
                  [130, 110, 45],       #primo layer                11
                  [80, 10, 70],          #secondo layer             12
                  [80, 100, 70],         #secondo layer             13
                  [120, 10, 70],         #secondo layer             14
                  [120, 100, 70],        #secondo layer             15
                  [140, 20, 35],       #intermedi posteriori        16
                  [140, 90, 35]])      #intermedi posteriori        17



edges = np.array(
    [
        # --- 1. ZONA ANTERIORE / MUSETTO ---
        [0, 1],  # Traversa anteriore bassa
        [0, 2],
        [1, 3],  # Collegamento fondo musetto-cabina
        [0, 9],
        [1, 8],  # Obliqui frontali
        [0, 8],
        [1, 9],  # Puntoni obliqui dal musetto alla cintura
        # --- 2. MONTANTI INFERIORI CABINA (Da terra Z=15 a cintura Z=45) ---
        [2, 8],
        [3, 9],  # Montanti verticali anteriori
        [4, 10],
        [5, 11],  # Montanti verticali centrali
        [4, 16],
        [5, 17],
        # --- 3. FIANCATE E PORTIERE (Door Bars & Diagonali) ---
        [8, 10],
        [9, 11],  # Barre orizzontali portiere
        [2, 10],
        [4, 8],  # Croce diagonale fiancata sinistra
        [3, 11],
        [5, 9],  # Croce diagonale fiancata destra
        # --- 4. PARABREZZA (Dalla cintura Z=45 al tetto Z=70) ---
        [8, 12],
        [9, 13],  # Montanti del parabrezza
        [8, 9],  # Traversa inferiore parabrezza (Dash bar)
        [12, 13],  # Traversa superiore parabrezza
    
        # --- 5. ARCO CENTRALE / MAIN HOOP (Sopra la testa) ---
        [10, 14],
        [11, 15],  # Montanti superiori arco centrale
        [10, 11],  # Traversa orizzontale cinture (Harness bar)
        [10, 15],
        [11, 14],  # Croce diagonale arco centrale
        # --- 6. TETTO (Z=70) ---
        [12, 14],
        [13, 15],  # Longheroni laterali del tetto
        [14, 15],  # Traversa posteriore tetto
        [12, 15],
        [13, 14],  # Croce a 'X' sul tetto (Cruciale per la torsione!)
        # --- 7. DISCESA POSTERIORE E CROCE FIA ---
        [14, 16],
        [15, 17],  # Puntoni dal tetto agli snodi intermedi
        [16, 6],
        [17, 7],  # Puntoni dagli intermedi alla base posteriore
        [16, 17],  # Traversa intermedia posteriore
        [14, 17],
        [15, 16],  # Croce posteriore alta
        [16, 7],
        [17, 6],  # Croce posteriore bassa
        # --- 8. COLLEGAMENTI RETROTRENO ---
        [4, 6],
        [5, 7],  # Tiranti base cabina-retrotreno
        [10, 16],
        [11, 17],  # Tiranti cintura-intermedi posteriori
        [6, 7],  # Traversa retrotreno bassa
    ]
)

thicknesses = np.random.uniform(0, 2.5, edges.shape[0])

def generate_cage(nodes, edges, thicknesses, min_thickness):
    mask = (thicknesses >= min_thickness)
    
    active_edges = edges[mask]
    active_thicknesses = thicknesses[mask]
    return nodes, active_edges, active_thicknesses
    

nodi, archi, spessori = generate_cage(nodes, edges, thicknesses, 0.5)






fig = plt.figure()
ax = fig.add_subplot(projection='3d')

for i in range(nodi.shape[0]):
    ax.scatter(nodi[i,0], nodi[i,1], nodi[i,2], color = 'k')
    ax.text(nodi[i,0], nodi[i,1], nodi[i,2], str(i), color = 'r')

for (start, end), spessore in zip(archi, spessori):
    p1 = nodi[start]
    p2 = nodi[end]
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], color="blue", alpha=0.6, linewidth=spessore*1.5)



ax.set_aspect('equal')
plt.show()