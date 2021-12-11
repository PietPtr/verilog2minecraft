import time
from itertools import product
from typing import List, Tuple, Set, Dict, Any, NamedTuple, Optional
from enum import Enum

from amulet import Block

from compiler.graph import Cell
from util.coord import tupleAdd
import heapq

from util.wool import WoolType

FOUR_DIRECTIONS = [(1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1)]
ALL_DIRECTIONS = [(x, y + a, z) for x, y, z in FOUR_DIRECTIONS for a in range(-1, 2)]
print(ALL_DIRECTIONS)
    
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


class NoRouteFoundException(Exception):
    collision: Set[Tuple[int, int, int]]

    def __init__(self, collision_output: Set[Tuple[int, int, int]], msg: str):
        self.collision = collision_output
        super(NoRouteFoundException, self).__init__(msg)


class Router:

    bounding_box: Set[Tuple[int, int, int]]
    bounding_box_static: Set[Tuple[int, int, int]]
    bounding_box_route: Dict[Tuple[int, int, int], Set[Tuple[int, int, int]]]
    all_routes: Dict[Tuple[int, int, int], List[Tuple[BlockType, Tuple[int, int, int]]]]
    blocks_to_route_starts: Dict[Tuple[int, int, int], Set[Tuple[int, int, int]]]

    def __init__(self, static_bounding_box: Set[Tuple[int, int, int]]):
        self.bounding_box = set()
        self.bounding_box_static = static_bounding_box
        self.all_routes = dict()
        self.bounding_box_route = dict()
        self.blocks_to_route_starts = dict()
        self.recompute_bounding_box()

    def _manhattan(self, a: Tuple[int, int, int], b: Tuple[int, int, int]):
        return abs(a[0]-b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])

    def _find_route(self, original_start: Tuple[int, int, int], start: Tuple[int, int, int], end: Tuple[int, int, int]) -> RouteNode:
        Q = []
        heapq.heappush(Q, (self._manhattan(start, end), 0, RouteNode(start, None, 0)))
        best = self._manhattan(start, end)
        visited = set()
        collision_output: Optional[List[Tuple[int, int, int]]] = None
        while 0 < len(Q) < 10000:
            heuristic, unused, node = heapq.heappop(Q)
            if node.point == end:
                return node

            if self._manhattan(node.point, end) < best:
                best = self._manhattan(node.point, end)

            previous_points = node.visited_points()

            for x, y, z in ALL_DIRECTIONS:
                pos = tupleAdd((x, y, z), node.point)
                if pos != end and (
                        pos in previous_points or
                        (pos in self.bounding_box - self.bounding_box_route.get(original_start, set())) or
                        ((pos[0], pos[1] - 1, pos[2]) in self.bounding_box - self.bounding_box_route.get(original_start, set())) or
                        (pos[0], pos[1] - 1, pos[2]) in previous_points or
                        (pos[0], pos[1] + 1, pos[2]) in previous_points
                ):
                    collision_output = self.blocks_to_route_starts.get(pos, None) or \
                                       self.blocks_to_route_starts.get((pos[0], pos[1] - 1, pos[2]), None) or \
                                       self.blocks_to_route_starts.get((pos[0], pos[1] - 2, pos[2]), None)
                    continue

                if pos in visited:
                    continue
                visited.add(pos)

                # if self._manhattan(pos, end) <= 2:
                #     print(f'Adding {pos} with distance {self._manhattan(pos, end)}')
                heapq.heappush(Q, (self._manhattan(pos, end) + node.length + 1, -node.length, RouteNode(pos, node, node.length + 1)))

        raise NoRouteFoundException(collision_output,
                                    f'Could not find route between {start} and {end}. Closest: {best}, start: {self._manhattan(start, end)}')

    def recompute_bounding_box(self):
        self.bounding_box.clear()
        self.bounding_box.update(self.bounding_box_static)
        for bb in self.bounding_box_route.values():
            self.bounding_box.update(bb)

    def remove_route(self, route_start: Tuple[int, int, int]):
        routes = self.all_routes[route_start]
        for block, pos in routes:
            if pos in self.blocks_to_route_starts:
                self.blocks_to_route_starts[pos].remove(route_start)
            else:
                print('WARNING!!!')
        del self.bounding_box_route[route_start]
        del self.all_routes[route_start]
        self.recompute_bounding_box()

    def make_route(self, start: Tuple[int, int, int], end: Tuple[int, int, int]):
        best_pos, best = start, self._manhattan(start, end)
        if start in self.all_routes:
            for block, pos in self.all_routes[start]:
                if block != BlockType.REDSTONE:
                    continue
                score = self._manhattan(pos, end)
                if score < best:
                    best_pos, best = pos, score
        print(f"Starting route from {best_pos}({start})->{end}")
        node = self._find_route(start, best_pos, end)

        print(f"found route from {best_pos}({start})->{end}")
        result = []
        if start not in self.bounding_box_route:
            self.bounding_box_route[start] = set()

        while node is not None:
            wool_idx = sum(start)
            result.append((WoolType.num_to_wool(wool_idx), (node.point[0], node.point[1] - 1, node.point[2])))
            result.append((BlockType.REDSTONE, (node.point[0], node.point[1], node.point[2])))
            for x, y, z in product(range(-1, 2), range(-2, 2), range(-1, 2)):
                pos = tupleAdd((x, y, z), node.point)
                self.bounding_box.add(pos)
                self.bounding_box_route[start].add(pos)
                if pos not in self.blocks_to_route_starts:
                    self.blocks_to_route_starts[pos] = set()
                self.blocks_to_route_starts[pos].add(start)
            node = node.previous
        if start not in self.all_routes:
            self.all_routes[start] = []

        self.all_routes[start].extend(result)

    def get_all_blocks(self) -> List[Tuple[BlockType, Tuple[int, int, int]]]:
        result = []
        for route in self.all_routes.values():
            result.extend(route)
        return result


def create_routes(network: Dict[Tuple[int, int, int], List[Tuple[int, int, int]]],
                  component_bounding_box: Set[Tuple[int, int, int]]) -> List[Tuple[BlockType, Tuple[int, int, int]]]:
    router = Router(component_bounding_box)
    todo = [start for start in network.keys()]
    while len(todo) > 0:
        start = todo.pop(0)
        for end in network[start]:
            print(f'Routing {start} -> {end}')
            while True:
                try:
                    router.make_route(start, end)
                    break
                except NoRouteFoundException as e:
                    print(e)
                    for collision_start in e.collision:
                        print(f"Removing routes from point: {e.collision}")
                        router.remove_route(collision_start)
                        todo.append(collision_start)

    return router.get_all_blocks()
