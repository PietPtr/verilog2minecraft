import numpy as np
import random
from pprint import pprint
from enum import Enum
from typing import Tuple, List, Dict
import compiler.graph as graph
import util.coord as tup
import math


class GateVersion:
    def __init__(self, celltype, size, input_positions, output_positions, implementation_file):
        self.celltype = celltype
        self.size = size
        self.input_positions = input_positions
        self.output_positions = output_positions
        self.implementation_file = implementation_file # file name of the implemented gate
    
    def __repr__(self) -> str:
        return f"GateVersion {self.celltype} {self.size[0]}x{self.size[1]}x{self.size[2]}"

# every size, position, etc is x y z
minecraft_cell_lib = {
    # TODO: beetje dubbele administratie zo, wsch is de celltype property dan niet nodig
    "$_NOT_": [
        GateVersion("$_NOT_", 
            np.array([1, 3, 6]),
            {"A": np.array([0, 1, 0])}, # pos + input_pos  = feed repeater in this block to drive input
            {"Y": np.array([0, 1, 5])}, # pos + output_pos = block next to which a repeater can be placed
            "$_NOT_")
        ],
    "$_OR_": [
        GateVersion("$_OR_",
            np.array([5, 3, 3]),
            {"A": np.array([4, 1, 2]),
             "B": np.array([0, 1, 2])},
            {"Y": np.array([2, 1, 0])},
            "$_OR_")
    ],
    "$_DFFE_PP0N_": [
        GateVersion("$_DFFE_PP0N_",
            np.array([7, 4, 13]),
            {"C": np.array([4, 1, 0]),
             "R": np.array([6, 1, 10]),
             "E": np.array([2, 1, 0]),
             "D": np.array([0, 1, 0])},
            {"Q": np.array([2, 1, 12])},
            "$_DFFE_PP0N_")
    ]
}

def generate_4_rotation_versions(gv : GateVersion) -> List[GateVersion]:
    def rotate(v, angle):
        return tup.to_np(rotate(tup.to_tup(v), angle))

    versions = []
    for angle in range(0, 360, 90):
        # new_gv = GateVersion(
        #         gv.name + "_" + str(angle),
        #         rotate(gv.size, angle),
        #         {p: rotate(p, )}
                
        #     )
        pass

def collides_with_any(position, size, placed_cells):
    for placed in placed_cells:
        if placed.collides(position, size):
            return True
    return False


def place_random(graph, seed):
    x_size = int(len(graph) * 10.0)
    y_size = x_size

    np.random.seed(seed)

    placed_cells = []

    def random_pos():
        location = (np.random.rand(3) * (x_size - 4)).astype(int)
        location[1] = 4
        return location

    max_collision_tries = 0

    for cell in graph:
        collides = True
        collision_tries = 0
        while collides:
            position = random_pos()
            gv = random.choice(minecraft_cell_lib[cell.celltype])

            collides = collides_with_any(position, gv.size, placed_cells)
            if collides:
                collision_tries += 1

        max_collision_tries = max(max_collision_tries, collision_tries)

        cell.place(position, gv)
        placed_cells.append(cell)

    return (graph, max_collision_tries)

def manhattan_distance(graph):
    sum = 0

    netmap = placed_to_netmap(graph)

    for (start, ends) in netmap.items():
        for end in ends:
            sum += tup.dist(start, end)

    return sum

def random_search(graph):
    best_distance = float("inf")
    best_placed_seed = 0
    total_dist = 0
    total_tries = 0

    seed1 = random.randint(0, 2**32 - 1)
    iterations = 100

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

def placed_to_netmap(placed: List[graph.Cell]) -> Dict[Tuple[int, int, int], List[Tuple[int, int, int]]]:
    def arr_to_tuple(arr):
        return (arr[0], arr[1], arr[2])

    netmap = dict()
    for from_cell in placed:
        for (from_port_name, to_cells) in from_cell.outputs.items():
            out_pos = from_cell.position + from_cell.gate_version.output_positions[from_port_name]
            in_positions = []
            for (to_cell, to_port_name) in to_cells:
                in_positions.append(
                    to_cell.position + to_cell.gate_version.input_positions[to_port_name])
            
            netmap[arr_to_tuple(out_pos)] = list(map(arr_to_tuple, in_positions))

    return netmap


def placed_cell_bb(placed: List[graph.Cell]):
    bounding_box = set()
    for cell in placed:
        tl = cell.position
        br = cell.position + cell.gate_version.size
        allowed = [tuple(x) for x in cell.gate_version.output_positions.values()] + [tuple(x) for x in cell.gate_version.input_positions.values()]
        for x in range(tl[0], br[0]):
            for y in range(tl[1], br[1]):
                for z in range(tl[2], br[2]):
                    if (x, y, z) in allowed:
                        continue
                    bounding_box.add((x, y, z))
    
    return bounding_box
