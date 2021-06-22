from typing import List, Dict, Tuple, Set
from strip import Strip, Face, get_strip_from_str
from database_tools import open_database, insert_data, open_dict_database, merge_databases
import json
import matplotlib.pyplot as plt
import matplotlib.colors as mcl
from tqdm import tqdm
from functools import reduce
import re
from itertools import starmap


def calculate_all_folds_strip_length():
    """
    Calculate all possible strips of some lengths.
    Length 11 | creases: 0b111111111 | mv: 0b111100100 | Strip: 1V1V1M1V1V1M1M1M1M2
    :return:
    """
    connection, cur = open_database()
    merge_batch = 0
    for length in range(11, 12):
        for creases in range(2 ** (length - 1)):
            for mv_assignment in range(2 ** bin(creases).count('1')):
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
                for i in range(2 ** (len(s) - 1)):
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


def construct_global_order(layers: Dict[str, Dict[str, str]], order: str) -> Dict[int, Set[int]]:
    """
    Return a dictionary for each face which other faces are directly below it.

    :param layers:
    :param order:
    :return:
    """
    adjacency_dict: Dict[int, Set[int]] = {}
    for _, layer_list in layers.items():
        previous: List[int] = []
        for layer_str in layer_list[order].split('|'):
            layer: int = int(layer_str)
            for face in previous:
                if face not in adjacency_dict:
                    adjacency_dict[face] = set()
                adjacency_dict[face].add(int(layer))
            previous.append(layer)
    return adjacency_dict


def detect_cycle(adjacency_dict: Dict[int, Set[int]], face: int, visited: List[bool], rec_stack: List[bool]) -> bool:
    visited[face] = True
    rec_stack[face] = True
    for neighbor in adjacency_dict[face]:
        if not visited[neighbor]:
            if detect_cycle(adjacency_dict, neighbor, visited, rec_stack):
                return True
        elif rec_stack[neighbor]:
            return True
    rec_stack[face] = False
    return False


def find_any_cycle():
    connection, cur = open_database()
    # Get strips
    cur.execute(f'SELECT strip_name, layers, n_creases FROM strips WHERE len>? AND n_creases>?', (1, 1))
    for row in cur:
        print(f'Testing {row[0]}')
        layers = json.loads(row[1])
        all_orders: Set[str] = get_all_orders(layers)
        all_faces: List[int] = list(map(lambda x: int(x), all_orders.pop().split('|')))
        all_faces.append(max(all_faces) + 1)
        visited: List[bool] = [False] * (len(all_faces))
        rec_stack: List[bool] = [False] * (len(all_faces))
        for order in all_orders:
            adjacency_dict: Dict[int, Set[int]] = construct_global_order(layers, order)
            for face in all_faces:
                if face not in adjacency_dict:
                    adjacency_dict[face] = set()
            if detect_cycle(adjacency_dict, 0, visited, rec_stack):
                print(f'Strip {row[0]}: {order}')
                return True
    return False


def same_order(layer_dict: Dict[str, Dict[str, str]], all_orders: List[str]) -> int:
    orders: Set[str] = set()
    for order in all_orders:
        state_string: str = ''
        for _, layers in layer_dict.items():
            state_string += layers[order]
        orders.add(state_string)
    return len(orders)


def get_all_orders(orders: Dict[str, Dict[str, str]]) -> Set[str]:
    all_orders: Set[str] = set()
    for _, layers in orders.items():
        for order in layers:
            all_orders.add(order)
        break
    return all_orders


def get_order_intersection(orders: Dict[str, Dict[str, str]], order_set: Set[str]):
    all_orders: Set[str] = get_all_orders(orders)
    intersection = order_set.intersection(all_orders)
    return intersection


def get_orders_union(orders: Dict[str, Dict[str, str]], order_set: Set[str]) -> Set[str]:
    all_orders: Set[str] = get_all_orders(orders)
    union = order_set.union(all_orders)
    return union


def test_if_consecutive_exists():
    """
    See if there exists a strip which has no order containing consecutive layers
    :return:
    """
    connection, cur = open_database()
    cur.execute(f'SELECT strip_name, layers, n_creases FROM strips WHERE n_creases > 1')
    for row in cur:
        json_object = json.loads(row[1])
        all_orders: List[str] = list(get_all_orders(json_object))
        n_layers: int = len(all_orders[0].split('|'))
        for i in range(n_layers - 1):
            found_consecutive: bool = False
            for _, layers_by_order in json_object.items():
                for order, layers in layers_by_order.items():
                    if f'{i}' in layers and f'{i + 1}' in layers and (
                            f'{i}|{i + 1}' in layers or f'{i + 1}|{i}' in layers):
                        found_consecutive = True
                        print(f'Found consecutive {i}|{i + 1} in {row[0]}: {order}')
                        break
                if found_consecutive:
                    break
            if not found_consecutive:
                print(f'Did not found consecutive {i}|{i + 1} for strip: {row[0]}')
                print(f'{json_object}')
                return False
    return True


