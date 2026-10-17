from cage import edges, generate_cage, nodes
from geometry import (
    cell_size,
    cylinder_centers,
    cylinder_radius,
    generate_chassis,
    height,
    length,
    mask,
    width,
)
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np

n_rows, n_cols = mask.shape
raw_heights = np.full(mask.shape, 3.5)


chassis_discrete = generate_chassis(raw_heights, mask, radius=cylinder_radius)

test_thicknesses = np.full(edges.shape[0], 1)
cage = generate_cage(nodes, edges, test_thicknesses, min_thickness=0.5)


fig = plt.figure(figsize=(13, 8))
ax = fig.add_subplot(111, projection="3d")

x_fine = np.linspace(0, length, 110)
y_fine = np.linspace(0, width, 70)
Y_fine_grid, X_fine_grid = np.meshgrid(y_fine, x_fine)

Z_surface = np.full_like(X_fine_grid, 3.5)



fillet_width = 7.0  
for cx, cy in cylinder_centers:
    dist = np.sqrt((X_fine_grid - cx) ** 2 + (Y_fine_grid - cy) ** 2)

    inside = dist <= cylinder_radius
    Z_surface[inside] = height

    fillet = (dist > cylinder_radius) & (dist <= cylinder_radius + fillet_width)
    decay = np.cos(
        ((dist[fillet] - cylinder_radius) / fillet_width) * (np.pi / 2.0)
    )
    Z_surface[fillet] = np.maximum(
        Z_surface[fillet],
        Z_surface[fillet] + (height - Z_surface[fillet]) * decay,
    )


surf = ax.plot_surface(
    X_fine_grid,
    Y_fine_grid,
    Z_surface,
    cmap="turbo",
    vmin=0.0,
    vmax=15.0,
    edgecolor="none",
    alpha=0.6,
    antialiased=True,
    zorder=1,
)

Z_zero = np.zeros_like(Z_surface)
ax.plot_surface(
    X_fine_grid, Y_fine_grid, Z_zero, color="#2f4f4f", alpha=0.35, zorder=1
)

X_wall_lr = np.vstack([x_fine, x_fine])
ax.plot_surface(
    X_wall_lr,
    np.zeros_like(X_wall_lr),
    np.vstack([np.zeros_like(Z_surface[:, 0]), Z_surface[:, 0]]),
    color="#20b2aa",
    alpha=0.45,
    zorder=1,
)
ax.plot_surface(
    X_wall_lr,
    np.full_like(X_wall_lr, width),
    np.vstack([np.zeros_like(Z_surface[:, -1]), Z_surface[:, -1]]),
    color="#20b2aa",
    alpha=0.45,
    zorder=1,
)

Y_wall_fb = np.vstack([y_fine, y_fine])
ax.plot_surface(
    np.zeros_like(Y_wall_fb),
    Y_wall_fb,
    np.vstack([np.zeros_like(Z_surface[0, :]), Z_surface[0, :]]),
    color="#20b2aa",
    alpha=0.45,
    zorder=1,
)
ax.plot_surface(
    np.full_like(Y_wall_fb, length),
    Y_wall_fb,
    np.vstack([np.zeros_like(Z_surface[-1, :]), Z_surface[-1, :]]),
    color="#20b2aa",
    alpha=0.45,
    zorder=1,
)


for (start, end), spessore in zip(cage.active_edges, cage.active_thicknesses):
    p1 = cage.nodes[start]
    p2 = cage.nodes[end]
    ax.plot(
        [p1[0], p2[0]],
        [p1[1], p2[1]],
        [p1[2], p2[2]],
        color="#d50000",
        linewidth=spessore * 2.0,
        zorder=100,  
        solid_capstyle="round",
    )

upper_nodes = cage.nodes[8:]
ax.scatter(
    upper_nodes[:, 0],
    upper_nodes[:, 1],
    upper_nodes[:, 2],
    color="black",
    s=40,
    depthshade=False,
    zorder=110,
)


ax.set_title(
    "RC Buggy prototype 1:10 - Chassis & Cage",
    fontsize=14,
    fontweight="bold",
)
ax.set_xlabel("X (Length mm)")
ax.set_ylabel("Y (Width mm)")
ax.set_zlabel("Z (Height mm)")

ax.set_aspect("equal")
ax.view_init(elev=32, azim=-55)

cbar = fig.colorbar(
    surf,
    ax=ax,
    shrink=0.5,
    aspect=12,
    pad=0.1,
    orientation="horizontal",
    ticks=[0, 3, 6, 9, 12, 15],
)
cbar.set_label("Chassis thickness (mm)")

ax.legend(loc="upper left")
plt.tight_layout()
plt.show()