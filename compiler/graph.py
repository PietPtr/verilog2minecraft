import json
from pprint import pprint

import numpy as np

class Cell:
    def __init__(self, name, celltype, input_ports, output_ports):
        self.name = name
        self.celltype = celltype
        self.input_ports = input_ports # [(string, net_id)]
        self.output_ports = output_ports
        self.outputs = []
        self.inputs = []

        self.position = None
        self.gate_version = None
        self.rotation = None
        self.placed = False
    
    def set_outputs(self, outputs):
        self.outputs = outputs # {output_port: (cell, input port)}

    def set_inputs(self, inputs):
        self.inputs = inputs

    def place(self, position, gate_version, rotation):
        self.position = position
        self.gate_version = gate_version
        self.rotation = rotation
        self.placed = True

    def collides(self, position, size):
        if self.gate_version is None or self.position is None:
            return False

        SPACER = np.array([2, 2, 1])

        a_pos = self.position - SPACER
        a_size = self.gate_version.size + SPACER

        b_pos = position - SPACER
        b_size = size + SPACER
        
        a_tl = a_pos
        a_br = a_pos + a_size
        b_tl = b_pos
        b_br = b_pos + b_size

        a_max_x = max(a_tl[0], a_br[0])
        a_min_x = min(a_tl[0], a_br[0])
        a_max_y = max(a_tl[1], a_br[1])
        a_min_y = min(a_tl[1], a_br[1])
        a_max_z = max(a_tl[2], a_br[2])
        a_min_z = min(a_tl[2], a_br[2])

        b_max_x = max(b_tl[0], b_br[0])
        b_min_x = min(b_tl[0], b_br[0])
        b_max_y = max(b_tl[1], b_br[1])
        b_min_y = min(b_tl[1], b_br[1])
        b_max_z = max(b_tl[2], b_br[2])
        b_min_z = min(b_tl[2], b_br[2])

        return (
            (a_min_x <= b_max_x and a_max_x >= b_min_x) and
            (a_min_y <= b_max_y and a_max_y >= b_min_y) and
            (a_min_z <= b_max_z and a_max_z >= b_min_z))


        
    
    def __repr__(self):
        if not self.placed:
            return f"Cell ({self.celltype} -> {[x[0].celltype for x in self.outputs]})"
        else:
            return f"Placed Cell ({self.celltype} at {self.position[0]},{self.position[1]},{self.position[2]} {self.rotation})"


def load_graph(filename):
    yosys = json.load(open(filename))

    if len(yosys['modules']) > 1:
        print("_your design is not flattened. Run `flatten' in _yosys when synthesizing your design.")
        exit()

    top = list(yosys['modules'].items())[0][1]

    graph = []

    for (cell, cellinfo) in top['cells'].items():
        inputs = []
        outputs = []
        for (port_name, port_dir) in cellinfo['port_directions'].items():
            if port_dir == "input":
                # assumes every output port is 1 bit wide.
                inputs.append((port_name, cellinfo['connections'][port_name][0]))
            elif port_dir == "output":
                outputs.append((port_name, cellinfo['connections'][port_name][0]))

        cell_obj = Cell(cell, cellinfo['type'], inputs, outputs)
        graph.append(cell_obj)
    
    for (partial_cell) in graph:
        find_outputs(partial_cell, graph)

    return graph


def find_outputs(partial_cell, cells):
    output_cells = {}
    for output in partial_cell.output_ports:
        (output_port, output_net_id) = output
        for cell in cells:
            for input in cell.input_ports:
                (port_name, input_net_id) = input
                if output_net_id == input_net_id:
                    if output_port in output_cells:
                        output_cells[output_port].append((cell, port_name))
                    else:
                        output_cells[output_port] = [(cell, port_name)]

    partial_cell.set_outputs(output_cells)


def find_inputs(partial_cell, cells):
    input_cells = {}
    for input in partial_cell.input_ports:
        (input_port, input_net_id) = input
        for cell in cells:
            for output in cell.output_ports:
                (port_name, output_net_id) = output
                if output_net_id == input_net_id:
                    if input_port in input_cells:
                        input_cells[input_port].append((cell, port_name))
                    else:
                        input_cells[input_port] = [(cell, port_name)]
    partial_cell.set_inputs(input_cells)
