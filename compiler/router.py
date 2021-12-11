from itertools import product
from typing import List, Tuple, Set, Dict, Any, NamedTuple, Optional
from enum import Enum

from amulet import Block

from compiler.graph import Cell
from util.coord import tupleAdd
import heapq

class BlockType(Enum):
    STONE = "stone"
    REDSTONE = "redstone_wire"
    REPEATER = "repeater"

    def to_minecraft(self) -> Block:
        return Block('minecraft', self.value)

class RouteNode(NamedTuple):
    point: Tuple[int, int, int]
    previous: Optional['RouteNode']
    length: int

    def visited_points(self, steps=6) -> Set[Tuple[int, int, int]]:
        n = self
        result = set()
        while n is not None:
            result.add(n.point)
            n = n.previous
            if len(result) >= steps:
                return result
        return result


class Router:

    bounding_box: Set[Tuple[int, int, int]]
    routes: Dict[Tuple[Cell, str], List[List[Tuple[BlockType, Tuple[int, int, int]]]]]

    def __init__(self):
        self.bounding_box = set()
        self.routes = dict()

    def _manhattan(self, a: Tuple[int, int, int], b: Tuple[int, int, int]):
        return abs(a[0]-b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])

    def _find_route(self, start: Tuple[int, int, int], end: Tuple[int, int, int]) -> RouteNode:
        Q = []
        heapq.heappush(Q, (self._manhattan(start, end), RouteNode(start, None, 0)))
        while len(Q) > 0:
            heuristic, node = heapq.heappop(Q)
            if node.point == end:
                return node
        
            previous_points = node.visited_points()
            FOUR_DIRECTIONS = [(1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1)]
            for x, y, z in FOUR_DIRECTIONS + [(d[0], 1, [d[2]]) for d in FOUR_DIRECTIONS] + [(d[0], -1, d[2]) for d in FOUR_DIRECTIONS]:
                pos = tupleAdd((x, y, z), node.point)
                if (x, y, z) in previous_points or (x, y, z) in self.bounding_box:
                    continue
                heapq.heappush(Q, (self._manhattan(pos, end) + node.length, RouteNode(pos, node, node.length + 1)))

        raise Exception(f'Could not find route between {start} and {end}')

    def fill_bb_with_placed_graph(self, placed):
        # TODO: lists inputs/outputs as blocklisted points, is that a problem? tool it yourself.
        for cell in placed:
            tl = cell.position
            br = cell.position + cell.gate_version.size
            for x in range(tl[0], br[0] + 1):
                for y in range(tl[0], br[0] + 1):
                    for z in range(tl[0], br[0] + 1):
                        self.bounding_box.add(x, y, z)

    def make_route(self, cell_output: Tuple[Cell, str], start: Tuple[int, int, int], end: Tuple[int, int, int]):
        try:
            node = self._find_route(start, end)
        except:
            return 
        print(f"found route from {start}->{end}")
        result = []
        while node is not None:
            result.append((BlockType.STONE, (node.point[0], node.point[1] - 1, node.point[2])))
            result.append((BlockType.REDSTONE, (node.point[0], node.point[1], node.point[2])))
            for x, y, z in product(range(-1, 2), range(-2, 2), range(-1, 2)):
                self.bounding_box.add((x, y, z))
            node = node.previous
        if cell_output not in self.routes:
            self.routes[cell_output] = []
        self.routes[cell_output].append(result)
        print("self.routes:", self.routes)

    def get_all_blocks(self) -> List[Tuple[BlockType, Tuple[int, int, int]]]:
        result = []
        for routes in self.routes.values():
            for route in routes:
                result.extend(route)
                print(route)

        return result


def route(placed_cells) -> List[Tuple[BlockType, Tuple[int, int, int]]]:
    router = Router()
    router.fill_bb_with_placed_graph(placed_cells)
    for cell in placed_cells:
        for (from_port_name, to_cells) in cell.outputs.items():
            for (to_cell, to_port_name) in to_cells:
                start = cell.position + cell.gate_version.output_positions[from_port_name]
                end = to_cell.position + to_cell.gate_version.input_positions[to_port_name]
                router.make_route(to_cell, (start[0], start[1], start[2]), (end[0], end[1], end[2]))

    return router.get_all_blocks()
