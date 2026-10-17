import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter

length = 200
width = 120
height = 15.0
cell_size = 10.0
cylinder_radius = 5.0

grid_length = length / cell_size
grid_width = width / cell_size
n_rows = int(grid_length)
n_cols = int(grid_width)

mask = np.full((n_rows, n_cols), False)

mask[0, 4] = True  # buchi differenziale anteriore
mask[0, 7] = True  # buchi differenziale anteriore
mask[2, 4] = True  # buchi differenziale anteriore
mask[2, 7] = True  # buchi differenziale anteriore
mask[3, 3] = True  # buchi gabbia
mask[3, 8] = True  # buchi gabbia
mask[5, 0] = True  # buchi gabbia
mask[5, 11] = True  # buchi gabbia
mask[13, 0] = True  # buchi gabbia
mask[13, 11] = True  # buchi gabbia
mask[16, 3] = True  # buchi gabbia
mask[16, 8] = True  # buchi gabbia
mask[5, 4] = True  # buchi hardware
mask[5, 7] = True  # buchi hardware
mask[8, 4] = True  # buchi hardware
mask[8, 7] = True  # buchi hardware
mask[14, 4] = True  # buchi hardware
mask[14, 7] = True  # buchi hardware
mask[17, 4] = True  # buchi differenziale posteriore
mask[17, 7] = True  # buchi differenziale posteriore
mask[19, 4] = True  # buchi differenziale posteriore
mask[19, 7] = True  # buchi differenziale posteriore

def get_cylinder_centers(mask, cell_size=cell_size):

    rows, cols = np.where(mask)
    center_x = (rows + 0.5) * cell_size
    center_y = (cols + 0.5) * cell_size
    return np.column_stack([center_x, center_y])


cylinder_centers = get_cylinder_centers(mask)

def generate_chassis(heights, mask, radius=cylinder_radius):

    centers = get_cylinder_centers(mask)

    rows_grid, cols_grid = np.indices((n_rows, n_cols))
    X_grid = (rows_grid + 0.5) * cell_size
    Y_grid = (cols_grid + 0.5) * cell_size

    dists = np.zeros((n_rows, n_cols))
    for r in range(n_rows):
        for c in range(n_cols):
            pt = np.array([X_grid[r, c], Y_grid[r, c]])
            dists[r, c] = np.min(np.linalg.norm(centers - pt, axis=1))

    background = gaussian_filter(heights, sigma=1.0)
    background[background < 1.5] = 0.0

    chassis = background.copy()

    inside_cylinder = dists <= radius
    chassis[inside_cylinder] = float(height)

    fillet_width = 8.0 
    outside_fillet = (dists > radius) & (dists <= radius + fillet_width)

    decay = np.cos(
        ((dists[outside_fillet] - radius) / fillet_width) * (np.pi / 2.0)
    )
    chassis[outside_fillet] = np.maximum(
        chassis[outside_fillet],
        background[outside_fillet]
        + (float(height) - background[outside_fillet]) * decay,
    )

    return chassis


if __name__ == "__main__":
    test_heights = np.full((n_rows, n_cols), 5.0)
    test_chassis = generate_chassis(test_heights, mask)

    plt.figure(figsize=(7, 5))
    plt.imshow(test_chassis, cmap="turbo", vmin=0.0, vmax=15.0, interpolation= "bicubic")
    plt.colorbar(label="Spessore (mm)")
    plt.title(f"Pianale con Cilindri Fissi (Raggio: {cylinder_radius} mm)")
    plt.show()