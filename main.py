from typing import Tuple, Set

from compiler import graph, place, router
from compiler.daanpnr import place_and_route
from minecraft.world import World
from minecraft.components import ComponentManager
from dotenv import load_dotenv
import os
from util.coord import tupleAdd
from pprint import pprint

load_dotenv()

unplaced = graph.load_graph("jsons/test.json")
# placed = place_and_route(unplaced)
placed = place.random_search(unplaced)
netmap = place.placed_to_netmap(placed)

minecraft = World()
components = ComponentManager()
offset = (0, 2, 0)

static_bounding_box: Set[Tuple[int, int, int]] = set()

for cell in placed:
    model = components.get_component(cell.celltype)
    # model.fill_area(cell.gate_version.size)
    position = tupleAdd(cell.position, offset)
    minecraft.add_model(position, model)
    static_bounding_box.update(tupleAdd(position, pos) for pos in model.bounding_box)

minecraft.build(os.getenv("HOME") + "/.minecraft/saves/output")

redstone_tracks = router.create_routes(netmap, static_bounding_box)
print(redstone_tracks)

for block, position in redstone_tracks:
    print(f"put {block} at {position}")
    minecraft.set_block(tupleAdd(position, offset), block.to_minecraft())

minecraft.build(os.getenv("HOME") + "/.minecraft/saves/output")
