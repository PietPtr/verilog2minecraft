import numpy as np
import minecraft.world
from typing import Tuple, List, Dict
from util.wool import *

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
        if model_name != "$_NOT_":
            continue
        
        input_positions = []
        output_positions = []
        print(model_name, model.yosys_name)

        for (wool, location) in model.ports.items():
            # print(wool, location)
            port_name = wool_map[model.yosys_name][wool]
            

        gv = GateVersion(
            model.yosys_name,
            model.size,
            input_positions,
            output_positions,
            model_name
        )

wool_map = {
    "$_NOT_": {
        WoolType.WHITE_WOOL: "A",
        WoolType.GREEN_WOOL: "Y"
    },
    "$_OR_": {
        WoolType.WHITE_WOOL: "A",
        WoolType.BLACK_WOOL: "B",
        WoolType.GREEN_WOOL: "Y"
    },
    "$_DFFE_PP0N_": {
        WoolType.ORANGE_WOOL: "R",
        WoolType.MAGENTA_WOOL: "Q",
        WoolType.LIGHT_BLUE_WOOL: "D",
        WoolType.YELLOW_WOOL: "C",
        WoolType.LIME_WOOL: "E"
    },
    "INPUT": {

    }
}

minecraft_cell_lib = {

}

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