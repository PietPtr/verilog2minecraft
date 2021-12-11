import time
from itertools import product
from typing import List, Tuple, Set, Dict, Any, NamedTuple, Optional
from enum import Enum

from amulet import Block

from compiler.graph import Cell
from util.coord import tupleAdd
import heapq
FOUR_DIRECTIONS = [(1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1)]
ALL_DIRECTIONS = [(x, y + a, z) for x, y, z in FOUR_DIRECTIONS for a in range(-1, 2)]
print(ALL_DIRECTIONS)



class BlockType(Enum):
    STONE = "stone"
    REDSTONE = "redstone_wire"
    REPEATER = "repeater"
    WHITE_WOOL = "white_wool"
    ORANGE_WOOL = "orange_wool"
    MAGENTA_WOOL = "magenta_wool"
    LIGHT_BLUE_WOOL = "light_blue_wool"
    YELLOW_WOOL = "yellow_wool"
    LIME_WOOL = "lime_wool"
    PINK_WOOL = "pink_wool"
    GRAY_WOOL = "gray_wool"
    LIGHT_GRAY_WOOL = "light_gray_wool"
    CYAN_WOOL = "cyan_wool"
    PURPLE_WOOL = "purple_wool"
    BLUE_WOOL = "blue_wool"
    BROWN_WOOL = "brown_wool"
    GREEN_WOOL = "green_wool"
    RED_WOOL = "red_wool"
    BLACK_WOOL = "black_wool"

    def to_minecraft(self) -> Block:
        return Block('minecraft', self.value)
    
    def num_to_wool(idx):
        # haha dit is gewoon een array (:  
        num_to_wool = {
            0: BlockType.WHITE_WOOL,
            1: BlockType.ORANGE_WOOL,
            2: BlockType.MAGENTA_WOOL,
            3: BlockType.LIGHT_BLUE_WOOL,
            4: BlockType.YELLOW_WOOL,
            5: BlockType.LIME_WOOL,
            6: BlockType.PINK_WOOL,
            7: BlockType.GRAY_WOOL,
            8: BlockType.LIGHT_GRAY_WOOL,
            9: BlockType.CYAN_WOOL,
            10: BlockType.PURPLE_WOOL,
            11: BlockType.BLUE_WOOL,
            12: BlockType.BROWN_WOOL,
            13: BlockType.GREEN_WOOL,
            14: BlockType.RED_WOOL,
            15: BlockType.BLACK_WOOL
        }
        return num_to_wool[idx % 16]


    

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
    bounding_box_route: Dict[Tuple[int, int, int], Set[Tuple[int, int, int]]]

    def __init__(self):
        self.bounding_box = set()
        self.routes = dict()
        self.bounding_box_route = dict()

    def _manhattan(self, a: Tuple[int, int, int], b: Tuple[int, int, int]):
        return abs(a[0]-b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])

    def _find_route(self, start: Tuple[int, int, int], end: Tuple[int, int, int]) -> RouteNode:
        Q = []
        heapq.heappush(Q, (self._manhattan(start, end), 0, RouteNode(start, None, 0)))
        best = self._manhattan(start, end)
        visited = set()
        while 0 < len(Q) < 1000:
            heuristic, unused, node = heapq.heappop(Q)
            if node.point == end:
                return node

            if heuristic < best:
                best = heuristic

            previous_points = node.visited_points()

            for x, y, z in ALL_DIRECTIONS:
                pos = tupleAdd((x, y, z), node.point)
                if pos != end and (
                        pos in previous_points or
                        (pos in self.bounding_box - self.bounding_box_route.get(end, set())) or
                        (pos[0], pos[1] - 1, pos[2]) in previous_points or
                        (pos[0], pos[1] - 2, pos[2]) in previous_points
                ):
                    continue
                if pos in visited:
                    continue
                visited.add(pos)
                heapq.heappush(Q, (self._manhattan(pos, end) + node.length + 1, -node.length, RouteNode(pos, node, node.length + 1)))

        raise Exception(f'Could not find route between {start} and {end}. Closest: {best}, start: {self._manhattan(start, end)}')

    def fill_bb_with_placed_graph(self, placed: List[Cell]):
        for cell in placed:
            tl = cell.position
            br = cell.position + cell.gate_version.size
            allowed = [tuple(x) for x in cell.gate_version.output_positions.values()] + [tuple(x) for x in cell.gate_version.input_positions.values()]
            for x in range(tl[0], br[0] + 1):
                for y in range(tl[1], br[1] + 1):
                    for z in range(tl[2], br[2] + 1):
                        if (x, y, z) in allowed:
                            continue
                        self.bounding_box.add((x, y, z))

    def make_route(self, cell_output: Tuple[Cell, str], start: Tuple[int, int, int], end: Tuple[int, int, int]):
        node = self._find_route(start, end)
        print(f"found route from {start}->{end}")
        result = []
        if end not in self.bounding_box_route:
            self.bounding_box_route[end] = set()

        while node is not None:
            wool_idx = sum(map(ord, cell_output.name))
            result.append((BlockType.num_to_wool(wool_idx), (node.point[0], node.point[1] - 1, node.point[2])))
            result.append((BlockType.REDSTONE, (node.point[0], node.point[1], node.point[2])))
            for x, y, z in product(range(-1, 2), range(-2, 3), range(-1, 2)):
                pos = tupleAdd((x, y, z), node.point)
                self.bounding_box.add(pos)
                self.bounding_box_route[end].add((x, y, z))
            node = node.previous
        if cell_output not in self.routes:
            self.routes[cell_output] = []
        self.routes[cell_output].append(result)

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
                print(cell, to_cell)
                try:
                    router.make_route(to_cell, (start[0], start[1], start[2]), (end[0], end[1], end[2]))
                except Exception as e:

                    print(e)

    return router.get_all_blocks()
