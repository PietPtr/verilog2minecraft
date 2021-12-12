import random
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
BOUNDING_DIRECTIONS = list(product(range(-1, 2), range(-2, 3), range(-1, 2)))

    
class BlockType(Enum):
    STONE = "stone"
    REDSTONE = "redstone_wire"
    REPEATER = "repeater"
    GLASS = "glass"

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
    could_not_expand: Set[Tuple[int, int, int]]
    start_dist: int
    end_dist: int

    def __init__(self, collision_output: Set[Tuple[int, int, int]], start_dist: int, end_dist: int, could_not_expand: Set[Tuple[int, int, int]], msg: str):
        self.collision = collision_output
        self.start_dist = start_dist
        self.end_dist = end_dist
        self.could_not_expand = could_not_expand
        super(NoRouteFoundException, self).__init__(msg)


class Router:

    bounding_box: Set[Tuple[int, int, int]]
    bounding_box_static: Set[Tuple[int, int, int]]
    bounding_box_route: Dict[Tuple[int, int, int], Set[Tuple[int, int, int]]]
    all_routes: Dict[Tuple[int, int, int], List[Tuple[BlockType, Tuple[int, int, int]]]]
    blocks_to_route_starts: Dict[Tuple[int, int, int], Set[Tuple[int, int, int]]]
    network: Dict[Tuple[int, int, int], List[Tuple[int, int, int]]]
    iterations: int

    def __init__(self, network: Dict[Tuple[int, int, int], List[Tuple[int, int, int]]], static_bounding_box: Set[Tuple[int, int, int]]):
        self.bounding_box = set()
        self.bounding_box_static = static_bounding_box
        self.all_routes = dict()
        self.bounding_box_route = dict()
        self.blocks_to_route_starts = dict()
        self.network = network
        self.connection_points = set()
        for endpoints in self.network.values():
            self.connection_points.update(endpoints)
        for startpoints in self.network.keys():
            self.connection_points.add(startpoints)
        self.recompute_bounding_box()

    def _manhattan(self, a: Tuple[int, int, int], b: Tuple[int, int, int]):
        return abs(a[0]-b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])

    def _find_route(self, original_start: Tuple[int, int, int], start: Tuple[int, int, int], end: Tuple[int, int, int],
                    maxQ: int, max_depth: int = None) -> RouteNode:
        Q = []
        self.iterations = 0
        heapq.heappush(Q, (self._manhattan(start, end), 0, RouteNode(start, None, 0)))
        best = self._manhattan(start, end)
        visited = set()
        collision_output: Optional[List[Tuple[int, int, int]]] = None
        collision_dist: int = self._manhattan(start, end) + 100
        last_distance = self._manhattan(start, end)
        start_distance = self._manhattan(start, end)
        could_not_expand = set()
        counter = 0
        while 0 < len(Q) < maxQ and counter <= 500 and self.iterations <= 5000:
            self.iterations += 1
            heuristic, unused, node = heapq.heappop(Q)
            if node.point == end:
                return node

            current_dist = self._manhattan(node.point, end)

            if max_depth and start_distance - current_dist >= max_depth:
                return node

            if current_dist < best:
                best = current_dist
                counter = 0

            if last_distance <= current_dist:
                counter += 1

            last_distance = current_dist

            previous_points = node.visited_points().union({end})
            random.shuffle(ALL_DIRECTIONS)
            for x, y, z in ALL_DIRECTIONS:
                pos = tupleAdd((x, y, z), node.point)
                positions_to_check = {pos, tupleAdd(pos, (0, 1, 0)), tupleAdd(pos, (0, -1, 0))}
                own_bounding = set([tupleAdd(pos, offset) for offset in BOUNDING_DIRECTIONS])
                dynamic_bounding_box_intersects = False
                for pos_to_check in positions_to_check:
                    if self.blocks_to_route_starts.get(pos_to_check, set()) - {original_start} != set():
                        dynamic_bounding_box_intersects = True
                        dist = self._manhattan(pos_to_check, end)
                        if collision_output is None or dist < collision_dist:
                            collision_output = self.blocks_to_route_starts.get(pos_to_check, None)
                            collision_dist = dist

                if pos != end and (
                        own_bounding.intersection(self.connection_points) - {start, end} != set() or
                        positions_to_check.intersection(previous_points) != set() or
                        tupleAdd(pos, (0, 2, 0)) in previous_points or
                        tupleAdd(pos, (0, -2, 0)) in previous_points or
                        positions_to_check.intersection(self.bounding_box_static) != set() or
                        dynamic_bounding_box_intersects
                ):
                    could_not_expand.add(pos)
                    continue

                if pos in visited:
                    continue
                visited.add(pos)

                # if self._manhattan(pos, end) <= 2:
                #     print(f'Adding {pos} with distance {self._manhattan(pos, end)}')
                heapq.heappush(Q, (self._manhattan(pos, end), node.length + 1, RouteNode(pos, node, node.length + 1)))

        raise NoRouteFoundException(collision_output.copy() if collision_output else None, self._manhattan(start, end), best, could_not_expand,
                                    f'Could not find route between {start} and {end}. Closest: {best}, start: {self._manhattan(start, end)}')

    def recompute_bounding_box(self):
        self.bounding_box.clear()
        self.bounding_box.update(self.bounding_box_static)
        for bb in self.bounding_box_route.values():
            self.bounding_box.update(bb)

    def remove_route(self, route_start: Tuple[int, int, int]):
        routes = self.all_routes[route_start]
        for block, pos in routes:
            if block == BlockType.REDSTONE:
                for offset in BOUNDING_DIRECTIONS:
                    bounding_pos = tupleAdd(pos, offset)
                    try:
                        self.blocks_to_route_starts[bounding_pos].remove(route_start)
                    except KeyError:
                        pass
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
        try:
            tmp_node = self._find_route(end, end, best_pos, 150, max_depth=4)
        except NoRouteFoundException as e:
            if e.start_dist - e.end_dist <= 4:
                print('Finding reverse route failed! Throwing exception')
                raise e

        node = self._find_route(start, best_pos, end, 100000)

        print(f"found route from {best_pos}({start})->{end} in {self.iterations} iterations")
        result = []
        if start not in self.bounding_box_route:
            self.bounding_box_route[start] = set()

        while node is not None:
            wool_idx = sum(start)
            result.append((WoolType.num_to_wool(wool_idx), (node.point[0], node.point[1] - 1, node.point[2])))
            result.append((BlockType.REDSTONE, (node.point[0], node.point[1], node.point[2])))
            for x, y, z in BOUNDING_DIRECTIONS:
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

    def get_bounding_blocks(self, could_not_expand: Set[Tuple[int, int, int]]) -> List[Tuple[BlockType, Tuple[int, int, int]]]:
        result = self.get_all_blocks()
        for static_block in self.bounding_box_static:
            result.append((BlockType.GLASS, static_block))
        for route, box in self.bounding_box_route.items():
            result.extend([(WoolType.num_to_wool(sum(route)), pos) for pos in box])
        result.extend((WoolType.RED_WOOL, b) for b in could_not_expand)
        return result

router = None
def create_routes(network: Dict[Tuple[int, int, int], List[Tuple[int, int, int]]],
                  component_bounding_box: Set[Tuple[int, int, int]]) -> List[Tuple[BlockType, Tuple[int, int, int]]]:
    global router
    router = Router(network, component_bounding_box)
    todo = [start for start in network.keys()]
    while len(todo) > 0:
        print(f'Todo size: {len(todo)}')
        start = todo.pop(0)
        for end in network[start]:
            print(f'Routing {start} -> {end}')
            while True:
                try:
                    router.make_route(start, end)
                    break
                except NoRouteFoundException as e:
                    print(e)
                    if e.collision is None:
                        return router.get_bounding_blocks(e.could_not_expand)
                    for collision_start in e.collision:
                        print(f"Removing routes from point: {collision_start}")
                        router.remove_route(collision_start)
                        todo.append(collision_start)
                        random.shuffle(todo)

    return router.get_all_blocks()
