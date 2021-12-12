import numpy as np
import random
from pprint import pprint
from enum import Enum
from typing import Tuple, List, Dict
import compiler.graph as graph
import util.coord as tup
import math
from compiler.cell_defs import *




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
        # location[1] = 5
        return location

    max_collision_tries = 0

    for cell in graph:
        collides = True
        collision_tries = 0
        while collides:
            position = random_pos()
            gv = minecraft_cell_lib[cell.celltype][0]
            if cell.celltype == "$_NOT_":
                # gv = random.choice(minecraft_cell_lib[cell.celltype]) # 152 @ 193_000 / 200_000 (*3, combi)
                gv = minecraft_cell_lib[cell.celltype][0] # 168 @ 97000 / 200_000

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

def random_search(graph, iterations=100):
    best_distance = float("inf")
    best_placed_seed = 0
    total_dist = 0
    total_tries = 0

    seed1 = random.randint(0, 2**32 - 1)

    for i in range(iterations):
        seed = (i * seed1) & 0xffffffff
        (placed, collision_tries) = place_random(graph, seed)
        dist = manhattan_distance(placed)
        total_dist += dist
        total_tries += collision_tries
        if dist < best_distance:
            best_distance = dist
            best_placed_seed = seed
        
        if collision_tries > 120:
            print(f"High amount of collisions ({collision_tries}) in placer, provide more space.")
        
        if i % 100 == 0:
            print(f"Random placer iteration {i}, best so far: {best_distance}...")

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


def place_sa(graph):
    def temperature(k):
        T_0 = 100
        a = 0.2
        return T_0 / (1 + a * k)

    def apply_offsets(graph, offsets):
        i = 0
        for cell in graph:
            offset = offsets[i]
            position = cell.position + offset
            size = minecraft_cell_lib[cell.celltype][0].size

            # TODO: dit werkt niet want position zit al in de graph sukkol
            collides = collides_with_any(position, size, graph)
            
            if not collides:
                cell.place(position, minecraft_cell_lib[cell.celltype][0])
                print("wat")


            i += 1

    def generate_offsets(seed):
        np.random.seed(seed)
        OFFSET_RANGE = np.array([5, 5, 5])
        offsets = [((np.random.rand(3) - 0.5) * OFFSET_RANGE).astype(int)
            for _ in range(len(graph))
        ]
        return offsets

    def save_positions(graph):
        nonlocal best_positions
        best_positions = []
        for cell in graph:
            best_positions.append(cell.position)


    best_score = float("inf")
    best_positions = [] # same order and size as graph, positions per cell...
    

    def apply_neighbor_transform(graph, k, temp, seed0):
        nonlocal best_score
        seed = k * seed0 & 0xffffffff

        old_score = manhattan_distance(graph)
        offsets = generate_offsets(seed)
        apply_offsets(graph, offsets)
        
        new_score = manhattan_distance(graph)

        if new_score > old_score: # if new is _worse_ than old, accept it by chance.
            delta = new_score - old_score
            r = random.random()
            value = - delta / (k * temp)
            print(value)
            if (r < math.exp(value)):
                pass
            else:
                apply_offsets(graph, list(map(lambda x: -x, offsets)))
        else:
            # keep old graph
            apply_offsets(graph, list(map(lambda x: -x, offsets)))

        score = min(new_score, old_score)
        if score < best_score:
            best_score = score
            save_positions(graph)

            print(f"New best score found: {best_score}")

        

    # generate 100 random placements and take the best
    initial = random_search(graph, 100)

    
    k_max = 100
    seed = random.randint(0,987432987432)
    for k in range(0, k_max + 1):
        temp = temperature(k)

        apply_neighbor_transform(initial, k, temp, seed)

        if k % 10 == 0:
            print(f"{k}: temp = {round(temp*100)/100}")
        
    i = 0
    for pos in best_positions:
        graph[i].position = pos
        i += 1

    print(manhattan_distance(graph))
        

    return graph