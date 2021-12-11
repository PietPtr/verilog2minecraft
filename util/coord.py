from typing import Tuple
import numpy as np


def tupleAdd(a: Tuple[int, int, int], b: Tuple[int, int, int]) -> Tuple[int, int, int]:
    return tuple((x + y for x, y in zip(a, b)))


def tupleSub(a: Tuple[int, int, int], b: Tuple[int, int, int]) -> Tuple[int, int, int]:
    return tuple((x - y for x, y in zip(a, b)))


def dist(a: Tuple[int, int, int], b: Tuple[int, int, int]) -> int:
    return abs(a[0]-b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])

def rotate(v : Tuple[int, int, int], theta : int) -> Tuple[int, int, int]:
    (x, y, z) = v
    neppe_switch = {
        0: (x, y, z),
        90: (z, y, -x),
        180: (-x, y, -z),
        270: (-z, y, x),
        360: (x, y, z)
    }
    return neppe_switch[theta]

def to_np(v : Tuple[int, int, int]) -> np.ndarray:
    return np.array([v[0], v[1], v[2]])

def to_tup(v : np.ndarray) -> Tuple[int, int, int]:
    return (int(v[0]), int(v[1]), int(v[2]))
