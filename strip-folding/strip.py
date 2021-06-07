from typing import Tuple, List, Dict
from grid import TriangleGrid, Shape
from itertools import permutations
from enum import Enum
from visualization import visualize_grid
import random
from functools import reduce


class FoldabilityError(Exception):
    """Base class for foldability exceptions"""
    pass


def transform_coordinate(coordinate: Tuple[int, int, int]) -> Tuple[int, int]:
    """
    Transform a coordinate.
    This is a transformation from global fold line coordinate system to a traditional 2d x,y system.

    :param coordinate: the coordinate in global fold line coordinate system
    :return: 2d x,y coordinates of the given coordinate
    """
    if is_upside_down(coordinate):
        return coordinate[1] + coordinate[2] - 1, coordinate[0] - 1
    else:
        return coordinate[1] + coordinate[2] - 1, coordinate[0]


def is_upside_down(triangle: Tuple[int, int, int]) -> bool:
    """
    Check if a triangle is upside down.
    Check if the horizontal fold line is above the other fold lines.

    :param triangle: the given triangle
    :return: boolean whether the given triangle is upside down
    """
    if triangle[2] - triangle[1] == triangle[0] and not (triangle[2] - triangle[1] == triangle[0] + 1 or
                                                         triangle[2] - triangle[1] == triangle[0] - 1):
        raise ValueError
    return triangle[2] - triangle[1] < triangle[0]


class Direction(Enum):
    H = 0
    N = 1
    S = 2


def reduce_int_list(ls: List[int]) -> str:
    order_string: str = reduce(lambda a, b: a + f'{b}|', ls, '')
    return order_string[:-1]


