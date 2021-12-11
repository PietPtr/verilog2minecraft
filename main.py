from compiler import graph, place, router
from minecraft.world import World
from minecraft.components import ComponentManager
from dotenv import load_dotenv
import os

load_dotenv()

unplaced = graph.load_graph("test.json")
placed = place.random_search(unplaced)
routed = router.route(placed)


minecraft = World()
components = ComponentManager()

for cell in placed:
    model = components.get_component(cell.celltype)
    position = [cell.position[0] - 70, cell.position[1], cell.position[2] - 135]
    minecraft.add_model(position, model)

minecraft.build(os.getenv("HOME") + "/.minecraft/saves/output")
