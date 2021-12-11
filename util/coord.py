from typing import Tuple


def tupleAdd(a: Tuple[int, int, int], b: Tuple[int, int, int]) -> Tuple[int, int, int]:
    return tuple((x + y for x, y in zip(a, b)))

def dist(a: Tuple[int, int, int], b: Tuple[int, int, int]) -> int:
    return abs(a[0]-b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])
