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
        cmp = components.get_model(model_name)
        rotated_blocks = dict()
        for (pos, block_id) in cmp.blocks.items():
            rotated_blocks[tup.rotate(pos, theta)] = block_id
        
        model = Model(rotated_blocks)
        with open(f'minecraft/data/components/{model_name + "_" + str(theta)}', 'wb') as f:
            pickle.dump(model, f)



if __name__ == "__main__":
    rotated_versions(sys.argv[1])