def next_triangle_coordinate(current_coordinate: Tuple[int, int, int], direction: Direction) -> Tuple[int, int, int]:
    """
    Get the coordinates for the next triangle given the current_coordinate and the direction.

    :param current_coordinate: the current coordinate
    :param direction: the direction in which the next triangle is
    :return: the next triangle from the current_coordinate in the given direction
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
    """
    Fold a given coordinate.
    Given a coordinate to be folded and a global fold line, fold the given coordinate around this fold line.
    In this coordinate system we can find this by a simple transformation.

    :param coordinate: The given coordinate to fold
    :param direction: The direction of the global fold line
    :param index: The index of the global fold line
    :return: The coordinate of the folded triangle
    """
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

    def get_length(self) -> int:
        return self._length

    def get_last_crease(self) -> Tuple[Direction, int]:
        """
        Get the global crease of the last triangle of this face

        :return: Direction and index of the global crease of this face
        """
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
        self._direction = direction
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
            triangles.append(transform_coordinate(coordinate))
        return triangles


def coordinate_greater_than_crease(coordinate: Tuple[int, int, int], global_crease: Tuple[Direction, int]) -> bool:
    """
    Given a global crease, check if the same direction crease in the coordinate is greater.
    Every coordinate consists of the three global fold line directions of some index.
    Check if the fold line in the coordinate is greater than the given one.

    :param coordinate: Given coordinate
    :param global_crease: Given the crease as a direction and index
    :return: A boolean whether the given coordinate is greater than the given crease.
    """
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
    """
    Check whether a given coordinate folds up.
    If a crease is folded, the relative position of a coordinate to that crease
    determines whether the coordinate folds up or down.
    The crease is either mountain or valley.
    The direction of the face containing the coordinate influences the direction
    since it influences which side of the crease is up or down with respect to the crease being mountain or valley.

    :param coordinate: the given coordinate
    :param global_crease: the global crease
    :param is_mountain_fold: boolean whether global_crease is a mountain or valley fold
    :param face: the face of the global crease
    :return: boolean whether the coordinate folds up
    """
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
        self._creases_base: int = creases
        self._folds: int = folds
        self._folds_base: int = folds
        self._layers: Dict[Tuple[int, int, int], List[Face]] = {}
        self._db = {}
        self.initialize_faces()

    def get_length(self) -> int:
        length = 0
        for face in self._faces:
            length += face.get_length()
        return length

    def get_crease_amount(self) -> int:
        return self._crease_amount

    def get_original_creases(self) -> int:
        return self._creases_base

    def get_original_folds(self) -> int:
        return self._folds_base

    def get_n_mountain_folds(self) -> int:
        return bin(self._creases_base).count('1')

    def get_db(self):
        return self._db

    def set_db(self, db):
        self._db = db

    def get_strip_string(self) -> str:
        result: str = ''
        for face_index in range(len(self._faces)):
            result = result + str(self._faces[face_index].get_length())
            if face_index != len(self._faces) - 1:
                if self._creases_base & (1 << face_index):
                    result = result + 'M'
                else:
                    result = result + 'V'
        return result

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

    def reset_strip(self):
        self._creases = self._creases_base
        self._folds = self._folds_base
        self._layers = {}
        self.initialize_faces()

    def _add_strip_to_database(self, order: List[int]):
        """
        Add the strip order to the database.
        Database is structures as (for coordinate (0, 0, 1) with order [1, 2, 3] with face order [1,2,3,4]):
        { '0|0|1': {'1|2|3': '1|2|3|4'} }

        :param order: order in which the creases are folded
        :return:
        """
        self.sanitize_layers()
        order_string: str = reduce_int_list(order)
        for coord, faces in self._layers.items():
            coordinate: str = f'{coord[0]}|{coord[1]}|{coord[2]}'
            if coordinate not in self._db:
                self._db[coordinate] = {
                    order_string: reduce_int_list([self._faces.index(face) for face in faces])
                }
            else:
                self._db[coordinate][order_string] = reduce_int_list([self._faces.index(face) for face in faces])

    def all_simple_folds(self) -> bool:
        """
        Go over all possible orders in which to fold this strip and add it to the database

        :return:
        """
        orders: List[int] = list(range(0, self._crease_amount))
        random.shuffle(orders)
        found_valid_foldable_order: bool = False
        for order in permutations(orders):
            self.reset_strip()
            if self.is_simple_foldable_order(list(order), visualization=False):
                self._add_strip_to_database(list(order))
                found_valid_foldable_order = True
                pass
        return found_valid_foldable_order

    def sanitize_layers(self):
        self._layers = {k: v for k, v in self._layers.items() if len(v) > 0}

    def is_simple_foldable(self, visualization: bool = False, animate: bool = False) -> bool:
        """
        Check whether the strip is simple foldable.
        Randomly get some order and check whether it is simple foldable.
        This does not guarantee a correct answer.
        Remove randomization to go brute force for a real answer.


        :param visualization: Whether we want to visualize the strip
        :param animate: Whether we want to animate the folding sequence
        :return: boolean whether the strip is simple foldable
        """
        # orders = list(permutations(range(0, self._crease_amount)))
        orders: List[int] = list(range(0, self._crease_amount))
        for order in permutations(orders):
            random.shuffle(orders) # Remove this to find a definitive answer
            self.reset_strip()
            if self.is_simple_foldable_order(list(orders), visualization=False):
                if visualization:
                    print(self.get_strip_string())
                    print('Found valid order: {}'.format(list(orders)))
                    # self.visualize_strip(name=self.get_strip_string())
                if animate:
                    self.reset_strip()
                    self.is_simple_foldable_order(list(orders), animate=True)
                self.sanitize_layers()
                self._add_strip_to_database(orders)
                return True
        print('No valid order: {}'.format(self.get_strip_string()))
        self.sanitize_layers()
        return False

    def is_simple_foldable_order(self, crease_order: List[int],
                                 visualization: bool = True, animate: bool = False) -> bool:
        """
        Check whether the given folding order of the creases is valid for simple folding.

        :param crease_order: The order in which to fold the creases
        :param visualization: Whether we want to visualize the strip
        :param animate: Whether we want to animate the folding sequence
        :return:
        """
        for i in range(self._crease_amount):
            if i not in crease_order:
                raise ValueError('No complete order given: Missing {}'.format(i))
        for crease in crease_order:
            try:
                if animate:
                    self.visualize_strip(name=self.get_strip_string()+'_{}'.format(crease_order.index(crease)))
                self.simple_fold_crease(crease)
            except FoldabilityError:
                return False
        if visualization:
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
        """
        Get the layers which are to be folded for the given coordinate.
        Find the faces which will fold in the given direction.
        We assume this is possible, otherwise we raise an exception.

        :param coordinate: the coordinate to be folded
        :param crease_index: the index of the crease (to find subsequent faces)
        :param up: whether the coordinate folds up or down
        :return: a list of faces which are folded
        """
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

    def __fold_layer_ordering(self,
                              coordinate,
                              folded_coordinate,
                              crease_index: int,
                              up: bool,
                              folded_coordinate_exists: bool):
        """
        Fold the layers to the new coordinate.

        :param coordinate: the coordinate to be folded
        :param folded_coordinate: the coordinate of the folded location
        :param crease_index: the index of the folded crease
        :param up: boolean whether the coordinate is folded up or down
        :param folded_coordinate_exists: boolean indicating the existence of the folded coordinate
        :return: 
        """
        if folded_coordinate_exists:
            layers_1: List[Face] = self.get_folding_layers(coordinate, crease_index, up)
            layers_2: List[Face] = self.get_folding_layers(folded_coordinate, crease_index, not up)
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
            layers_1: List[Face] = self.get_folding_layers(coordinate, crease_index, up)
            # Remove current layers form current and folded coordinate
            for face in layers_1:
                self._layers[coordinate].remove(face)
            # Add current and folded coordinate to visited list
            layers_1.reverse()
            if folded_coordinate not in self._layers:
                self._layers[folded_coordinate] = []
            if up:
                self._layers[folded_coordinate].extend(layers_1)
            else:
                self._layers[folded_coordinate] = layers_1 + self._layers[folded_coordinate]

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

                if not self.__is_foldable_coordinate(coordinate, up, index + 1):
                    raise FoldabilityError('Crease not simple foldable: crease {}'.format(index))
                folded_coordinate_exists: bool = folded_coordinate in all_coordinates
                if folded_coordinate_exists and not self.__is_foldable_coordinate(folded_coordinate, not up, index + 1):
                    raise FoldabilityError('Crease not simple foldable: crease {}'.format(index))
                #
                # Add the coordinates to the visited list
                visited_coordinates.append(coordinate)
                visited_coordinates.append(folded_coordinate)
                #
                # Put layers in the correct order in the folded coordinate
                #   If the folded coordinate already existed, also do it for the folded coordinate to current coordinate
                self.__fold_layer_ordering(coordinate, folded_coordinate, index, up, folded_coordinate_exists)
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

    def visualize_strip(self, name: str = 'visualization'):
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
        visualize_grid(grid, file_name=name)
