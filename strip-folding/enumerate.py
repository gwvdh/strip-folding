from typing import List
from strip import Strip, Face


def brute_force():
    pass


def brute_force_simple_folds():
    for creases in range(2**6):
        bit_string: str = bin(creases).replace('0b', '')
        for face in range(len(bit_string) + 1):
            for strip_lengths in range(10**(len(bit_string) + 1)):
                faces: List[Face] = []
                for face_length in str(strip_lengths):
                    faces.append(Face(face_length))
                strip: Strip = Strip(faces, creases)
                print(strip.is_simple_foldable())

    strip: Strip = Strip()
