from compiler import graph, place, router
from minecraft.world import World
from minecraft.components import ComponentManager
from dotenv import load_dotenv
import os

load_dotenv()

print(os.getenv("HOME"))

unplaced = graph.load_graph("test.json")
placed = place.random_search(unplaced)
routed = router.route(placed)

print(place.manhattan_distance(placed))
print(placed)

minecraft = World()
components = ComponentManager()

for cell in placed:
    model = components.get_component(cell.celltype)
    minecraft.add_model(cell.position, model)

minecraft.build(os.getenv("HOME") + ".minecraft/saves/output")
