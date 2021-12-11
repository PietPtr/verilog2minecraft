from typing import Tuple


def tupleAdd(a: Tuple[int, int, int], b: Tuple[int, int, int]) -> Tuple[int, int, int]:
    return tuple((x + y for x, y in zip(a, b)))
