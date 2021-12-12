import random
import time
from itertools import product
from typing import List, Tuple, Set, Dict, Any, NamedTuple, Optional
from enum import Enum

from amulet import Block
from amulet_nbt import TAG_String

from compiler.graph import Cell
from util.coord import tupleAdd, tupleSub
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


class RoutingBlock:
    block_type: BlockType
    properties: Dict[str, TAG_String]

    def __init__(self, block_type: BlockType, direction: Tuple[Tuple[int, int, int], Tuple[int, int, int]] = None):
        self.block_type = block_type
        self.properties = dict()
        if direction:
            self.set_orientation(direction[0], direction[1])

    def to_minecraft(self) -> Block:
        return Block('minecraft', self.block_type.value, properties=self.properties)

    def set_orientation(self, prev: Tuple[int, int, int], this: Tuple[int, int, int]):
        delta = tupleSub(this, prev)
        if delta == (0, 0, 1):
            self.properties['facing'] = TAG_String('north')
        elif delta == (0, 0, -1):
            self.properties['facing'] = TAG_String('south')
        elif delta == (1, 0, 0):
            self.properties['facing'] = TAG_String('west')
        elif delta == (-1, 0, 0):
            self.properties['facing'] = TAG_String('east')

    def __str__(self):
        return f'RoutingBlock({self.block_type.value})'

    def __repr__(self):
        return str(self)

class RouteNode(NamedTuple):
    point: Tuple[int, int, int]
    previous: Optional['RouteNode']
    length: int
    last_straight: int

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
    all_routes: Dict[Tuple[int, int, int], List[Tuple[RoutingBlock, Tuple[int, int, int]]]]
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
                    maxQ: int, max_depth: int = None, max_counter: int = 100, is_revese: bool = False) -> RouteNode:
        Q = []
        self.iterations = 0
        last_repeater = 7 if start == original_start else 15
        heapq.heappush(Q, (self._manhattan(start, end), 0, RouteNode(start, None, 0, last_repeater)))
        best = self._manhattan(start, end)
        visited = set()
        collision_output: Optional[List[Tuple[int, int, int]]] = None
        collision_dist: int = self._manhattan(start, end) + 100
        last_distance = self._manhattan(start, end)
        start_distance = self._manhattan(start, end)
        could_not_expand = set()
        counter = 0
        while 0 < len(Q) < maxQ and counter <= max_counter:
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
            directions = ALL_DIRECTIONS

            if node.last_straight >= 15:
                newx, _, newz = tupleSub(node.point, node.previous.point)
                directions = [(newx, 0, newz)]

            for x, y, z in directions:
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
                last_straight = node.last_straight + 1
                delta = tupleSub(pos, node.point)
                if node.previous and tupleSub(node.point, node.previous.point) == delta and delta[1] == 0 and delta.count(0) == 2:
                    last_straight = 1
                heapq.heappush(Q, (self._manhattan(pos, end), node.length + 1, RouteNode(pos, node, node.length + 1, last_straight)))

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
            if block.block_type in (BlockType.REDSTONE, BlockType.REPEATER):
                for offset in BOUNDING_DIRECTIONS:
                    bounding_pos = tupleAdd(pos, offset)
                    try:
                        self.blocks_to_route_starts[bounding_pos].remove(route_start)
                    except KeyError:
                        pass
        del self.bounding_box_route[route_start]
        del self.all_routes[route_start]
        self.recompute_bounding_box()

    def make_route(self, start: Tuple[int, int, int], end: Tuple[int, int, int], max_counter: int):
        best_pos, best = start, self._manhattan(start, end)
        last_pos = start
        if start in self.all_routes:
            for block, pos in self.all_routes[start]:
                if block != BlockType.REDSTONE or tupleSub(pos, last_pos)[1] != 0:
                    last_pos = pos
                    continue
                last_pos = pos
                score = self._manhattan(pos, end)
                if score < best:
                    best_pos, best = pos, score
        print(f"Starting route from {best_pos}({start})->{end}")
        try:
            tmp_node = self._find_route(end, end, best_pos, 150, max_depth=4, max_counter=25, is_revese=True)
        except NoRouteFoundException as e:
            if e.start_dist - e.end_dist <= 4:
                print('Finding reverse route failed! Throwing exception')
                raise e

        node = self._find_route(start, best_pos, end, 100000, max_counter=max_counter)

        print(f"found route from {best_pos}({start})->{end} in {self.iterations} iterations")
        result = []
        if start not in self.bounding_box_route:
            self.bounding_box_route[start] = set()

        last_possible: Tuple[int, Tuple[int, int, int]] = None
        last_repeated: int = 5
        ordered_nodes: List[RouteNode] = []
        while node is not None:
            ordered_nodes.append(node)
            node = node.previous
        ordered_nodes = list(reversed(ordered_nodes))

        for idx, node in enumerate(ordered_nodes):
            wool_idx = sum(start)
            if idx+1 < len(ordered_nodes) and ordered_nodes[idx+1].last_straight == 1:
                last_possible = (len(result) + 1, node.point)
            result.append((RoutingBlock(WoolType.num_to_wool(wool_idx)), (node.point[0], node.point[1] - 1, node.point[2])))
            result.append((RoutingBlock(BlockType.REDSTONE), (node.point[0], node.point[1], node.point[2])))
            if last_repeated >= 15:
                prev = result[last_possible[0]-2][1]
                result[last_possible[0]] = (RoutingBlock(BlockType.REPEATER, (prev, last_possible[1])), last_possible[1])
                last_repeated = (len(result) - last_possible[0])//2 - 1
            last_repeated += 1
            for x, y, z in BOUNDING_DIRECTIONS:
                pos = tupleAdd((x, y, z), node.point)
                self.bounding_box.add(pos)
                self.bounding_box_route[start].add(pos)
                if pos not in self.blocks_to_route_starts:
                    self.blocks_to_route_starts[pos] = set()
                self.blocks_to_route_starts[pos].add(start)

        if start not in self.all_routes:
            self.all_routes[start] = []

        self.all_routes[start].extend(result)

    def get_all_blocks(self) -> List[Tuple[RoutingBlock, Tuple[int, int, int]]]:
        result = []
        for route in self.all_routes.values():
            result.extend(route)
        return result


router = None
def create_routes(network: Dict[Tuple[int, int, int], List[Tuple[int, int, int]]],
                  component_bounding_box: Set[Tuple[int, int, int]]) -> List[Tuple[RoutingBlock, Tuple[int, int, int]]]:
    global router
    router = Router(network, component_bounding_box)
    todo = [start for start in network.keys()]
    base = 1
    while len(todo) > 0:
        print(f'Todo size: {len(todo)}')
        start = todo.pop(0)
        tries = 0
        for end in network[start]:
            print(f'Routing {start} -> {end}')
            while True:
                try:
                    router.make_route(start, end, min(500 + 1000*tries, 7500))
                    break
                except NoRouteFoundException as e:
                    print(e)
                    tries += 1
                    base += 1
                    if e.collision is None:
                        continue
                    for collision_start in e.collision:
                        print(f"Removing routes from point: {collision_start}")
                        router.remove_route(collision_start)
                        todo.append(collision_start)
                        random.shuffle(todo)

    return router.get_all_blocks()
