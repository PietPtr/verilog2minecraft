import json
from pprint import pprint



class Cell:
    def __init__(self, name, celltype, input_ports, output_ports):
        self.name = name
        self.celltype = celltype
        self.input_ports = input_ports # [(string, net_id)]
        self.output_ports = output_ports
        self.outputs = []

        self.position = None
        self.gate_version = None
        self.rotation = None
        self.placed = False
    
    def set_outputs(self, outputs):
        self.outputs = outputs # [(cell, input port)]

    def place(self, position, gate_version, rotation):
        self.position = position
        self.gate_version = gate_version
        self.rotation = rotation
        self.placed = True
    
    def __repr__(self):
        if not self.placed:
            return f"Cell ({self.celltype} -> {[x[0].celltype for x in self.outputs]})"
        else:
            return f"Placed Cell ({self.celltype} at {self.position[0]},{self.position[1]},{self.position[2]} {self.rotation})"


def load_graph(filename):
    yosys = json.load(open(filename))

    if len(yosys['modules']) > 1:
        print("Your design is not flattened. Run `flatten' in Yosys when synthesizing your design.")
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
    output_cells = []
    for output in partial_cell.output_ports:
        (output_port, output_net_id) = output
        for cell in cells:
            for input in cell.input_ports:
                (port_name, input_net_id) = input
                if output_net_id == input_net_id:
                    output_cells.append((cell, port_name))

    partial_cell.set_outputs(output_cells)

