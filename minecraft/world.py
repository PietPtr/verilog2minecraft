from typing import Dict, Tuple
import numpy as np
import amulet
import os
from enum import Enum

mc_version = ("java", (1, 17, 1))


def tupleAdd(a: Tuple[int, int, int], b: Tuple[int, int, int]) -> Tuple[int, int, int]:
    return tuple((x + y for x, y in zip(a, b)))


class Block(Enum):
    STONE = "stone"
    REDSTONE = "redstone_wire"
    TORCH = "redstone_torch"


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
            self.set_block(tupleAdd(position, coords), amulet.Block("minecraft", block.value))

    def build(self, path: str):
        os.system(f"cp -r data/flat {path}")
        self.minecraft = amulet.load_level(path)
        for coords, block in self.blocks.items():
            print(f"Adding block: {coords} {block}")
            self.minecraft.set_version_block(coords[0], coords[1], coords[2], "minecraft:overworld", mc_version, block)
        self.minecraft.save()
        self.minecraft.close()
