import graph
import place
import router

from pprint import pprint

# TODO: neem een verilog file en draai yosys zelf met de goede .ys
def synthesize(json_file):
    unplaced = graph.load_graph(json_file)
    placed = place.random_search(unplaced)

    print(place.manhattan_distance(placed))

synthesize("test.json")
