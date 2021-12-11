import random

import numpy as np

from compiler.place import minecraft_cell_lib, collides_with_any


def place_and_route(unplaced):

    to_place = [(None, unplaced[0])]
    placed_cells = []

    while len(to_place) > 0:
        placer, cell = to_place[0]
        if cell in placed_cells:
            to_place.pop(0)
            continue
        gv = minecraft_cell_lib[cell.celltype][0]
        if placer is None:
            cell.place(np.array([0, 5, 0]), gv)
        else:
            new_position = np.array(placer.position)
            new_position[0] += placer.gate_version.size[0] + 1
            while collides_with_any(new_position, gv.size, placed_cells):
                # print("position collides:", new_position)
                new_position[0] += random.randint(-2, 2)
                new_position[1] = max(5, new_position[1] + random.randint(-2, 2))
                new_position[2] += random.randint(-2, 2)
            cell.place(new_position, gv)

        for inputs in cell.inputs.values():
            for input, _ in inputs:
                if input not in placed_cells and input not in to_place:
                    to_place.append((cell, input))

        for outputs in cell.outputs.values():
            for output, _ in outputs:
                if output not in placed_cells and output not in to_place:
                    to_place.append((cell, output))
        placed_cells.append(cell)
        to_place.pop(0)
        print("placed: ", cell, "total: ", len(placed_cells), "out of", len(unplaced))

    print("Finished")
    return unplaced


