import time
import os

def convert_terrain_to_datapack(height_map, block_map, water_level=60, grass_density_percentage=100, output_dir="make"):
    block_names = [
        "grass_block",
        "grass_block",  # steeper grass
        "stone",
        "stone",  # steeper stone
    ]

    for x in range(height_map.shape[0]):
        percent_complete = x / height_map.shape[0]
        block_percent = round(percent_complete * 20)
        print(f"\rProcessing {round(percent_complete * 100, 1)}% |{'█' * block_percent}{' ' * (20 - block_percent)}|", end="")

        open(os.path.join(output_dir, f"chunk_{x}.mcfunction"), "w").close()  # remove any pre-existing data
        with open(os.path.join(output_dir, f"chunk_{x}.mcfunction"), "a") as file:
            for y in range(height_map.shape[1]):
                height = height_map[x][y]
                block = block_map[x][y]

                if block == 2:
                    possible_blocks = ["stone", "cobblestone"]
                    choice = (x + y) % len(possible_blocks)
                    block_name = possible_blocks[choice]
                else:
                    block_name = block_names[block]

                generated_line = f"setblock {x} {height} {y} {block_name}\n"

                if height < water_level:
                    generated_line += f"fill {x} {height} {y} {x} {water_level} {y} water\n"


                elif block == 0:
                    if (x + y) % 100 < grass_density_percentage:
                        generated_line += f"setblock {x} {height+1} {y} grass\n"

                file.write(generated_line)

    print(f"\rCleaning up...")

    open(os.path.join(output_dir, f"_make.mcfunction"), "w").close()  # clean out file

    with open(os.path.join(output_dir, f"_make.mcfunction"), "a") as f:
        f.write(f"fill 0 0 0 {height_map.shape[0]} 200 0 barrier\n")  # Create shell for fluids (and players)
        f.write(f"fill 0 0 0 0 200 {height_map.shape[1]} barrier\n")
        f.write(f"fill {height_map.shape[0]} 0 0 {height_map.shape[0]} 200 {height_map.shape[1]} barrier\n")
        f.write(f"fill 0 0 {height_map.shape[1]} {height_map.shape[0]} 200 {height_map.shape[1]} barrier\n")

        for x in range(height_map.shape[0]):
            f.write(f"schedule function {output_dir}:chunk_{x} {x+1}t\n")


