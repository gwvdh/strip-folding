from typing import Tuple, List, Dict
from grid import TriangleGrid, Shape
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
    """
    Get the coordinates for the next triangle given the current_coordinate and the direction.

    :param current_coordinate: The current coordinate
    :param direction: The direction in which the next triangle is
    :return: The next triangle from the current_coordinate in the given direction
    """
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
    def __init__(self, length: int, direction: Direction = Direction.H):
        self._length: int = length
        self._direction: Direction = direction
        self._coordinates: List[Tuple[int, int, int]] = []

    def get_direction(self) -> Direction:
        return self._direction

    def get_last_crease(self) -> Tuple[Direction, int]:
        last_tuple: Tuple[int, int, int] = self._coordinates[-1]
        if self._direction == Direction.H:
            # H + N = S
            if last_tuple[2] - last_tuple[0] > last_tuple[1]:
                return Direction.S, last_tuple[2]
            elif last_tuple[0] + last_tuple[1] > last_tuple[2]:
                return Direction.N, last_tuple[1]
            else:
                raise Exception('Incorrect crease coordinate: {}'.format(last_tuple))
        elif self._direction == Direction.N:
            # H + N = S
            if last_tuple[2] - last_tuple[1] > last_tuple[0]:
                return Direction.H, last_tuple[0]
            elif last_tuple[0] + last_tuple[1] > last_tuple[2]:
                return Direction.S, last_tuple[2]
            else:
                raise Exception('Incorrect crease coordinate: {}'.format(last_tuple))
        elif self._direction == Direction.S:
            # H + N = S
            if last_tuple[2] - last_tuple[1] > last_tuple[0]:
                return Direction.N, last_tuple[1]
            elif last_tuple[0] + last_tuple[1] > last_tuple[2]:
                return Direction.H, last_tuple[0]
            else:
                raise Exception('Incorrect crease coordinate: {}'.format(last_tuple))
        else:
            raise Exception

    def set_absolute_coordinates(self, coordinates: List[Tuple[int, int, int]]):
        self._coordinates = coordinates

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
        return current_coordinate

    def get_coordinates(self) -> List[Tuple[int, int, int]]:
        return self._coordinates

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
                                                        coordinate[2] - index,
                                                        index + coordinate[1])
                new_coordinates.append(new_coordinate)
            if self._direction == Direction.N:
                self._direction = Direction.S
            elif self._direction == Direction.S:
                self._direction = Direction.N
        elif direction == Direction.N:
            for coordinate in self._coordinates:
                new_coordinate: Tuple[int, int, int] = (coordinate[2] - index,
                                                        2 * index - coordinate[1],
                                                        coordinate[0] + index)
                new_coordinates.append(new_coordinate)
            if self._direction == Direction.H:
                self._direction = Direction.S
            elif self._direction == Direction.S:
                self._direction = Direction.H
        elif direction == Direction.S:
            for coordinate in self._coordinates:
                new_coordinate: Tuple[int, int, int] = (index - coordinate[1],
                                                        index - coordinate[0],
                                                        2 * index - coordinate[2])
                new_coordinates.append(new_coordinate)
            if self._direction == Direction.N:
                self._direction = Direction.H
            elif self._direction == Direction.H:
                self._direction = Direction.N
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


def coordinate_greater_than_crease(coordinate: Tuple[int, int, int], global_crease: Tuple[Direction, int]) -> bool:
    crease_direction, crease_index = global_crease
    if crease_direction == Direction.H:
        if coordinate[0] != crease_index:
            return coordinate[0] > crease_index
        # Else: H = S - N
        return coordinate[2] - coordinate[1] > crease_index
    elif crease_direction == Direction.N:
        if coordinate[1] != crease_index:
            return coordinate[1] > crease_index
        # Else: N = S - H
        return coordinate[2] - coordinate[0] > crease_index
    elif crease_direction == Direction.S:
        if coordinate[2] != crease_index:
            return coordinate[2] > crease_index
        # Else: S = H + N
        return coordinate[0] + coordinate[1] > crease_index
    else:
        raise Exception('Invalid crease direction: {}'.format(crease_direction))


