from typing import Dict, List
from strip import Strip, Face
import os
import json
import sys
import sqlite3
from tqdm import tqdm

DATABASE_PATH: str = 'output/database.json'


def open_database():
    if not os.path.exists(f'output/'):
        os.makedirs(f'output/')
    if not os.path.exists(DATABASE_PATH):
        with open(DATABASE_PATH, 'w') as outfile:
            json.dump({
                '1': {'': {
                    'layers': {'001': [0]},
                    'order': []
                }}
            }, outfile)
    with open(f'{DATABASE_PATH}') as json_file:
        return json.load(json_file)


def write_database(data: Dict):
    with open(f'{DATABASE_PATH}', 'w') as outfile:
        json.dump(data, outfile)


def merge_databases(new_database):
    old_database = open_database()
    for strip, order_data in new_database.items():
        if strip in old_database:
            for order, data in order_data.items():
                if order not in old_database[strip]:
                    old_database[strip][order] = data
        else:
            old_database[strip] = order_data
    write_database(old_database)


def calculate_all_folds():
    database = {}
    merge_batch = 0
    with tqdm(range(10000, 20000)) as progress_bar:
        progress_bar.set_postfix(Merge=merge_batch, refresh=False)
        for f in progress_bar:
            s: str = str(f)
            if '0' not in s:
                faces: List[Face] = []
                for face in s:
                    faces.append(Face(int(face)))
                for i in range(2**(len(s) - 1)):
                    strip: Strip = Strip(faces, i, 0, len(s) - 1)
                    strip.set_json_data(database)
                    strip.all_simple_folds()
                    database = strip.get_json_data()
            if sys.getsizeof(database) > 1e6:
                merge_batch += 1
                merge_databases(database)
                progress_bar.set_postfix(Merge=merge_batch, refresh=False)
                progress_bar.update(0)
                database = {}
    merge_databases(database)
