from typing import List
from strip import Strip, Face
import json
import sys
from sqlitedict import SqliteDict
from tqdm import tqdm

DATABASE_PATH: str = 'output/database.db'


def open_database():
    return SqliteDict(DATABASE_PATH, autocommit=True)


def merge_databases(new_database):
    old_database = open_database()
    for strip, order_data in new_database.items():
        if strip in old_database:
            for order, data in order_data.items():
                if order not in old_database[strip]:
                    old_database[strip][order] = data
        else:
            old_database[strip] = order_data


def calculate_all_folds():
    database = {}
    merge_batch = 0
    with tqdm(range(2195, 100000)) as progress_bar:
        for f in progress_bar:
            s: str = str(f)
            if '0' not in s:
                progress_bar.set_postfix(Data=f'{merge_batch} | {sys.getsizeof(database)}', refresh=True)
                faces: List[Face] = []
                for face in s:
                    faces.append(Face(int(face)))
                for i in range(2**(len(s) - 1)):
                    strip: Strip = Strip(faces, i, 0, len(s) - 1)
                    strip.set_db(database)
                    strip.all_simple_folds()
                    database = strip.get_db()
            if sys.getsizeof(database) > 1e5:
                merge_batch += 1
                merge_databases(database)
                database = {}
    merge_databases(database)
