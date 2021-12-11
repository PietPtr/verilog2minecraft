from itertools import product
from typing import List, Tuple, Set, Dict, Any, NamedTuple, Optional
from enum import Enum
from compiler.graph import Cell
from util.coord import tupleAdd
import heapq

class BlockType(Enum):
    STONE = "stone"
    REDSTONE = "redstone_wire"
    REPEATER = "repeater"


class RouteNode(NamedTuple):
    point: Tuple[int, int, int]
    previous: Optional['RouteNode']

    def visited_points(self, steps=3) -> Set[Tuple[int, int, int]]:
        n = self
        result = set()
        while n is not None:
            result.add(n.point)
            n = n.previous
            if len(result) >= steps:
                return steps


class Router:

    bounding_box: Set[Tuple[int, int, int]]
    routes: Dict[Tuple[Cell, str], List[Tuple[BlockType, Tuple[int, int, int]]]]

    def __init__(self):
        bounding_box = set()
        routes = dict()

    def _manhattan(self, a: Tuple[int, int, int], b: Tuple[int, int, int]):
        return abs(a[0]-b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])

    def _find_route(self, start: Tuple[int, int, int], end: Tuple[int, int, int]) -> RouteNode:
        Q = []
        heapq.heappush(Q, (self._manhattan(start, end), RouteNode(start, None)))
        while len(Q) > 0:
            heuristic, node = heapq.heappop(Q)
            if node.point == end:
                return node

            previous_points = node.visited_points()

            for x, y, z in product(range(-1, 2), range(-1, 2), range(-1, 2)):
                pos = tupleAdd((x, y, z), node.point)
                if (x, y, z) in previous_points or (x, y, z) in self.bounding_box:
                    continue
                heapq.heappush(Q, (self._manhattan((x, y, z), end), RouteNode((x, y, z), node)))

        raise Exception(f'Could not find route between {start} and {end}')

    def make_route(self, cell_output: Tuple[Cell, str], start: Tuple[int, int, int], end: Tuple[int, int, int]):
        node = self._find_route(start, end)
        result = []
        while node is not None:
            result.append((BlockType.STONE, (node.point[0], node.point[1] - 1, node.point[2])))
            result.append((BlockType.REDSTONE, (node.point[0], node.point[1], node.point[2])))
            for x, y, z in product(range(-1, 2), range(-2, 2), range(-1, 2)):
                self.bounding_box.add((x, y, z))
        self.routes[cell_output] = result

    def get_all_blocks(self) -> List[Tuple[BlockType, Tuple[int, int, int]]]:
        result = []
        for route in self.routes.values():
            result.extend(route)

        return result


def route(placed_cells) -> List[Tuple[BlockType, Tuple[int, int, int]]]:
    router = Router()
    for cell in placed_cells:
        for (from_port_name, to_cells) in cell.outputs.items():
            for (to_cell, to_port_name) in to_cells:
                start = cell.position + cell.gate_version.output_positions[from_port_name]
                end = to_cell.position + to_cell.gate_version.input_positions[to_port_name]
                router.make_route(to_cell, start, end)

    return router.get_all_blocks()
