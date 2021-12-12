import os, sys
import pickle
from pprint import pprint
from minecraft.components import ComponentManager
from minecraft.world import Model

import util.coord as tup

components = ComponentManager()

def rotated_versions(model_name):
    angles = [0, 90, 180, 270]
    for theta in angles:
        model = components.get_model(model_name)
        rotated_blocks = dict()
        for (pos, block_id) in model.blocks.items():
            new_pos = tup.tupleAdd(tup.rotate(pos, theta), (2, 2, 2))
            rotated_blocks[new_pos] = block_id
            print(pos, new_pos, block_id)
        
        model_new = Model(rotated_blocks, model.bounding_box, model.ports, model.size, model.yosys_name, model.name)
        with open(f'minecraft/data/components/{model_new.name + "_" + str(theta)}', 'wb') as f:
            pickle.dump(model_new, f)



if __name__ == "__main__":
    rotated_versions(sys.argv[1])

