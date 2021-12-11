import json
from pprint import pprint
import compiler.cell_defs as cell_defs

import numpy as np

class Cell:
    def __init__(self, name, celltype, input_ports, output_ports):
        self.name = name
        self.celltype = celltype
        self.input_ports = input_ports # [(string, net_id)]
        self.output_ports = output_ports
        self.outputs = {}
        self.inputs = {}

        self.position = None
        self.gate_version = None
        self.placed = False
        self.freeze_placement = False
    
    def set_outputs(self, outputs):
        self.outputs = outputs # {output_port: (cell, input port)}

    def set_inputs(self, inputs):
        self.inputs = inputs

    def place(self, position, gate_version):
        if not self.freeze_placement:
            self.position = position
            self.gate_version = gate_version
            self.placed = True

    def freeze(self):
        self.freeze_placement = True

    def collides(self, position, size):
        if self.gate_version is None or self.position is None:
            return False

        SPACER = np.array([2, 2, 2])

        a_pos = self.position - SPACER
        a_size = self.gate_version.size + SPACER * 2

        b_pos = position - SPACER
        b_size = size + SPACER * 2
        
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
            return f"Placed Cell ({self.celltype} at {self.position[0]},{self.position[1]},{self.position[2]} impl {self.gate_version.implementation_file})"

def read_constraints(filename):
    def parse_constraint(line):
        port_name = line.split(":")[0]
        coords = list(map(int, line.split(":")[1].split(",")))
        return (
            port_name,
            np.array([coords[0], coords[1], coords[2]])
        )

    io_constraints = {}
    
    with open(filename, 'r') as file:
        for line in file.readlines():
            (port_name, coords) = parse_constraint(line)
            io_constraints[port_name] = coords

    return io_constraints


def load_graph(yosys_json, constraint_file, components):
    yosys = json.load(open(yosys_json))

    if len(yosys['modules']) > 1:
        print("_your design is not flattened. Run `flatten' in _yosys when synthesizing your design.")
        exit()
        
    top = list(yosys['modules'].items())[0][1]
    cell_defs.build(components.models, top)
    constraints = read_constraints(constraint_file)

    graph = []

    add_outputs_to_graph(graph, constraints, top['ports'])

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
        find_inputs(partial_cell, graph)

    add_inputs_to_graph(graph, constraints, top['ports'])

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

def add_outputs_to_graph(graph, constraints, port_json):
    for (port_name, data) in port_json.items():
        if data['direction'] == 'output':
            net_id = data['bits'][0] # Assume 1-bit I/O

            o_cell = Cell(port_name + '_output', 'OUTPUT', [('DRIVEN', net_id)], [])
            o_cell.place(constraints[port_name], cell_defs.minecraft_cell_lib['OUTPUT'][0])
            o_cell.freeze()
            graph.append(o_cell)
    
    return graph


def add_inputs_to_graph(graph, constraints, port_json):
    for (port_name, data) in port_json.items():
        if data['direction'] == 'input':
            net_id = data['bits'][0] # Assume 1-bit I/O
            # i_cell = Cell(port_name + '_input', '$_NOT_', [], [('A', 7778), ('Y', net_id)])
            # i_cell.place(constraints[port_name], cell_defs.minecraft_cell_lib['$_NOT_'][0])


            i_cell = Cell(port_name + '_input', 'INPUT', [], [('DRIVES', net_id)])
            i_cell.place(constraints[port_name], cell_defs.minecraft_cell_lib['INPUT'][0])
            i_cell.freeze()
            find_outputs(i_cell, graph)
            graph.append(i_cell)
    
    return graph