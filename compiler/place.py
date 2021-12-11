import numpy as np
import random
from pprint import pprint
from enum import Enum

class Rotation(Enum):
    NORTH = 0
    EAST = 90
    SOUTH = 180
    WEST = 270

class GateVersion:
    def __init__(self, celltype, size, input_positions, output_positions):
        self.celltype = celltype
        self.size = size
        self.input_positions = input_positions
        self.output_positions = output_positions
        # self.implementation = ?implementation? # iets van een design file name of zo?
    
    def __repr__(self) -> str:
        return f"GateVersion {self.celltype} {self.size[0]}x{self.size[1]}x{self.size[2]}"

# every size, position, etc is x y z
minecraft_cell_lib = {
    # TODO: beetje dubbele administratie zo, wsch is de celltype property dan niet nodig
    "$_NOT_": [
        GateVersion("$_NOT_", 
            np.array([1, 3, 6]),
            {"A": np.array([0, 1, 0])}, # pos + input_pos  = feed repeater in this block to drive input
            {"Y": np.array([0, 1, 5])}) # pos + output_pos = block next to which a repeater can be placed
        ], 
    "$_OR_": [
        GateVersion("$_OR_",
            np.array([5, 3, 3]),
            {"A": np.array([4, 2, 2]),
             "B": np.array([0, 2, 2])},
            {"Y": np.array([2, 2, 0])})
    ],
    "$_DFFE_PP0N_": [
        GateVersion("$_DFFE_PP0N_",
            np.array([7, 4, 13]),
            {"C": np.array([4, 1, 0]),
             "R": np.array([6, 1, 10]),
             "E": np.array([2, 1, 0]),
             "D": np.array([0, 1, 0])},
            {"Q": np.array([2, 1, 12])})
    ]
}

def collides_with_any(position, size, placed_cells):
    for placed in placed_cells:
        if placed.collides(position, size):
            return True
    return False


def place_random(graph, seed):
    x_size = int(len(graph) * 3.0)
    y_size = x_size

    np.random.seed(seed)

    placed_cells = []

    def random_pos():
        location = (np.random.rand(3) * (x_size - 4)).astype(int)
        location[1] = 2
        return location

    max_collision_tries = 0

    for cell in graph:
        collides = True
        collision_tries = 0
        while collides:
            position = random_pos()
            gv = minecraft_cell_lib[cell.celltype][0]

            collides = collides_with_any(position, gv.size, placed_cells)
            if collides:
                collision_tries += 1

        max_collision_tries = max(max_collision_tries, collision_tries)

        cell.place(position, gv, Rotation.NORTH)
        placed_cells.append(cell)

    # print(f"Placed randomly, result distance score: {manhattan_distance(graph)}, {max_collision_tries} collision tries.")

    return (graph, max_collision_tries)

def manhattan_distance(graph):
    sum = 0
    for cell in graph:
        for (dest, port_name) in cell.outputs:
            # TODO: hier moet je naar output _port_ locations
            dist = np.abs(dest.position - cell.position).sum() ** 2
            sum += dist

    return sum

def random_search(graph):
    best_distance = float("inf")
    best_placed_seed = 0
    total_dist = 0
    total_tries = 0

    seed1 = random.randint(0, 2**32 - 1)
    iterations = 1000

    for i in range(iterations):
        seed = (i * seed1) & 0xffffffff
        (placed, collision_tries) = place_random(graph, seed)
        dist = manhattan_distance(placed)
        total_dist += dist
        total_tries += collision_tries
        if dist < best_distance:
            best_distance = dist
            best_placed_seed = seed
        
        if collision_tries > 50:
            print(f"High amount of collisions ({collision_tries}) in placer, provide more space.")
        
        if i % 100 == 0:
            print(f"Random placer iteration {i}...")

    print(f"Placed {iterations} iterations randomly:")
    print(f"\tAverage distance: {total_dist // iterations}")
    print(f"\tAverage collision tries: {total_tries / iterations}")
    print(f"\tBest distance: {best_distance}")
    
    (result, tries) = place_random(graph, best_placed_seed)
    return result
