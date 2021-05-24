import unittest
from typing import List, Tuple
from strip import is_upside_down, Strip, Face, Direction, coordinate_folds_up
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
            coordinate_folds_up(coordinate_1, global_crease_h, is_mountain_fold, face)
        face = Face(10, Direction.N)
        # TODO: Check these, they might not be correct
        self.assertFalse(coordinate_folds_up(coordinate_1, global_crease_h, is_mountain_fold, face))
        self.assertTrue(coordinate_folds_up(coordinate_h, global_crease_h, is_mountain_fold, face))
        is_mountain_fold: bool = False
        self.assertTrue(coordinate_folds_up(coordinate_1, global_crease_h, is_mountain_fold, face))
        self.assertFalse(coordinate_folds_up(coordinate_h, global_crease_h, is_mountain_fold, face))
        face = Face(10, Direction.S)
        self.assertFalse(coordinate_folds_up(coordinate_1, global_crease_h, is_mountain_fold, face))
        self.assertTrue(coordinate_folds_up(coordinate_h, global_crease_h, is_mountain_fold, face))
        is_mountain_fold: bool = True
        self.assertTrue(coordinate_folds_up(coordinate_1, global_crease_h, is_mountain_fold, face))
        self.assertFalse(coordinate_folds_up(coordinate_h, global_crease_h, is_mountain_fold, face))
        # North crease
        face = Face(10, Direction.N)
        global_crease_n: Tuple[Direction, int] = (Direction.N, 0)
        coordinate_n: Tuple[int, int, int] = (1, 0, 0)
        is_mountain_fold: bool = True
        with self.assertRaises(Exception):
            coordinate_folds_up(coordinate_1, global_crease_n, is_mountain_fold, face)
        face = Face(10, Direction.H)
        self.assertFalse(coordinate_folds_up(coordinate_1, global_crease_n, is_mountain_fold, face))
        self.assertTrue(coordinate_folds_up(coordinate_n, global_crease_n, is_mountain_fold, face))
        is_mountain_fold: bool = False
        self.assertTrue(coordinate_folds_up(coordinate_1, global_crease_n, is_mountain_fold, face))
        self.assertFalse(coordinate_folds_up(coordinate_n, global_crease_n, is_mountain_fold, face))
        face = Face(10, Direction.S)
        self.assertFalse(coordinate_folds_up(coordinate_1, global_crease_n, is_mountain_fold, face))
        self.assertTrue(coordinate_folds_up(coordinate_n, global_crease_n, is_mountain_fold, face))
        is_mountain_fold: bool = True
        self.assertTrue(coordinate_folds_up(coordinate_1, global_crease_n, is_mountain_fold, face))
        self.assertFalse(coordinate_folds_up(coordinate_n, global_crease_n, is_mountain_fold, face))
        # South crease
        face = Face(10, Direction.S)
        global_crease_s: Tuple[Direction, int] = (Direction.S, 0)
        coordinate_s: Tuple[int, int, int] = (-1, 0, 0)
        is_mountain_fold: bool = True
        with self.assertRaises(Exception):
            coordinate_folds_up(coordinate_h, global_crease_s, is_mountain_fold, face)
        face = Face(10, Direction.H)
        self.assertFalse(coordinate_folds_up(coordinate_h, global_crease_s, is_mountain_fold, face))
        self.assertTrue(coordinate_folds_up(coordinate_s, global_crease_s, is_mountain_fold, face))
        is_mountain_fold: bool = False
        self.assertTrue(coordinate_folds_up(coordinate_h, global_crease_s, is_mountain_fold, face))
        self.assertFalse(coordinate_folds_up(coordinate_s, global_crease_s, is_mountain_fold, face))
        face = Face(10, Direction.N)
        self.assertFalse(coordinate_folds_up(coordinate_h, global_crease_s, is_mountain_fold, face))
        self.assertTrue(coordinate_folds_up(coordinate_s, global_crease_s, is_mountain_fold, face))
        is_mountain_fold: bool = True
        self.assertTrue(coordinate_folds_up(coordinate_h, global_crease_s, is_mountain_fold, face))
        self.assertFalse(coordinate_folds_up(coordinate_s, global_crease_s, is_mountain_fold, face))

    def test_simple_foldable_order(self):
        faces: List[Face] = (Face(2), Face(1), Face(1), Face(1))
        creases: int = int('011', 2)
        folds: int = int('000', 2)
        strip: Strip = Strip(faces, creases, folds, 3)
        self.assertFalse(strip.is_simple_foldable_order([0, 1, 2]))
        faces: List[Face] = (Face(2), Face(1), Face(1), Face(1))
        strip: Strip = Strip(faces, creases, folds, 3)
        self.assertTrue(strip.is_simple_foldable_order([1, 2, 0]))