def analyze_states_length_intersection():
    """
    See which strips of different lengths and same crease patterns have intersecting states.

    :return:
    """
    connection, cur = open_database()
    # Get strips
    all_intersecting: Set[str] = set()
    print()
    # 1V1M1M1V1M1V1M1M1
    for j in range(int('11010110', 2), int('11010111', 2)):
        name = ''
        base: Set[str] = set()
        for i in range(7, 11):
            cur.execute(f'SELECT strip_name, layers, M_creases, len, n_creases, n_states, crease_direction '
                        f'FROM strips WHERE len=? AND crease_direction=? AND n_creases=?', (i, j, 8))
            for row in cur:
                if name == '':
                    name = row[0]
                state_length_set: Set[str] = set()
                json_object = json.loads(row[1])
                state_length_set = get_orders_union(json_object, state_length_set)
                list_rep: List[str] = list(get_all_orders(json_object))
                list_rep.sort()
                if i == 9:
                    base = set(list_rep)
                if len(list_rep) < 50:
                    print(f'Length {i}, {row[0]}: {list_rep}')
                else:
                    print(f'Length {i}, {row[0]}: {len(list_rep)}')
                intersection = list(base.intersection(set(list_rep)))
                if len(intersection) < 50:
                    print(f'Intersection: {intersection}')
                else:
                    print(f'Intersection: {len(intersection)}')
                if all_intersecting:
                    all_intersecting = all_intersecting.intersection(state_length_set)
                else:
                    all_intersecting = state_length_set
        list_rep: List[str] = list(all_intersecting)
        list_rep.sort()
        if len(list_rep) < 30:
            print(f'{name}: {list_rep}')
        else:
            print(f'{name}: {len(list_rep)}')


def analyze_states():
    """
    Create a new dataset for all the folded states per strip

    :return:
    """
    connection, cur = open_database()
    # Get strips
    cur.execute(f'SELECT strip_name, layers, M_creases, len, n_creases, n_states, crease_direction '
                f'FROM strips WHERE len=?', (4,))
    write_cursor = connection.cursor()
    n_states = []
    n_orders = []
    m_creases = []
    length = []
    n_creases = []
    mv_assignment = []
    counter = 0
    pbar = tqdm(total=50000)
    analyze_states_length_intersection()
    least_orders = {}
    for row in cur:
        if '0' in row[0]:
            print(row[0])
        orders = row[5]
        # print(f'Strip {row[0]}: {row[1]}')
        json_object = json.loads(row[1])
        print(f'{row[0]}: {json_object}')
        all_orders: List[str] = []
        for _, order_layers in json_object.items():
            for order_str, layers in order_layers.items():
                all_orders.append(order_str)
            break
        if row[4] not in least_orders or least_orders[row[4]][1] > len(all_orders):
            least_orders[row[4]] = (row[0], len(all_orders))
        if row[6] == -1:
            # orders = same_order(json_object, all_orders)
            strip: Strip = get_strip_from_str(row[0])
            print(f'Folds {row[0]}: {row[6]} -> {strip.get_original_creases()}')
            write_cursor.execute(f'UPDATE strips SET crease_direction = {strip.get_original_creases()} '
                                 f'WHERE strip_name = "{row[0]}"')
            connection.commit()
        if True or row[6] == 63:
            # if len(all_orders) > 10000:
            #     print(f'{row[0]}: {len(all_orders)}')
            n_states.append(orders)
            # if len(all_orders) > 75000:
            #     print(f'States: {row[0]}')
            # if row[3] == 5:
            # print(f'Orders {row[3]}: {orders}')
            m_creases.append(row[2])
            n_orders.append(len(all_orders))
            length.append(row[3])
            n_creases.append(row[4])
            mv_assignment.append(row[6])

        counter += 1
        pbar.update(1)
    print(f'Least orders: {least_orders}')
    print(f'Max states: {max(n_states)}')
    pbar.close()
    plt.hist2d(n_orders, n_states, norm=mcl.LogNorm(), cmap=plt.cm.jet, cmin=1,
               bins=(100, 100))  # bins=(max(n_orders), max(n_states)))
    plt.colorbar()
    plt.show()


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


def fold_least_crease(strip: str) -> bool:
    strip_object: Strip = get_strip_from_str(strip)
    strip_scores: List[Tuple[int, int]] = []
    for face in range(len(strip_object.get_faces()) - 1):
        strip_scores.append((face, strip_object.get_faces()[face].get_length()))
    strip_scores = sorted(strip_scores, key=lambda tup: tup[1])
    fold_order: List[int] = list(map(lambda creases: creases[0], strip_scores))
    print(fold_order)
    return strip_object.is_simple_foldable_order(fold_order, visualization=False)


