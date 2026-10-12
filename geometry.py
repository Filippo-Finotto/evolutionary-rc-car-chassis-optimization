import numpy as np
from scipy.ndimage import gaussian_filter
import matplotlib.pyplot as plt

length = 200
width = 120
height = 15

grid_length = length/10
grid_width = width/10

heights = np.full((int(grid_length), int(grid_width)), height)
mask = np.full((int(grid_length), int(grid_width)), False)

mask[0,4] = True   # buchi differenziale anteriore  
mask[0,7] = True   # buchi differenziale anteriore
mask[2,4] = True   # buchi differenziale anteriore
mask[2,7] = True   # buchi differenziale anteriore
mask[3,3] = True     #buchi gabbia 
mask[3,8] = True     #buchi gabbia
mask[5,0] = True     #buchi gabbia
mask[5,11] = True    #buchi gabbia
mask[13,0] = True    #buchi gabbia
mask[13,11] = True   #buchi gabbia
mask[16,3]  = True   #buchi gabbia
mask[16,8] = True    #buchi gabbia
mask[5,4] = True       #buchi hardware
mask[5,7] = True       #buchi hardware
mask[8,4] = True       #buchi hardware
mask[8,7] = True       #buchi hardware
mask[14,4] = True      #buchi hardware
mask[14,7] = True      #buchi hardware
mask[17,4] = True   #buchi differenziale posteriore
mask[17,7] = True   #buchi differenziale posteriore
mask[19,4] = True   #buchi differenziale posteriore
mask[19,7] = True   #buchi differenziale posteriore

def generate_chassis(heights, mask):
    chassis = heights.copy()
    chassis[mask] = 15
    chassis = gaussian_filter(chassis, sigma=1)
    chassis[mask] = 15
    chassis[chassis < 1.5] = 0
    return chassis

heights2 = np.full((int(grid_length), int(grid_width)), 0.1)
chassis = generate_chassis(heights2, mask)
print(chassis)

plt.imshow(chassis, cmap='viridis')
plt.colorbar(label='Spessore (mm)')
plt.show()

