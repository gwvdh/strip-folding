from typing import Dict, Tuple, List
from grid import TriangleGrid
from itertools import permutations


class Face:
    def __init__(self, length: int):
        self._length: int = length


class Strip:
    def __init__(self, crease_amount: int, faces: List[Face], creases: int):
        self._crease_amount: int = crease_amount
        self._faces: List[Face] = faces
        self._creases: int = creases
        self._database: Dict[int, FoldedStrip] = {}

    def is_simple_foldable(self) -> bool:
        amount_of_creases: int = len(bin(self._creases).replace('0b'))
        orders: List[Tuple] = list(permutations(range(amount_of_creases), amount_of_creases))

        return False

    def __fold_creases(self, order: List[int]):
        pass


class FoldedStrip:
    def __init__(self, strip: Strip, folds: int):
        self._strip: Strip = strip
        self._folds: int = folds

    def fold_crease(self):
        pass

    def visualize_strip(self):
        pass


def is_upside_down(x: int, y: int):
    return (y % 2 == 1) != (x % 2 == 1)


def get_triangle_coordinate(bit_string: int, start: Tuple[int, int], length: int) -> Tuple[int, int]:
    """
    Find the coordinate given a bit string (as an integer) representing folds.
    :param bit_string: The bit string representing folds
    :param start: Starting coordinate of the (static) first triangle
    :param length: The length of the strip
    :return: The coordinate of the final triangle in the strip when all folds are folded
    """
    direction: str = 'B'  # 'B'; base, 'U'; up, 'D'; down
    x_coordinate: int = start[0]
    y_coordinate: int = start[1]
    for crease in range(length):
        if bit_string & (1 << crease):  # If the ith crease is folded
            if crease % 2 == 0:
                direction = 'B' if direction == 'D' else 'D'
            else:
                direction = 'B' if direction == 'U' else 'U'
        else:
            if direction == 'B':
                x_coordinate += 1
            elif direction == 'U':
                if is_upside_down(x_coordinate, y_coordinate):
                    y_coordinate += 1
                else:
                    x_coordinate -= 1
            elif direction == 'D':
                if is_upside_down(x_coordinate, y_coordinate):
                    x_coordinate -= 1
                else:
                    y_coordinate -= 1
            else:
                raise ValueError('Direction {} does not exist'.format(direction))
    return x_coordinate, y_coordinate



