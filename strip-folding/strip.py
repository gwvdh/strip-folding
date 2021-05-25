from typing import Tuple, List, Dict, Set
from grid import TriangleGrid, Shape
from itertools import permutations
from enum import Enum
from visualization import visualize_grid


class FoldabilityError(Exception):
    """Base class for foldability exceptions"""
    pass


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


def fold_coordinate(coordinate: Tuple[int, int, int], direction: Direction, index: int) -> Tuple[int, int, int]:
    if direction == Direction.H:
        return 2 * index - coordinate[0], coordinate[2] - index, index + coordinate[1]
    elif direction == Direction.N:
        return coordinate[2] - index, 2 * index - coordinate[1],  coordinate[0] + index
    elif direction == Direction.S:
        return index - coordinate[1], index - coordinate[0], 2 * index - coordinate[2]
    else:
        raise Exception('Incorrect crease direction: {}'.format(direction))


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
        for coordinate in self._coordinates:
            new_coordinate: Tuple[int, int, int] = fold_coordinate(coordinate, direction, index)
            new_coordinates.append(new_coordinate)
        if direction == Direction.H:
            if self._direction == Direction.N:
                self._direction = Direction.S
            elif self._direction == Direction.S:
                self._direction = Direction.N
        elif direction == Direction.N:
            if self._direction == Direction.H:
                self._direction = Direction.S
            elif self._direction == Direction.S:
                self._direction = Direction.H
        elif direction == Direction.S:
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
            return cgc == is_mountain_fold
        elif face_direction == Direction.S:
            return cgc != is_mountain_fold
        else:
            raise Exception('Invalid face direction: {}'.format(face_direction))
    elif crease_direction == Direction.N:
        if face_direction == Direction.H:
            return cgc != is_mountain_fold
        elif face_direction == Direction.S:
            return cgc == is_mountain_fold
        else:
            raise Exception('Invalid face {} direction: {}'.format(face, face_direction))
    elif crease_direction == Direction.S:
        if face_direction == Direction.H:
            return cgc != is_mountain_fold
        elif face_direction == Direction.N:
            return cgc == is_mountain_fold
        else:
            raise Exception('Invalid face direction: {}'.format(face_direction))
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

    def is_simple_foldable_order(self, crease_order: List[int]) -> bool:
        for i in range(self._crease_amount):
            if i not in crease_order:
                raise ValueError('No complete order given: Missing {}'.format(i))
        for crease in crease_order:
            try:
                self.simple_fold_crease(crease)
            except FoldabilityError:
                return False
        self.visualize_strip()
        return True

    def __is_foldable_coordinate(self,
                                 coordinate: Tuple[int, int, int],
                                 up: bool,
                                 face_index: int) -> bool:
        """
        Given a coordinate, is it foldable in the given direction.

        :param coordinate:
        :param up:
        :param face_index:
        :return:
        """
        layers: List[Face] = self._layers[coordinate]
        iterable = reversed(range(len(layers))) if up else range(len(layers))
        obstructed: bool = False
        for layer_face in iterable:
            if self._faces.index(layers[layer_face]) < face_index:
                obstructed = True
            if obstructed and self._faces.index(layers[layer_face]) >= face_index:
                return False
        return True

    def __crease_is_simple_foldable(self, index: int) -> bool:
        """
        Can the given crease be simple folded?

        :param index: Index of the crease
        :return: Whether the crease can be simple folded
        """
        m_or_v: int = self._creases & (1 << index)
        global_crease: Tuple[Direction, int] = self.get_global_crease(index)
        face_object: Face = self._faces[index + 1]
        for face in range(index + 1, len(self._faces)):
            for coordinate in self._faces[face].get_coordinates():
                up: bool = coordinate_folds_up(coordinate, global_crease, bool(m_or_v), face_object)
                if not self.__is_foldable_coordinate(coordinate, up, index + 1):
                    return False
        return True

    def __get_all_subsequent_face_coordinates(self, face_index: int) -> List[Tuple[int, int, int]]:
        """
        Get all coordinates which are from a given face or subsequent faces.

        :param face_index:
        :return:
        """
        coordinates: List[Tuple[int, int, int]] = []
        for face_i in range(face_index, len(self._faces)):
            coordinates.extend(self._faces[face_i].get_coordinates())
        return list(dict.fromkeys(coordinates))

    def get_folding_layers(self, coordinate: Tuple[int, int, int], crease_index: int, up: bool) -> List[Face]:
        layers: List[Face] = self._layers[coordinate]
        if len(layers) == 0:
            raise Exception('No layers: {}'.format(layers))
        folding_layers: List[Face] = []
        if up:
            if self._faces.index(layers[-1]) <= crease_index:
                raise Exception('Not foldable')
            for layer in reversed(range(len(layers))):
                if self._faces.index(layers[layer]) <= crease_index:
                    folding_layers.reverse()
                    return folding_layers
                folding_layers.append(layers[layer])
            folding_layers.reverse()
            return folding_layers
        else:
            if self._faces.index(layers[0]) <= crease_index:
                raise Exception('Not foldable')
            for layer in range(len(layers)):
                if self._faces.index(layers[layer]) <= crease_index:
                    return folding_layers
                folding_layers.append(layers[layer])
            return folding_layers

    def simple_fold_crease(self, index: int):
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
        if not self.__crease_is_simple_foldable(index):
            raise FoldabilityError('Crease not simple foldable: crease {}'.format(index))
        # print('Faces: {}'.format(self._faces))
        m_or_v: int = self._creases & (1 << index)
        all_coordinates: List[Tuple[int, int, int]] = self.__get_all_subsequent_face_coordinates(index + 1)
        visited_coordinates: List[Tuple[int, int, int]] = []
        crease: Tuple[Direction, int] = self.get_global_crease(index)
        for coordinate in all_coordinates:
            # Check if we have not already visited this coordinate
            if coordinate not in visited_coordinates:
                # Find the folded coordinate
                folded_coordinate: Tuple[int, int, int] = fold_coordinate(coordinate, *crease)
                up: bool = coordinate_folds_up(coordinate, crease, bool(m_or_v), self._faces[index + 1])
                # Add the coordinates to the visited list
                visited_coordinates.append(coordinate)
                visited_coordinates.append(folded_coordinate)
                # Put layers in the correct order in the folded coordinate
                #   If the folded coordinate already existed, also do it for the folded coordinate to current coordinate
                if folded_coordinate in all_coordinates:
                    layers_1: List[Face] = self.get_folding_layers(coordinate, index, up)
                    layers_2: List[Face] = self.get_folding_layers(folded_coordinate, index, not up)
                    # Remove current layers form current and folded coordinate
                    for face in layers_1:
                        self._layers[coordinate].remove(face)
                    for face in layers_2:
                        self._layers[folded_coordinate].remove(face)
                    # Add current and folded coordinate to visited list
                    layers_1.reverse()
                    layers_2.reverse()
                    if up:
                        self._layers[folded_coordinate].extend(layers_1)
                        self._layers[coordinate] = layers_2 + self._layers[coordinate]
                    else:
                        self._layers[folded_coordinate] = layers_1 + self._layers[folded_coordinate]
                        self._layers[coordinate].extend(layers_2)
                else:
                    # print('Layer check One {}: {}'.format(coordinate, self._layers.get(coordinate, [])))
                    # print('Layer check One {}: {}'.format(folded_coordinate, self._layers.get(folded_coordinate, [])))
                    layers_1: List[Face] = self.get_folding_layers(coordinate, index, up)
                    # Remove current layers form current and folded coordinate
                    for face in layers_1:
                        self._layers[coordinate].remove(face)
                    # print('Layer check Two {}: {}'.format(coordinate, self._layers.get(coordinate, [])))
                    # print('Layer check Two {}: {}'.format(folded_coordinate, self._layers.get(folded_coordinate, [])))
                    # Add current and folded coordinate to visited list
                    layers_1.reverse()
                    if folded_coordinate not in self._layers:
                        self._layers[folded_coordinate] = []
                    if up:
                        self._layers[folded_coordinate].extend(layers_1)
                    else:
                        self._layers[folded_coordinate] = layers_1 + self._layers[folded_coordinate]
                    # print('Layer check Three {}: {}'.format(coordinate, self._layers.get(coordinate, [])))
                    # print('Layer check Three {}: {}'.format(folded_coordinate, self._layers.get(folded_coordinate, [])))
        # Fold the faces
        for face_i in range(index + 1, len(self._faces)):
            self._faces[face_i].fold(*crease)
        # Flip crease bit
        self._folds = self._folds ^ (1 << index)
        # Flip mountain valley assignments after folded crease
        for i in range(index + 1, self._crease_amount):
            self._creases = self._creases ^ (1 << i)
        # print('--------- End of fold ---------')
        # -----------------------------

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
