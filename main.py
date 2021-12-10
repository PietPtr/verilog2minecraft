from compiler import graph, place
from minecraft.world import World
from minecraft.components import ComponentManager


unplaced = graph.load_graph("test.json")
placed = place.random_search(unplaced)

print(place.manhattan_distance(placed))
print(placed)

minecraft = World()
components = ComponentManager()

for cell in placed:
    model = components.get_component(cell.celltype)
    minecraft.add_model(cell.position, model)

minecraft.build("/home/daan/.minecraft/saves/output")
