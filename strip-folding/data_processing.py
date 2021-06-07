from typing import List, Dict, Tuple, Set
from strip import Strip, Face
import json
import matplotlib.pyplot as plt
import matplotlib.colors as mcl
from sqlitedict import SqliteDict
from tqdm import tqdm
import sqlite3

DICT_DATABASE_PATH: str = 'output/dict_database_2.db'
DATABASE_PATH: str = 'output/database_3.db'


def open_database():
    """
    Open the database and return the connection and cursor of the SQLite database
    :return:
    """
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS strips
                   (strip_name text, 
                   len INTEGER, 
                   n_creases INTEGER, 
                   M_creases INTEGER, 
                   creases INTEGER, 
                   crease_direction INTEGER,
                   layers text)'''
                )
    return con, cur


def insert_data(data, cursor):
    """
    Insert the given data into the SQLite database.

    :param data: tuple of data
    :param cursor: cursor of the SQLite database
    :return:
    """
    sql = '''INSERT INTO strips(strip_name, len, n_creases, M_creases, creases, crease_direction, layers) 
             VALUES(?, ?, ?, ?, ?, ?, ?)'''
    cursor.execute(sql, data)


def open_dict_database():
    return SqliteDict(DICT_DATABASE_PATH, autocommit=True)


def merge_databases(new_database):
    old_database = open_dict_database()
    for strip, order_data in new_database.items():
        if strip in old_database:
            for order, data in order_data.items():
                if order not in old_database[strip]:
                    old_database[strip][order] = data
        else:
            old_database[strip] = order_data


def calculate_all_folds_strip_length():
    """
    Calculate all possible strips of some lengths.

    :return:
    """
    connection, cur = open_database()
    merge_batch = 0
    for length in range(11, 12):
        for creases in range(2**(length - 1)):
            for mv_assignment in range(2**bin(creases).count('1')):
                face_length: int = 1
                crease_i: int = 0
                strip_str: str = ''
                for i in range(length - 1):
                    if creases & (1 << i):
                        strip_str += f'{face_length}{"M" if mv_assignment & (1 << crease_i) else "V"}'
                        face_length = 0
                        crease_i += 1
                    face_length += 1
                strip_str += str(face_length)
                print(f'Length {length} | creases: {bin(creases)} | mv: {bin(mv_assignment)} | Strip: {strip_str}')
                strip: Strip = get_strip_from_str(strip_str)
                # strip.set_db(database)
                if not strip.all_simple_folds():
                    return False
                data = (strip.get_strip_string(),
                        strip.get_length(),
                        strip.get_crease_amount(),
                        strip.get_n_mountain_folds(),
                        strip.get_original_creases(),
                        strip.get_original_folds(),
                        json.dumps(strip.get_db())
                        )
                insert_data(data, cur)
            connection.commit()
            merge_batch += 1
    return True


def calculate_all_folds():
    connection, cur = open_database()
    merge_batch = 0
    with tqdm(range(1000, 200000)) as progress_bar:
        for f in progress_bar:
            s: str = str(f)
            if '0' not in s:
                progress_bar.set_postfix(Batch=f'{merge_batch}', refresh=True)
                faces: List[Face] = []
                for face in s:
                    faces.append(Face(int(face)))
                for i in range(2**(len(s) - 1)):
                    strip: Strip = Strip(faces, i, 0, len(s) - 1)
                    # strip.set_db(database)
                    if not strip.all_simple_folds():
                        return False
                    data = (strip.get_strip_string(),
                            strip.get_length(),
                            strip.get_crease_amount(),
                            strip.get_n_mountain_folds(),
                            strip.get_original_creases(),
                            strip.get_original_folds(),
                            json.dumps(strip.get_db())
                            )
                    insert_data(data, cur)
                    if f > (merge_batch + 1) * 1000:
                        connection.commit()
                        merge_batch += 1
    return True


def calculate_some_fold(strip: str):
    strip_object: Strip = get_strip_from_str(strip)
    if strip_object.is_simple_foldable():
        merge_databases(strip_object.get_db())


def read_database_layers(layers: Dict[str, List[int]]) -> Dict[Tuple[int, int, int], List[int]]:
    layer_dict: Dict[Tuple[int, int, int], List[int]] = {}
    for key, val in layers.items():
        key_tuple: Tuple = tuple(map(int, key.split('|')))
        layer_dict[key_tuple] = val
    return layer_dict


def construct_global_order(layers: Dict[Tuple[int, int, int], List[int]]):
    """
    Return a dictionary for each face which other faces are directly below it.

    :param layers:
    :return:
    """
    adjacency_dict: Dict[int, Set[int]] = {}
    for _, layer_list in layers.items():
        previous: int = -1
        for layer in layer_list:
            if layer not in adjacency_dict:
                adjacency_dict[layer] = set()
            if previous != -1:
                adjacency_dict[layer].add(previous)
                adjacency_dict[layer] = adjacency_dict[layer].union(adjacency_dict[previous])
            previous = layer
    return adjacency_dict


def same_order(orders: List[str], layer_dict: Dict[str, List[int]]) -> List[List[str]]:
    order_lists: List[List[str]] = []
    for order_1 in orders:
        for order_2 in orders:
            if layer_dict[order_1] == layer_dict[order_2]:
                found_group: bool = False
                for order_list in order_lists:
                    if order_1 not in order_list and order_2 in order_list:
                        order_list.append(order_1)
                        found_group = True
                        break
                if not found_group:
                    order_lists.append([order_1])
    return order_lists


def analyze_states():
    """
    Create a new dataset for all the folded states per strip

    :return:
    """
    connection, cur = open_database()
    # Get strips
    cur.execute(f'SELECT * FROM strips')
    for row in cur:
        print(row)
        json_object = {}  # TODO: add json object from row
        for _, order_layers in json_object.items():
            for order_str, layers in order_layers.items():
                order = order_str
                break
    # Create states
    states = {
        'amount': 0,
        'states': [
            {'layers': {},
             'orders': []
             }
        ]
    }


def analyze_database():
    database = open_dict_database()
    percentages: List[float] = []
    n_orders: List[int] = []
    counter: int = 0
    for s, data in tqdm(database.items(), total=len(database)):
        if 12 > len(s) > 10:
            if len(data) < 31:
                print(f'{s}: {len(data)}')
            p_mountain: float = (s.count('M') / ((len(s) - 1) / 2))
            # print(f'pM {s}: {pM}')
            percentages.append(p_mountain)
            n_orders.append(len(data))
            if counter > 1000000:
                break
            counter += 1

    plt.hist2d(percentages, n_orders, (50, 50), cmap=plt.cm.jet)
    plt.colorbar()
    plt.show()
    return True


def visualize_order_amount():
    creases = 5
    database = open_dict_database()
    percentages: List[float] = []
    n_orders: List[int] = []
    counter: int = 0
    for s, data in tqdm(database.items(), total=len(database)):
        if len(s) == creases * 2 + 1:
            if len(data) < 31:
                print(f'{s}: {len(data)}')
            p_mountain: float = (s.count('M') / ((len(s) - 1) / 2))
            # print(f'pM {s}: {pM}')
            percentages.append(p_mountain)
            n_orders.append(len(data))
            if counter > 1000000:
                break
            counter += 1
    my_cmap = plt.cm.get_cmap('jet')
    my_cmap.set_bad('w')
    plt.hist2d(percentages, n_orders, (50, 50), norm=mcl.LogNorm(), cmap=my_cmap)
    plt.colorbar()
    plt.show()
    return True


def get_strip_from_str(strip: str) -> Strip:
    """
    Transform a string representation of a strip into a strip object

    :param strip: string representing a strip
    :return: strip object of the strip string
    """
    faces: List[Face] = []
    creases: int = 0
    for s in strip:
        try:
            length = int(s)
            faces.append(Face(length))
        except ValueError:
            if s == 'M':
                creases = creases ^ (1 << len(faces) - 1)
    return Strip(faces, creases, 0, len(faces) - 1)


def fold_least_crease(strip: str) -> bool:
    strip_object: Strip = get_strip_from_str(strip)
    strip_scores: List[Tuple[int, int]] = []
    for face in range(len(strip_object.get_faces()) - 1):
        strip_scores.append((face, strip_object.get_faces()[face].get_length()))
    strip_scores = sorted(strip_scores, key=lambda tup: tup[1])
    fold_order: List[int] = list(map(lambda creases: creases[0], strip_scores))
    print(fold_order)
    return strip_object.is_simple_foldable_order(fold_order, visualization=False)
