import numpy as np
import multiprocessing as mp
import matplotlib.pyplot as plt
from perlin_noise import PerlinNoise
import random

import todatapack


def compute_row(args):
    """Compute a single row of the height map."""
    i, size, scale1, scale2, noise1, noise2 = args
    row = np.zeros(size)
    for j in range(size):
        row[j] = ((noise1([i / scale1, j / scale1]) + 0.5) * 10) + ((noise2([i / scale2, j / scale2]) + 0.5) * 150)
    return i, row

def generate_height_map(size, seed=None, scale1=200, scale2=800):
    """Generate height map using multiprocessing."""
    height_map = np.zeros((size, size))  # Initialize height map

    if not seed:
        seed = random.randint(1, 10000)
        print("[INFO] Using Seed: {}".format(seed))

    noise1 = PerlinNoise(octaves=3, seed=seed)
    noise2 = PerlinNoise(octaves=1, seed=seed+1)

    # Use multiprocessing Pool
    with mp.Pool(mp.cpu_count()) as pool:
        results = pool.map(compute_row, [(i, size, scale1, scale2, noise1, noise2) for i in range(size)])

    # Store results in height_map
    for i, row in results:
        height_map[i] = row

    return height_map


if __name__ == "__main__":
    # Generate terrain
    size = 1000
    height_map = generate_height_map(size=size)


    # Plot terrain
    x = np.linspace(0, size, size)
    y = np.linspace(0, size, size)
    x, y = np.meshgrid(x, y)

    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(x, y, height_map, cmap='terrain', edgecolor='none')

    ax.set_title(f"Downhill Race Track")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Height")
    plt.show()


    user_wants = input("Do you want to go with this map? [Y/n]:")

    if user_wants in ["y", "Y", ""]: # im lazy
        gradient_x, gradient_y = np.gradient(height_map)
        gradient_map = np.sqrt(gradient_x ** 2 + gradient_y ** 2)

        conditions = [
            {
                "function": lambda grad_x, grad_y, grad_mag: 0 < grad_mag < 0.02,  # grass
                "id": 0
            },
            {
                "function": lambda grad_x, grad_y, grad_mag: 0.02 < grad_mag < 0.1,  # grass
                "id": 1
            },
            {
                "function": lambda grad_x, grad_y, grad_mag: 0.1 < grad_mag < 0.18,  # sloped
                "id": 2
            },

            {
                "function": lambda grad_x, grad_y, grad_mag: 0.18 < grad_mag,  # steep
                "id": 3
            },
        ]

        block_map = np.zeros_like(height_map, dtype=int)

        # Loop through conditions and apply them
        for i, condition in enumerate(conditions):
            print(f"Applying Mask {i+1}...")
            # Apply the condition using np.where
            condition_mask = np.vectorize(condition["function"])(gradient_x, gradient_y, gradient_map)

            # Assign the corresponding ID to the ID map where the condition is true
            block_map[condition_mask] = condition["id"]

        print("Displaying...")
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')

        # Create the X and Y grid for plotting
        X, Y = np.meshgrid(np.arange(size), np.arange(size))

        # Plot the heightmap as a surface
        ax.plot_surface(X, Y, height_map, cmap='viridis', alpha=0.7)

        # Define color map for the block_map
        block_cmap = plt.get_cmap('jet')

        # Normalize the block_map values for better color representation
        norm = plt.Normalize(vmin=np.min(block_map), vmax=np.max(block_map))

        # Plot the block_map as a scatter plot on top of the heightmap
        ax.scatter(X, Y, height_map, c=block_map, cmap=block_cmap, s=40, alpha=0.005, edgecolor='k')

        # Set labels and title
        ax.set_title('Heightmap + Block Map')
        ax.set_xlabel('X')
        ax.set_ylabel('Z')
        ax.set_zlabel('Y')

        # Add a color bar for the block_map (ID colors)
        cbar = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=block_cmap), ax=ax, shrink=0.5, aspect=5)
        cbar.set_label('Block ID')

        plt.show()
        print("Converting...")

        todatapack.convert_terrain_to_datapack(
            height_map, block_map, water_level=60
        )

        print("Complete!")