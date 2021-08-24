from typing import List, Dict, Tuple
from strip import Strip, Face, get_strip_from_str
from folding_operations import Direction, FoldabilityError
from itertools import permutations


def find_all_orders(strip: str):
    pass


def is_valid_flat_folded_order(strip: str, order: List[int]):
    """
    There are 6 different orientations a crease can be in.
    Creases in the same direction can have a taco-taco intersection.
    This can also happen with creases in the opposite direction (like 0 and 3)???
    Then there can be taco-tortilla intersections which have to be detected.
       +----0----+
      /           \
    5/             \1
    /               \
    \               /
    4\             /2
      \           /
       +----3----+

    :param strip:
    :param order:
    :return:
    """
    layer_dict, creases = get_silhouette(strip)
    layer_orders: Dict[int, List[int]] = {}
    for coordinate, layers in layer_dict.items():
        if len(layers) > 1:
            crease_list: List[Tuple[Direction, int, Face]] = creases.get(coordinate, default=[])
            


def get_silhouette(strip: str):
    """
    Find the silhouette of a strip.
    The silhouette is represented by creases and triangle layers.
    A crease is represented by a coordinate and which global fold-line type it is in.
    Example: (1,0,0,Direction.N)
    :return:
    """
    strip_object: Strip = get_strip_from_str(strip)
    if strip_object.is_simple_foldable():
        layer_dict: Dict[Tuple[int, int, int], List[Face]] = strip_object.get_layers()
        creases: Dict[Tuple[int, int, int], List[Tuple[Direction, int, Face]]] = {}
        faces: Tuple[Face] = strip_object.get_faces()
        for face in faces:
            d, i = face.get_last_crease()
            last_coordinate: Tuple[int, int, int] = face.get_coordinates()[-1]
            if last_coordinate not in creases:
                creases[last_coordinate] = []
            creases[last_coordinate].append((d, i, face))
        return layer_dict, creases
    raise FoldabilityError(strip)
