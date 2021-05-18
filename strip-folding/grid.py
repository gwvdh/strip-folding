from typing import Dict, Tuple, List
from math import sqrt
from abc import abstractmethod


def get_height(side_length: float) -> float:
    """
    Get the height of an equilateral triangle given the side lengths.

    :param side_length: The lengths of any side
    :return: The height of the triangle
    """
    return side_length * sqrt(3) / 2


class Shape:
    def __init__(self, x: int, y: int):
        self._x: int = x
        self._y: int = y
        self._score: int = 0
        self._layers: List[int] = []

    def set_score(self, score: int):
        self._score = score

    def get_score(self) -> int:
        return self._score

    def get_grid_coordinates(self):
        return self._x, self._y

    def add_layer(self, layer: int):
        self._layers.append(layer)

    @abstractmethod
    def get_coordinates(self, length: float):
        raise NotImplemented

    @abstractmethod
    def get_center(self, length: float):
        raise NotImplemented


class Triangle(Shape):
    def is_upside_down(self) -> bool:
        """
        Check whether the current triangle is upside down.

        :return: A boolean indicating if the triangle is upside down
        """
        return (self._y % 2 == 1) != (self._x % 2 == 1)

    def get_coordinates(self, length: float) -> List[Tuple[float, float]]:
        """
        Retrieve the coordinates for each of the corners of the triangle given the lengths of the sides.
        The grid coordinates are given in the object.
        The order of the corners is given in the figure below.
           2      1-----3
          / \  or  \   /
         /   \      \ /
        1-----3      2

        :param length: The lengths of any side
        :return: A tuple of coordinates for each of the corners of the triangle
        """
        height: float = get_height(side_length=length)
        upside_down: bool = self.is_upside_down()
        one = (length * float(self._x) / 2, float(self._y) * height + (height if upside_down else 0))
        two = (length * float(self._x) / 2 + length / 2, float(self._y) * height + (0 if upside_down else height))
        three = (length * float(self._x) / 2 + length, float(self._y) * height + (height if upside_down else 0))
        return [one, two, three]

    def get_center(self, length: float) -> Tuple[float, float]:
        """
        Get the center of the triangle.

        :param length: The length of any side
        :return: The coordinate of the center
        """
        height: float = get_height(side_length=length)
        base = (length * float(self._x) / 2, float(self._y) * height)
        return base[0] + length / 2, base[1] + height / 2


class Grid:
    def __init__(self, side_lengths: float = 1.0):
        self.side_lengths: float = side_lengths
        self.grid: Dict[Tuple[int, int], Shape] = {}

    def get_shape(self, x: int, y: int) -> Shape:
        return self.grid.get((x, y))

    def get_shapes(self) -> List[Shape]:
        return [shape for _, shape in self.grid.items()]

    def get_max_score(self) -> int:
        max_score: int = 0
        for _, shape in self.grid.items():
            if shape.get_score() > max_score:
                max_score = shape.get_score()
        return max_score

    @abstractmethod
    def add_shape(self, x: int, y: int, score: int = 100):
        """
        Add a shape to the data structure.
        A score is also added.

        :param x: x-coordinate
        :param y: y-coordinate
        :param score: Score representing the amount of folds
        :return:
        """
        pass

    def get_grid_shape(self) -> Tuple[int, int, int, int]:
        """
        Get the min and max coordinates of the triangle grid.
        :return: A tuple consisting of the minimum and maximum x- and y-coordinates
        """
        min_x: int = 1
        min_y: int = 1
        max_x: int = 0
        max_y: int = 0
        for (x, y), _ in self.grid.items():
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x)
            max_y = max(max_y, y)
        return min_x, min_y, max_x, max_y


class TriangleGrid(Grid):
    def __init__(self, side_lengths: float = 1.0, upside_down: bool = False):
        super().__init__(side_lengths)
        self._upside_down: bool = upside_down

    def add_shape(self, x: int, y: int, score: int = 100):
        triangle: Triangle = Triangle(x, y)
        self.grid[(x, y)] = triangle

    def add_triangle(self, x: int, y: int, score: int = 100):
        self.add_shape(x, y, score)
