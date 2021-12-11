import numpy as np
import minecraft.world
from typing import Tuple, List, Dict
from util.wool import *
import util.coord as tup
from pprint import pprint

class GateVersion:
    def __init__(self, celltype, size, input_positions, output_positions, implementation_file):
        self.celltype = celltype
        self.size = size
        self.input_positions = input_positions
        self.output_positions = output_positions
        self.implementation_file = implementation_file # file name of the implemented gate
    
    def __repr__(self) -> str:
        return f"GateVersion {self.celltype} {self.size[0]}x{self.size[1]}x{self.size[2]}"

def build(models : Dict[str, minecraft.world.Model], cell_json) -> Dict[str, List[GateVersion]]:
    global minecraft_cell_lib

    for (model_name, model) in models.items():
        if not (model_name in ["$_NOT_", "$_OR_", "$_DFFE_PP0N_"]):
            continue
        
        input_positions = dict()
        output_positions = dict()
        print(model_name)

        for (wool, location) in model.ports.items():
            # print(wool, location)
            port_data = wool_map[model.yosys_name][wool]
            if port_data['direction'] == 'input':
                input_positions[port_data["name"]] = tup.to_np(location)
            elif port_data['direction'] == 'output':
                output_positions[port_data["name"]] = tup.to_np(location)        

        gv = GateVersion(
            model.yosys_name,
            model.size,
            input_positions,
            output_positions,
            model_name
        )

        pprint(input_positions)
        pprint(output_positions)

        if not (model.yosys_name in minecraft_cell_lib):
            minecraft_cell_lib[model.yosys_name] = []
        
        minecraft_cell_lib[model.yosys_name].append(gv)


wool_map = {
    "$_NOT_": {
        WoolType.WHITE_WOOL: {
            "name": "A",
            "direction": "input" 
        },
        WoolType.GREEN_WOOL: {
            "name": "Y",
            "direction": "output"
        }
    },
    "$_OR_": {
        WoolType.WHITE_WOOL: {
            "name": "A",
            "direction": "input" 
        },
        WoolType.BLACK_WOOL: {
            "name": "B",
            "direction": "input" 
        },
        WoolType.GREEN_WOOL: {
            "name": "Y",
            "direction": "output" 
        }
    },
    "$_DFFE_PP0N_": {
        WoolType.ORANGE_WOOL: {
            "name": "R",
            "direction": "input" 
        },
        WoolType.MAGENTA_WOOL: {
            "name": "Q",
            "direction": "output" 
        },
        WoolType.LIGHT_BLUE_WOOL: {
            "name": "D",
            "direction": "input" 
        },
        WoolType.YELLOW_WOOL: {
            "name": "C",
            "direction": "input" 
        },
        WoolType.LIME_WOOL: {
            "name": "E",
            "direction": "input" 
        },
    },
    "INPUT": {

    }
}

minecraft_cell_lib = dict()

# every size, position, etc is x y z
minecraft_cell_lib_old = {
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
    ],
    "INPUT": [None],
    "OUTPUT": [None]
}