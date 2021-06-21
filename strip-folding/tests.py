import unittest
from typing import List, Tuple
from strip import Strip, Face
from data_processing import calculate_all_folds, analyze_states, \
    analyze_database, fold_least_crease, \
    get_strip_from_str, visualize_order_amount, calculate_all_folds_strip_length, \
    test_if_consecutive_exists, find_any_cycle, analyze_same_crease_patterns
from folding_operations import is_upside_down, Direction, coordinate_folds_up
from data_visualization import random_simple_foldable
import random


class MethodTests(unittest.TestCase):
    def test_upside_down(self):
        with self.assertRaises(ValueError):
            is_upside_down((0, 0, 0))
        self.assertTrue(is_upside_down((1, 0, 0)))
        self.assertTrue(is_upside_down((1, 1, 1)))
        self.assertTrue(is_upside_down((0, 1, 0)))
        self.assertFalse(is_upside_down((0, 0, 1)))
        self.assertFalse(is_upside_down((-1, 1, 1)))


class VisualizationTests(unittest.TestCase):
    def test_strip_visualization(self):
        f1: Face = Face(5)
        faces: List[Face] = [Face(3), Face(4), Face(1), Face(1), f1]
        creases: int = int('1000', 2)
        folds: int = int('0000', 2)
        strip: Strip = Strip(faces, creases, folds)
        f1.fold(Direction.S, 5)
        f1.fold(Direction.H, 0)
        self.assertTrue(strip.is_simple_foldable())

    def test_strip_crease_folds(self):
        amount_of_faces: int = 10
        faces: List[Face] = [Face(random.randint(1, 10)) for i in range(amount_of_faces)]
        creases: int = int('0000', 2)
        folds: int = int('0000', 2)
        strip: Strip = Strip(faces, creases, folds, amount_of_faces-1)
        for i in range(amount_of_faces-1):
            if random.randint(1, 2) == 2 or True:
                strip.fold_crease(i)
        self.assertTrue(strip.is_simple_foldable())

    def test_coordinate_direction(self):
        face: Face = Face(10, Direction.H)
        coordinate_1: Tuple[int, int, int] = (0, 0, 1)
        coordinate_h: Tuple[int, int, int] = (0, 1, 0)
        global_crease_h: Tuple[Direction, int] = (Direction.H, 0)
        is_mountain_fold: bool = True
        with self.assertRaises(Exception):
            coordinate_folds_up(coordinate_1, global_crease_h, is_mountain_fold, face.get_direction())
        face = Face(10, Direction.N)
        # Horizontal crease
        self.assertTrue(coordinate_folds_up(coordinate_1, global_crease_h, is_mountain_fold, face.get_direction()))
        self.assertFalse(coordinate_folds_up(coordinate_h, global_crease_h, is_mountain_fold, face.get_direction()))
        is_mountain_fold: bool = False
        self.assertFalse(coordinate_folds_up(coordinate_1, global_crease_h, is_mountain_fold, face.get_direction()))
        self.assertTrue(coordinate_folds_up(coordinate_h, global_crease_h, is_mountain_fold, face.get_direction()))
        face = Face(10, Direction.S)
        self.assertTrue(coordinate_folds_up(coordinate_1, global_crease_h, is_mountain_fold, face.get_direction()))
        self.assertFalse(coordinate_folds_up(coordinate_h, global_crease_h, is_mountain_fold, face.get_direction()))
        is_mountain_fold: bool = True
        self.assertFalse(coordinate_folds_up(coordinate_1, global_crease_h, is_mountain_fold, face.get_direction()))
        self.assertTrue(coordinate_folds_up(coordinate_h, global_crease_h, is_mountain_fold, face.get_direction()))
        # North crease
        face = Face(10, Direction.N)
        global_crease_n: Tuple[Direction, int] = (Direction.N, 0)
        coordinate_n: Tuple[int, int, int] = (1, 0, 0)
        is_mountain_fold: bool = True
        with self.assertRaises(Exception):
            coordinate_folds_up(coordinate_1, global_crease_n, is_mountain_fold, face.get_direction())
        face = Face(10, Direction.H)
        self.assertFalse(coordinate_folds_up(coordinate_1, global_crease_n, is_mountain_fold, face.get_direction()))
        self.assertTrue(coordinate_folds_up(coordinate_n, global_crease_n, is_mountain_fold, face.get_direction()))
        is_mountain_fold: bool = False
        self.assertTrue(coordinate_folds_up(coordinate_1, global_crease_n, is_mountain_fold, face.get_direction()))
        self.assertFalse(coordinate_folds_up(coordinate_n, global_crease_n, is_mountain_fold, face.get_direction()))
        face = Face(10, Direction.S)
        self.assertFalse(coordinate_folds_up(coordinate_1, global_crease_n, is_mountain_fold, face.get_direction()))
        self.assertTrue(coordinate_folds_up(coordinate_n, global_crease_n, is_mountain_fold, face.get_direction()))
        is_mountain_fold: bool = True
        self.assertTrue(coordinate_folds_up(coordinate_1, global_crease_n, is_mountain_fold, face.get_direction()))
        self.assertFalse(coordinate_folds_up(coordinate_n, global_crease_n, is_mountain_fold, face.get_direction()))
        # South crease
        face = Face(10, Direction.S)
        global_crease_s: Tuple[Direction, int] = (Direction.S, 0)
        coordinate_s: Tuple[int, int, int] = (-1, 0, 0)
        is_mountain_fold: bool = True
        with self.assertRaises(Exception):
            coordinate_folds_up(coordinate_h, global_crease_s, is_mountain_fold, face.get_direction())
        face = Face(10, Direction.H)
        self.assertFalse(coordinate_folds_up(coordinate_h, global_crease_s, is_mountain_fold, face.get_direction()))
        self.assertTrue(coordinate_folds_up(coordinate_s, global_crease_s, is_mountain_fold, face.get_direction()))
        is_mountain_fold: bool = False
        self.assertTrue(coordinate_folds_up(coordinate_h, global_crease_s, is_mountain_fold, face.get_direction()))
        self.assertFalse(coordinate_folds_up(coordinate_s, global_crease_s, is_mountain_fold, face.get_direction()))
        face = Face(10, Direction.N)
        self.assertFalse(coordinate_folds_up(coordinate_h, global_crease_s, is_mountain_fold, face.get_direction()))
        self.assertTrue(coordinate_folds_up(coordinate_s, global_crease_s, is_mountain_fold, face.get_direction()))
        is_mountain_fold: bool = True
        self.assertTrue(coordinate_folds_up(coordinate_h, global_crease_s, is_mountain_fold, face.get_direction()))
        self.assertFalse(coordinate_folds_up(coordinate_s, global_crease_s, is_mountain_fold, face.get_direction()))

    def test_simple_foldable_order(self):
        faces: List[Face] = [Face(2), Face(1), Face(1), Face(1)]
        creases: int = int('110', 2)
        folds: int = int('000', 2)
        strip: Strip = Strip(faces, creases, folds, 3)
        self.assertFalse(strip.is_simple_foldable_order([0, 1, 2]))
        faces: List[Face] = [Face(2), Face(1), Face(1), Face(1)]
        strip: Strip = Strip(faces, creases, folds, 3)
        self.assertTrue(strip.is_simple_foldable_order([1, 2, 0]))
        creases: int = int('001', 2)
        faces: List[Face] = [Face(2), Face(1), Face(1), Face(1)]
        strip: Strip = Strip(faces, creases, folds, 3)
        self.assertFalse(strip.is_simple_foldable_order([0, 1, 2]))

    def test_simple_foldable_generator(self):
        amount_of_faces: int = 10
        max_face_length: int = 5
        iterations: int = 1000
        for i in range(iterations):
            faces: List[Face] = []
            for face in range(amount_of_faces):
                faces.append(Face(random.randint(1, max_face_length)))
            strip: Strip = Strip(faces, random.randint(0, 2**(amount_of_faces - 1)), 0, amount_of_faces - 1)
            self.assertTrue(strip.is_simple_foldable(visualization=True, animate=False))
            print('{}/{}'.format(i, iterations))

    def test_all_strips(self):
        self.assertTrue(calculate_all_folds())

    def test_all_strips_by_length(self):
        self.assertTrue(calculate_all_folds_strip_length())

    def test_data_visualization(self):
        strip_length: int = 49
        strip: str = f'{random.randint(1, 9)}'
        for i in range(strip_length):
            strip += f'{random.choice(["M", "V"])}{random.randint(1, 9)}'
        print(f'Try string: {strip}')
        # strip = '5V3V2V3V5'
        # strip = '1V1V3M3V2V1'
        # strip = '6V6V6V6M6'
        strip = '3V3V4'
        # strip_object = get_strip_from_str(strip)
        # self.assertTrue(strip_object.is_simple_foldable_order([4, 2, 1, 3, 0], visualization=False))
        random_simple_foldable(strip)

    def test_strategy(self, strategy):
        for j in range(1000):
            strip_length: int = 9
            strip: str = f'{random.randint(1, 9)}'
            for i in range(strip_length):
                strip += f'{random.choice(["M", "V"])}{random.randint(1, 9)}'
            print(f'Try string: {strip}')
            self.assertTrue(strategy(strip))
            print('---------- Success ----------')

    def test_least_strategy(self):
        self.test_strategy(fold_least_crease)

    def test_analyze_database(self):
        self.assertTrue(visualize_order_amount())

    def test_states(self):
        analyze_states()

    def test_consecutive(self):
        self.assertTrue(test_if_consecutive_exists())

    def test_find_cycle(self):
        self.assertFalse(find_any_cycle())

    def test_crease_types(self):
        self.assertTrue(analyze_same_crease_patterns())
