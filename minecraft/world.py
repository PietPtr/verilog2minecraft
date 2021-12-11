from typing import Dict, Tuple
import amulet
import os

from amulet import Block

from util.coord import tupleAdd

mc_version = ("java", (1, 17, 1))

class Model:
    blocks: Dict[Tuple[int, int, int], Block]

    def __init__(self, blocks: Dict[Tuple[int, int, int], Block]):
        self.blocks = blocks


class World:
    blocks: Dict[Tuple[int, int, int], Block]

    def __init__(self):
        self.minecraft = None
        self.blocks = dict()

    def set_block(self, position: Tuple[int, int, int], block: Block):
        self.blocks[position] = block

    def add_model(self, position: Tuple[int, int, int], model: Model):
        for coords, block in model.blocks.items():
            self.set_block(tupleAdd(position, coords), block)

    def read_model(self, path: str, position: Tuple[int, int, int], size: Tuple[int, int, int]) -> Model:
        minecraft = amulet.load_level(path)
        blocks: Dict[Tuple[int, int, int], Block] = dict()
        for x in range(0, size[0]):
            for y in range(0, size[1]):
                for z in range(0, size[2]):
                    pos = tupleAdd(position, (x, y, z))
                    block = minecraft.get_version_block(pos[0], pos[1], pos[2], "minecraft:overworld", mc_version)
                    if isinstance(block[0], Block) and block[0].base_name != 'air':
                        blocks[(x, y, z)] = block[0]
        minecraft.close()
        return Model(blocks)

    def build(self, path: str):
        os.system(f"rm -r {path} && cp -r minecraft/data/flat {path}")
        minecraft = amulet.load_level(path)
        for coords, block in self.blocks.items():
            minecraft.set_version_block(coords[0], coords[1], coords[2], "minecraft:overworld", mc_version, block)
        minecraft.save()
        minecraft.close()
