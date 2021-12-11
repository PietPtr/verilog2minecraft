from typing import Dict, Tuple, Set
import amulet
import os

from amulet import Block

from util.coord import tupleAdd, tupleSub
from util.wool import WoolType

mc_version = ("java", (1, 17, 1))

class Model:
    blocks: Dict[Tuple[int, int, int], Block]
    bounding_box: Set[Tuple[int, int, int]]
    size: Tuple[int, int, int]
    ports: Dict[WoolType, Tuple[int, int, int]]

    def __init__(self, blocks: Dict[Tuple[int, int, int], Block], bounding_box: Set[Tuple[int, int, int]],
                 ports: Dict[WoolType, Tuple[int, int, int]], size: Tuple[int, int, int]):
        self.blocks = blocks
        self.bounding_box = bounding_box
        self.ports = ports
        self.size = size

    def fill_area(self, size: Tuple[int, int, int]):
        for pos in self.bounding_box:
            self.blocks[pos] = Block("minecraft", "glass")

    


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
        bounding_box: Set[Tuple[int, int, int]] = set()
        ports: Dict[WoolType, Tuple[int, int, int]] = dict()
        for x in range(0, size[0]):
            for y in range(0, size[1]):
                for z in range(0, size[2]):
                    pos = tupleAdd(position, (x, y, z))
                    block = minecraft.get_version_block(pos[0], pos[1], pos[2], "minecraft:overworld", mc_version)
                    if isinstance(block[0], Block) and block[0].base_name != 'air':
                        if block[0].base_name == 'glass':
                            bounding_box.add((x, y, z))
                        elif block[0].base_name in WoolType:
                            ports[WoolType(block[0].base_name)] = (x, y+1, z)
                        else:
                            if block[0].base_name == 'stone':
                                bounding_box.add((x, y, z))
                            blocks[(x, y, z)] = block[0]
        minecraft.close()
        # Calculate origin
        all_blocks = set(blocks.keys()).union(bounding_box)
        xs, ys, zs = [x[0] for x in all_blocks],  [x[1] for x in all_blocks],  [x[2] for x in all_blocks]
        origin = min(xs), min(ys), min(zs)
        blocks = {tupleSub(k, origin): v for k, v in blocks.items()}
        bounding_box = {tupleSub(k, origin) for k in bounding_box}
        ports = {k: tupleSub(v, origin) for k, v in ports.items()}

        size = tupleSub((max(xs), max(ys), max(zs)), origin)

        return Model(blocks, bounding_box, ports, size)

    def build(self, path: str):
        os.system(f"rm -r {path} && cp -r minecraft/data/flat {path}")
        minecraft = amulet.load_level(path)
        for coords, block in self.blocks.items():
            minecraft.set_version_block(coords[0], coords[1], coords[2], "minecraft:overworld", mc_version, block)
        minecraft.save()
        minecraft.close()
