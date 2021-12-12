import numpy as np
import random
from pprint import pprint
from enum import Enum
from typing import Tuple, List, Dict
from compiler.graph import collides_with_any, collides_with_any_except, Cell
import util.coord as tup
import math
from compiler.cell_defs import *
import csv
from compiler.daanpnr import place_and_route



def place_random(graph, seed):
    x_size = int(len(graph) * 0.2)
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
            sum += tup.dist(start, end) ** 2

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

def placed_to_netmap(placed: List[Cell]) -> Dict[Tuple[int, int, int], List[Tuple[int, int, int]]]:
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


def placed_cell_bb(placed: List[Cell]):
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

# jahaaa dit moet eigenlijk een class zijn 
def place_sa(graph):
    T_0 = 100
    k_max = 1000
    a = 0.00005
    OFFSET_RANGE = np.array([5, 5, 5])
    def temperature(k):
        nonlocal a
        return T_0 / (1 + a * k*k)

    def random_other_cell(gv, graph):
        r = random.randint(0, len(graph))
        i = 0

        while r >= 0:
            cell = graph[i % len(graph)]
            if cell.gate_version.implementation_file == gv.implementation_file:
                r -= 1
                if r <= 0:
                    return cell
            i += 1
        raise Exception("Should not have reached this point haha")


    def apply_offsets(graph, offsets):
        i = 0
        for cell in graph:
            offset = offsets[i]
            position = cell.position + offset
            size = minecraft_cell_lib[cell.celltype][0].size

            collides = collides_with_any_except(position, size, graph, i)
            
            if not collides:
                cell.place(position, minecraft_cell_lib[cell.celltype][0])
            else:
                if not cell.is_io:
                    pass
                    # This is the logic to perform a cell swap for two equal implemenation cells
                    # other_cell = random_other_cell(cell.gate_version, graph)
                    # (other_cell.position, cell.position) = (cell.position, other_cell.position)
                    
                    

            i += 1

    def generate_offsets(seed):
        nonlocal OFFSET_RANGE
        np.random.seed(seed)
        offsets = [((np.random.rand(3) - 0.5) * OFFSET_RANGE).astype(int)
            for _ in range(len(graph))
        ]
        return offsets

    def save_positions(graph):
        nonlocal best_positions
        best_positions = []
        for cell in graph:
            best_positions.append((cell.position[0], cell.position[1], cell.position[2]))


    best_score = float("inf")
    best_positions = [] # same order and size as graph, positions per cell...


    def apply_neighbor_transform(graph, k, temp, seed0):
        nonlocal best_score
        nonlocal writer
        seed = k * seed0 & 0xffffffff

        old_score = manhattan_distance(graph)
        offsets = generate_offsets(seed)
        apply_offsets(graph, offsets)

        new_score = manhattan_distance(graph)

        writer.writerow([k, (temp / T_0) * 100, (old_score / start_score) * 100])

        if new_score > old_score: # if new is _worse_ than old, accept it by chance.
            delta = new_score - old_score
            r = random.random()
            value = - delta / (k * temp)
            p_accept = 1 - math.exp(value)
            # print(f"P_accept new anyway: {p_accept}, given delta = {delta}")
            if (r < p_accept):
                # print(f"Kept s' by chance. {r} {p_accept}")
                pass # keep new graph
            else:
                apply_offsets(graph, list(map(lambda x: -x, offsets)))
        else: # if new is _better_ than old, always accept it.
            pass


        score = min(new_score, old_score)
        if score < best_score:
            best_score = score
            save_positions(graph)

    f = open('sa_log.csv', 'w')
    writer = csv.writer(f)
    writer.writerow(["k", "temp", "old_score"])

    seed = random.randint(0,987432987432)

    # generate 100 random placements and take the best
    # initial = random_search(graph, iterations=100)
    initial = place_and_route(graph)

    start_score = manhattan_distance(initial)
    print(f"Starting with start score: {start_score}")

    
    for k in range(1, k_max + 1):
        temp = temperature(k)

        apply_neighbor_transform(initial, k, temp, seed)

        if k % (k_max // 10) == 0 or k == 1:
            print(f"{k}: temp = {round(temp*100)/100}, best = {best_score}")

    i = 0
    for pos in best_positions:
        graph[i].place(
            np.array([pos[0], pos[1], pos[2]]), 
            minecraft_cell_lib[graph[i].celltype][0])
        i += 1


    print(f"Final score: {manhattan_distance(graph)}")
    f.close()

    exit()

    return graph
