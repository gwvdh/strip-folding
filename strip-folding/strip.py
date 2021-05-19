from typing import Dict, Tuple, List
from grid import TriangleGrid, Triangle, Shape
from itertools import permutations
from enum import Enum
from visualization import visualize_grid


def is_upside_down(triangle: Tuple[int, int, int]) -> bool:
    if triangle[2] - triangle[1] == triangle[0] and not (triangle[2] - triangle[1] == triangle[0] + 1 or
                                                         triangle[2] - triangle[1] == triangle[0] - 1):
        raise ValueError
    return triangle[2] - triangle[1] < triangle[0]


class Direction(Enum):
    H = 0
    N = 1
    S = 2


def next_triangle_coordinate(current_coordinate: Tuple[int, int, int], direction: Direction) -> Tuple[int, int, int]:
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
    return current_coordinate


class Face:
    def __init__(self, length: int):
        self._length: int = length
        self._coordinates: List[Tuple[int, int, int]] = []

    def set_coordinates(self, start: Tuple[int, int, int], direction: Direction) -> Tuple[int, int, int]:
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
        for i in range(self._length - 1):
            current_coordinate = next_triangle_coordinate(current_coordinate, direction)
            self._coordinates.append(current_coordinate)
        print('Length {}: {}'.format(self._length, len(self._coordinates)))
        return current_coordinate

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

    def calculate_triangles(self) -> List[Tuple[int, int]]:
        """
        Transform a three coordinate grid to a traditional grid

        :return: List of Triangles with traditional coordinates
        """
        triangles: List[Tuple[int, int]] = []
        for coordinate in self._coordinates:
            if is_upside_down(coordinate):
                triangles.append((coordinate[1] + coordinate[2] - 1, coordinate[0] - 1))
            else:
                triangles.append((coordinate[1] + coordinate[2] - 1, coordinate[0]))
        return triangles


class Strip:
    def __init__(self, faces: List[Face], creases: int):
        self._crease_amount: int = len(bin(creases).replace('0b', ''))
        self._faces: List[Face] = faces
        self._creases: int = creases
        self.initialize_faces()

    def initialize_faces(self):
        current_coordinate: Tuple[int, int, int] = (0, 0, 1)
        for face in self._faces:
            current_coordinate = face.set_coordinates(current_coordinate, Direction.H)
            current_coordinate = next_triangle_coordinate(current_coordinate, Direction.H)

    def is_simple_foldable(self) -> bool:
        orders: List[Tuple] = list(permutations(range(self._crease_amount), self._crease_amount))
        folded_strip: FoldedStrip = FoldedStrip(self, 0)
        folded_strip.visualize_strip()
        return True

    def get_faces(self) -> Tuple:
        return tuple(self._faces)

    def __fold_creases(self, order: List[int]):
        pass


class FoldedStrip:
    def __init__(self, strip: Strip, folds: int):
        self._strip: Strip = strip
        self._folds: int = folds

    def fold_crease(self):
        pass

    def visualize_strip(self):
        grid: TriangleGrid = TriangleGrid()
        for face in self._strip.get_faces():
            for triangle in face.calculate_triangles():
                if triangle in grid.grid:
                    t: Shape = grid.grid[triangle]
                    t.set_score(t.get_score() + 1)
                else:
                    grid.add_triangle(*triangle)
        visualize_grid(grid)
