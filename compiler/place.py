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
            np.array([1, 3, 2]), 
            {"A": np.array([0, 0, 0])}, # pos + input_pos  = feed repeater in this block to drive input
            {"Y": np.array([0, 1, 0])}) # pos + output_pos = block next to which a repeater can be placed
        ], 
    "$_OR_": [
        GateVersion("$_OR_",
            np.array([3, 3, 2]),
            {"A": np.array([0, 0, 0]),
             "B": np.array([2, 0, 0])},
            {"Y": np.array([1, 1, 0])})
    ],
    "$_DFFE_PP0N_": [
        GateVersion("$_DFFE_PP0N_",
            np.array([11, 3, 7]),
            {"C": np.array([0, 0, 0]),
             "R": np.array([2, 0, 0]),
             "E": np.array([3, 1, 0]),
             "D": np.array([1, 3, 0])},
            {"Q": np.array([2, 3, 0])})
    ]
}

def collides_with_any(position, size, placed_cells):
    for placed in placed_cells:
        if placed.collides(position, size):
            return True
    return False


def place_random(graph, seed):
    x_size = int(len(graph) * 0.55)
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

    print(f"Placed randomly, result distance score: {manhattan_distance(graph)}, {max_collision_tries} collision tries.")

    return graph

def manhattan_distance(graph):
    sum = 0
    for cell in graph:
        for (dest, port_name) in cell.outputs:
            dist = np.abs(dest.position - cell.position).sum() ** 2
            sum += dist

    return sum

def random_search(graph):
    best_distance = float("inf")
    best_placed_seed = 0

    seed1 = random.randint(0, 2**32 - 1)

    for i in range(1000):
        seed = (i * seed1) & 0xffffffff
        placed = place_random(graph, seed)
        dist = manhattan_distance(placed)
        if dist < best_distance:
            best_distance = dist
            best_placed_seed = seed
    
    return place_random(graph, best_placed_seed)
