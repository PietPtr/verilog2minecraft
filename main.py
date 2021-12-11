from compiler import graph, place, router
from compiler.daanpnr import place_and_route
from minecraft.world import World
from minecraft.components import ComponentManager
from dotenv import load_dotenv
import os
from util.coord import tupleAdd

load_dotenv()

unplaced = graph.load_graph("jsons/combi.json")
# placed = place_and_route(unplaced) 
placed = place.random_search(unplaced)
redstone_tracks = router.route(placed)


minecraft = World()
components = ComponentManager()

offset = (-70, 1, -135)

for cell in placed:
    model = components.get_component(cell.celltype)
    position = tupleAdd(cell.position, offset)
    minecraft.add_model(position, model)

for block, position in redstone_tracks:
    print(f"put {block} at {position}")
    minecraft.set_block(tupleAdd(position, offset), block.to_minecraft())

minecraft.build(os.getenv("HOME") + "/.minecraft/saves/output")
