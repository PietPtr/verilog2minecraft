import signal
import sys
from typing import Tuple, Set

from compiler import graph, place, router, cell_defs
from compiler.daanpnr import place_and_route
from minecraft.world import World
from minecraft.components import ComponentManager
from dotenv import load_dotenv
import os
from util.coord import tupleAdd
from pprint import pprint

load_dotenv()

minecraft = World()
components = ComponentManager()

unplaced = graph.load_graph("jsons/test.json", "constraints.txt", components)
placed = place_and_route(unplaced)
# placed = place.random_search(unplaced, iterations=10000)
# placed = place.place_sa(unplaced)
netmap = place.placed_to_netmap(placed)

offset = (0, 2, 0)

static_bounding_box: Set[Tuple[int, int, int]] = set()

for cell in placed:
    model = components.get_model(cell.gate_version.implementation_file)
    position = tupleAdd(cell.position, offset)
    minecraft.add_model(position, model)
    # minecraft.add_model_bounding(tupleAdd(position, (0, 20, 0)), model)
    static_bounding_box.update(tupleAdd(cell.position, pos) for pos in model.bounding_box)


def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    print('Saving routing world so far...')
    redstone_tracks = router.router.get_all_blocks()

    for block, position in redstone_tracks:
        # print(f"put {block} at {position}")
        minecraft.set_block(tupleAdd(position, offset), block.to_minecraft())

    minecraft.build(os.getenv("HOME") + "/.minecraft/saves/output")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


redstone_tracks = router.create_routes(netmap, static_bounding_box)

for block, position in redstone_tracks:
    # print(f"put {block.to_minecraft()} at {position}")
    minecraft.set_block(tupleAdd(position, offset), block.to_minecraft())

minecraft.build(os.getenv("HOME") + "/.minecraft/saves/output")