def coordinate_folds_up(coordinate: Tuple[int, int, int],
                        global_crease: Tuple[Direction, int],
                        is_mountain_fold: bool,
                        face: Face) -> bool:
    face_direction: Direction = face.get_direction()
    crease_direction, crease_index = global_crease
    cgc: bool = coordinate_greater_than_crease(coordinate, global_crease)
    if crease_direction == Direction.H:
        if face_direction == Direction.N:
            return cgc != is_mountain_fold
        elif face_direction == Direction.S:
            return cgc == is_mountain_fold
        else:
            raise Exception('Invalid face direction: {}'.format(crease_direction))
    elif crease_direction == Direction.N:
        if face_direction == Direction.H:
            return cgc != is_mountain_fold
        elif face_direction == Direction.S:
            return cgc == is_mountain_fold
        else:
            raise Exception('Invalid face direction: {}'.format(crease_direction))
    elif crease_direction == Direction.S:
        if face_direction == Direction.H:
            return cgc != is_mountain_fold
        elif face_direction == Direction.N:
            return cgc == is_mountain_fold
        else:
            raise Exception('Invalid face direction: {}'.format(crease_direction))
    else:
        raise Exception('Invalid crease direction: {}'.format(crease_direction))


class Strip:
    def __init__(self, faces: List[Face], creases: int, folds: int, crease_amount: int):
        self._crease_amount: int = crease_amount
        self._faces: List[Face] = faces
        self._creases: int = creases
        self._folds: int = folds
        self._layers: Dict[Tuple[int, int, int], List[Face]] = {}
        self.initialize_faces()

    def initialize_faces(self):
        """
        Initialize the coordinates of the faces.

        :return:
        """
        current_coordinate: Tuple[int, int, int] = (0, 0, 1)
        for face in self._faces:
            current_coordinate = face.set_coordinates(current_coordinate, Direction.H)
            current_coordinate = next_triangle_coordinate(current_coordinate, Direction.H)
            for triangle in face.get_coordinates():
                if triangle not in self._layers:
                    self._layers[triangle] = []
                self._layers[triangle].append(face)

    def is_simple_foldable(self) -> bool:
        self.visualize_strip()
        return True

    def __is_foldable_coordinate(self,
                                 coordinate: Tuple[int, int, int],
                                 up: bool,
                                 face: Face) -> bool:
        """
        Given a coordinate, is it foldable in the given direction.

        :param coordinate:
        :param up:
        :param face:
        :return:
        """
        if face not in self._layers[coordinate]:
            raise Exception('Coordinate not in a layer: {}'.format(coordinate))
        return (up and self._layers[coordinate][-1] == face) or \
               (not up and self._layers[coordinate][0] == face)

    def __crease_is_simple_foldable(self, index: int) -> bool:
        """
        Can the given crease be simple folded?

        :param index: Index of the crease
        :return: Whether the crease can be simple folded
        """
        m_or_v: int = self._creases & (1 << index)
        global_crease: Tuple[Direction, int] = self.get_global_crease(index)
        for face in range(index + 1, len(self._faces)):
            for coordinate in self._faces[face].get_coordinates():
                face_object: Face = self._faces[face]
                up: bool = coordinate_folds_up(coordinate, global_crease, bool(m_or_v), face_object)
                if not self.__is_foldable_coordinate(coordinate, up, face_object):
                    return False
        return True

    def fold_crease(self, index: int):
        """
        Fold the crease at index.
        We fold the crease and transform all subsequent faces which are affected by the fold.

        :param index: The index of the crease
        :return:
        """
        if index >= self._crease_amount:
            raise ValueError('Invalid crease index: {} out of {}'.format(index, self._crease_amount))
        if self._folds & (1 << index):
            raise Exception('Crease is already folded')
        crease: Tuple[Direction, int] = self.get_global_crease(index)
        for face in range(index + 1, len(self._faces)):
            self._faces[face].fold(*crease)
        # Flip crease bit
        self._folds = self._folds ^ (1 << index)

    def get_global_crease(self, index: int) -> Tuple[Direction, int]:
        """
        Get the global fold line of the crease at index.
        From the strip, get the crease at index and return the direction and index of the global crease.

        :param index: The index of the crease
        :return: Global fold line direction and index
        """
        if not (self._folds & (1 << index)):
            return self._faces[index].get_last_crease()
        raise Exception('Crease is already folded')

    def get_faces(self) -> Tuple:
        return tuple(self._faces)

    def __fold_creases(self, order: List[int]):
        pass

    def visualize_strip(self):
        """
        Visualize the strip.

        :return:
        """
        grid: TriangleGrid = TriangleGrid()
        for face in self.get_faces():
            for triangle in face.calculate_triangles():
                if triangle in grid.grid:
                    t: Shape = grid.grid[triangle]
                    t.set_score(t.get_score() + 1)
                else:
                    grid.add_triangle(*triangle)
        visualize_grid(grid)