def analyze_up_to_10(strip: str):
    crease_directions = re.split('\d+', strip)
    face_lengths: List[str] = re.split('[A-Z]', strip)
    face_lengths: List[int] = list(map(lambda x: int(x), face_lengths))
    if reduce(lambda a, b: a+b, face_lengths, 0) < 9:
        pass


def is_subset_of(strip_1: str, strip_2: str) -> bool:
    if strip_2 == strip_1:
        return False
    face_lengths_1: List[str] = re.split('[A-Z]', strip_1)
    face_lengths_2: List[str] = re.split('[A-Z]', strip_2)
    face_lengths: List[int] = list(starmap(lambda a, b: int(a) - int(b), zip(face_lengths_1, face_lengths_2)))
    for length in face_lengths:
        if length > 0:
            return False
    # print(f'{strip_2} subset of {strip_1}')
    return True


def analyze_same_crease_patterns():
    connection, cur = open_database()
    # Get strips
    print('Start analysis')
    for n_creases in range(4, 5):
        print('-1-')
        for crease_type in range(5, 6):
            for crease_assignment in range(2**n_creases):
                order_dict: Dict[str, Set[str]] = {}
                minimum_orders: Set[str] = set()
                orders: Set[str] = set()
                print(f'Analyze: {n_creases} {crease_type}')
                cur.execute(f'SELECT strip_name, layers, len, creases, crease_type, n_creases, crease_direction '
                            f'FROM strips WHERE crease_type=? AND n_creases=? AND crease_direction=?',
                            (crease_type, n_creases, crease_assignment))
                # cur.execute(f'SELECT * FROM strips')
                for row in cur:
                    json_object = json.loads(row[1])
                    order_dict[row[0]] = get_all_orders(json_object)
                    if len(minimum_orders) == 0:
                        minimum_orders = get_all_orders(json_object)
                    if len(orders) == 0:
                        orders = get_all_orders(json_object)
                    else:
                        orders = get_order_intersection(json_object, orders)
                    minimum_intersection = get_order_intersection(json_object, minimum_orders)
                    # print(f'Minimum intersection: {minimum_intersection}')
                    orders_print = list(orders)
                    orders_print.sort()
                    # print(f'{row[0]}: {orders_print}')
                    if len(minimum_intersection) == 0:
                        print(f'Not intersecting: {row[0]}')
                        print(f'N_creases: {n_creases}, crease type: {crease_type}, '
                              f'crease assignment: {crease_assignment}')
                        return False
                    if len(orders) == 0:
                        print(f'No all intersecting: {row[0]}')
                        print(f'N_creases: {n_creases}, crease type: {crease_type}, '
                              f'crease assignment: {crease_assignment}')
                        # return False
                print(orders)
                lattice: Dict[str, List[str]] = {}
                for strip_1 in order_dict:
                    lattice[strip_1] = []
                    for strip_2 in order_dict:
                        if strip_2 != strip_1 and is_subset_of(strip_2, strip_1):
                            lattice[strip_1].append(strip_2)
                    print(f'{strip_1}: {lattice[strip_1]}')
                for strip, adj in lattice.items():
                    intersection: Set[str] = reduce(lambda a, b: a.intersection(order_dict[b]), adj, order_dict[strip])
                    print(f'Intersection {strip}: {intersection}')
                    if len(intersection) == 0:
                        return False
                for ele, adj in lattice.items():
                    to_remove = []
                    for strip in adj:
                        to_remove.extend(lattice[strip])
                    for strip in to_remove:
                        try:
                            lattice[ele].remove(strip)
                        except ValueError:
                            pass
                print(f'Lattice: {lattice}')
                for strip, fold_orders in order_dict.items():
                    print(f'{strip}: {fold_orders}')
                # return True
    return True


def insert_same_crease_patterns():
    connection, cur = open_database()
    # Get strips
    cur.execute(f'SELECT strip_name, len, n_creases, crease_direction FROM strips')
    write_cursor = connection.cursor()
    for row in cur:
        face_lengths: List[str] = re.split('[A-Z]', row[0])
        face_lengths: List[int] = list(map(lambda x: int(x), face_lengths))
        crease_type: int = 0
        crease_index: int = 0
        strip_length: int = 0
        for face in face_lengths[:-1]:
            strip_length += face
            if strip_length % 2 == 1:
                crease_type |= (1 << crease_index)
            crease_index += 1
        write_cursor.execute(f'UPDATE strips SET crease_type = {crease_type} '
                             f'WHERE strip_name = "{row[0]}"')
        print(f'Altered: {row[0]} | {bin(crease_type)}')
        connection.commit()
    return True



