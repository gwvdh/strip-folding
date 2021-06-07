from typing import Tuple
from enum import Enum


class FoldabilityError(Exception):
    """Base class for foldability exceptions"""
    pass


class Direction(Enum):
    H = 0
    N = 1
    S = 2


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
                        face_direction: Direction) -> bool:
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
    :param face_direction: the direction of the face of the global crease
    :return: boolean whether the coordinate folds up
    """
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
            raise Exception('Invalid face direction: {}'.format(face_direction))
    elif crease_direction == Direction.S:
        if face_direction == Direction.H:
            return cgc != is_mountain_fold
        elif face_direction == Direction.N:
            return cgc == is_mountain_fold
        else:
            raise Exception('Invalid face direction: {}'.format(face_direction))
    else:
        raise Exception('Invalid crease direction: {}'.format(crease_direction))
