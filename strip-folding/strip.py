from typing import Dict, Tuple, List
from grid import TriangleGrid, Triangle
from itertools import permutations


def is_upside_down(triangle: Tuple[int, int, int]) -> bool:
    if triangle[0] + triangle[1] - triangle[2] == 0:
        raise ValueError
    return triangle[0] + triangle[1] - triangle[2] > 0


class Direction:
    H = 0
    N = 1
    S = 2


class Face:
    def __init__(self, length: int):
        self._length: int = length
        self._coordinates: List[Tuple[int, int, int]] = []

    def set_coordinates(self, start: Tuple[int, int, int], direction: Direction):
        """
        Assign a coordinate for each triangle making up the face.
        Given is a starting coordinate of the first face. The face is facing in the direction of direction.
        We can extrapolate the remaining coordinates from the length of the face.
        Store the coordinates in self._coordinates.

        :param start: Coordinate of the first triangle of the face
        :param direction: Direction of the face
        :return:
        """
        current_coordinate: Tuple[int, int, int] = start
        self._coordinates = [current_coordinate]
        for i in range(self._length):
            if direction == Direction.H:
                if is_upside_down(current_coordinate):
                    current_coordinate = (current_coordinate[0] - 1, current_coordinate[1], current_coordinate[2] + 1)
                else:
                    current_coordinate = (current_coordinate[0] + 1, current_coordinate[1] + 1, current_coordinate[2])
            elif direction == Direction.N:
                if is_upside_down(current_coordinate):
                    current_coordinate = (current_coordinate[0], current_coordinate[1] - 1, current_coordinate[2] + 1)
                else:
                    current_coordinate = (current_coordinate[0] + 1, current_coordinate[1] + 1, current_coordinate[2])
            else:  # direction == Direction.S
                if is_upside_down(current_coordinate):
                    current_coordinate = (current_coordinate[0] - 1, current_coordinate[1], current_coordinate[2] + 1)
                else:
                    current_coordinate = (current_coordinate[0], current_coordinate[1] + 1, current_coordinate[2] - 1)
            self._coordinates.append(current_coordinate)

    def fold(self, direction: Direction, index: int):
        """
        Fold a face according to a given fold line.
        All coordinates of the face are updated according to the given fold line.

        :param direction: The direction of the fold line
        :param index: The index of the fold line
        :return:
        """
        new_coordinates: List[Tuple[int, int, int]] = []
        if direction == Direction.H:
            for coordinate in self._coordinates:
                new_coordinate: Tuple[int, int, int] = (2 * index - coordinate[0],
                                                        index - coordinate[2],
                                                        index - coordinate[1])
                new_coordinates.append(new_coordinate)
        elif direction == Direction.N:
            for coordinate in self._coordinates:
                new_coordinate: Tuple[int, int, int] = (coordinate[2] + index,
                                                        2 * index - coordinate[1],
                                                        coordinate[0] - index)
                new_coordinates.append(new_coordinate)
        elif direction == Direction.S:
            for coordinate in self._coordinates:
                new_coordinate: Tuple[int, int, int] = (coordinate[1] + index,
                                                        coordinate[0] - index,
                                                        2 * index - coordinate[2])
                new_coordinates.append(new_coordinate)
        else:
            raise ValueError
        self._coordinates = new_coordinates

    def calculate_triangles(self) -> List[Triangle]:
        pass


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
#
#
# def is_upside_down(x: int, y: int):
#     return (y % 2 == 1) != (x % 2 == 1)
#
#
# def get_triangle_coordinate(bit_string: int, start: Tuple[int, int], length: int) -> Tuple[int, int]:
#     """
#     Find the coordinate given a bit string (as an integer) representing folds.
#     :param bit_string: The bit string representing folds
#     :param start: Starting coordinate of the (static) first triangle
#     :param length: The length of the strip
#     :return: The coordinate of the final triangle in the strip when all folds are folded
#     """
#     direction: str = 'B'  # 'B'; base, 'U'; up, 'D'; down
#     x_coordinate: int = start[0]
#     y_coordinate: int = start[1]
#     for crease in range(length):
#         if bit_string & (1 << crease):  # If the ith crease is folded
#             if crease % 2 == 0:
#                 direction = 'B' if direction == 'D' else 'D'
#             else:
#                 direction = 'B' if direction == 'U' else 'U'
#         else:
#             if direction == 'B':
#                 x_coordinate += 1
#             elif direction == 'U':
#                 if is_upside_down(x_coordinate, y_coordinate):
#                     y_coordinate += 1
#                 else:
#                     x_coordinate -= 1
#             elif direction == 'D':
#                 if is_upside_down(x_coordinate, y_coordinate):
#                     x_coordinate -= 1
#                 else:
#                     y_coordinate -= 1
#             else:
#                 raise ValueError('Direction {} does not exist'.format(direction))
#     return x_coordinate, y_coordinate
#


