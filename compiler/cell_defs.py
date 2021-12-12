import numpy as np
import minecraft.world
from typing import Tuple, List, Dict
from util.wool import *
import util.coord as tup
from pprint import pprint

class GateVersion:
    input_positions: Dict[str, Tuple[int, int, int]]

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
    DO_ROTATE_FOR = ["$_NOT_"]

    for (model_name, model) in models.items():
        if not (model_name in ["$_NOT_", "$_OR_", "$_DFFE_PP0N_", "INPUT", "OUTPUT"]):
            continue
        
        input_positions = dict()
        output_positions = dict()
        
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

        if not (model.yosys_name in minecraft_cell_lib):
            minecraft_cell_lib[model.yosys_name] = []

        def rotate(v, angle):
            return tup.to_np(tup.rotate(tup.to_tup(v), angle))

        if model_name in DO_ROTATE_FOR:
            minecraft_cell_lib[model.yosys_name].append(gv)
            print(f"creating rotation gv's for {model_name}")
            for angle in range(0, 360, 90):
                new_gv = GateVersion(
                    gv.celltype + "_" + str(angle),
                    rotate(gv.size, angle),
                    {p: rotate(input_positions[p], angle) for p in input_positions},
                    {p: rotate(output_positions[p], angle) for p in output_positions},
                    gv.implementation_file + "_" + str(angle)
                )
                minecraft_cell_lib[model.yosys_name].append(new_gv)
        else:
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
        WoolType.GREEN_WOOL: {
            "name": "DRIVES",
            "direction": "output"
        }
    },
    "OUTPUT": {
        WoolType.WHITE_WOOL: {
            "name": "DRIVEN",
            "direction": "input"
        }
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