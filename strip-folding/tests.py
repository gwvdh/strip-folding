import unittest
from typing import List
from strip import is_upside_down, Strip, Face, Direction


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
        faces: List[Face] = [Face(3), Face(4), Face(1), Face(1), Face(5)]
        creases: int = int('0000', 2)
        folds: int = int('0000', 2)
        strip: Strip = Strip(faces, creases, folds, 4)
        strip.fold_crease(0)
        strip.fold_crease(2)
        strip.fold_crease(3)
        self.assertTrue(strip.is_simple_foldable())

