#This module generates a cage from a set of fixed nodes and edges, and variable thicknesses


import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from dataclasses import dataclass

@dataclass
class Cage:
    nodes : np.ndarray
    active_edges : np.ndarray
    active_thicknesses : np.ndarray

nodes = np.array(
    [
        # nodes that attach to the chassis
        [35.0, 35.0, 15.0],  
        [35.0, 85.0, 15.0],  
        [55.0, 5.0, 15.0],      
        [55.0, 115.0, 15.0],  
        [135.0, 5.0, 15.0],  
        [135.0, 115.0, 15.0], 
        [165.0, 35.0, 15.0],  
        [165.0, 85.0, 15.0],  
        # first layer
        [55.0, 5.0, 45.0],  
        [55.0, 115.0, 45.0],  
        [135.0, 5.0, 45.0],  
        [135.0, 115.0, 45.0],  
        # second layer
        [85.0, 15.0, 70.0],  
        [85.0, 105.0, 70.0],  
        [125.0, 15.0, 70.0],  
        [125.0, 105.0, 70.0],  
        #intermediate nodes on the back
        [145.0, 25.0, 35.0],  
        [145.0, 95.0, 35.0],  
    ]
)


edges = np.array(
    [
        [0, 1],  #front
        [0, 2],
        [1, 3], 
        [0, 9],
        [1, 8],  
        [0, 8],
        [1, 9],  
        
        [2, 8],  #center
        [3, 9],  
        [4, 10],
        [5, 11], 
        [4, 16],
        [5, 17],
        
        [8, 10],  #sides
        [9, 11],  
        [2, 10],
        [4, 8],  
        [3, 11],
        [5, 9],  
        
        [8, 12],
        [9, 13],  
        [8, 9], 
        [12, 13],  
    
       
        [10, 14],
        [11, 15],  
        [10, 11], 
        [10, 15],
        [11, 14],  
        
        [12, 14],
        [13, 15],  
        [14, 15],  
        [12, 15],
        [13, 14],  
        
        [14, 16],
        [15, 17],  
        [16, 6],
        [17, 7],  
        [16, 17],  
        [14, 17],
        [15, 16],  
        [16, 7],
        [17, 6],  
        [4, 6],
        [5, 7],  
        [10, 16],
        [11, 17],  
        [6, 7],  
    ]
)

#thicknesses = np.random.uniform(0, 2.5, edges.shape[0])

def generate_cage(nodes, edges, thicknesses, min_thickness):
    
    mask = (thicknesses >= min_thickness)
    
    active_edges = edges[mask]
    active_thicknesses = thicknesses[mask]
    cage = Cage(nodes, active_edges, active_thicknesses)
    return cage




# Still code I used to test this module

#cage = generate_cage(nodes, edges, thicknesses, 0.5)

#fig = plt.figure()
#ax = fig.add_subplot(projection='3d')
#
#for i in range(cage.nodes.shape[0]):
#    ax.scatter(cage.nodes[i,0], cage.nodes[i,1], cage.nodes[i,2], color = 'k')
#    ax.text(cage.nodes[i,0], cage.nodes[i,1], cage.nodes[i,2], str(i), color = 'r')
#
#for (start, end), spessore in zip(cage.active_edges, cage.active_thicknesses):
#    p1 = cage.nodes[start]
#    p2 = cage.nodes[end]
#    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], color="blue", alpha=0.6, linewidth=spessore*1.5)
#
#
#
#ax.set_aspect('equal')
#plt.show()