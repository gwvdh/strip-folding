from typing import List, Dict, Tuple, Set
from strip import Strip, get_strip_from_str, construct_strip_str, StripError
from database_tools import open_database, insert_data, merge_databases
from visualization import visualize_layers
import json
import matplotlib.pyplot as plt
import matplotlib.colors as mcl
from functools import reduce
import re
from itertools import starmap


def calculate_all_folds_strip_length(min_length: int = 1, max_length: int = 10, debug: bool = False) -> bool:
    """
    Calculate all possible strips of some lengths.
    Length 11 | creases: 0b111111111 | mv: 0b111100100 | Strip: 1V1V1M1V1V1M1M1M1M2
    :param: min_length: Minimum length of strips to calculate
    :param: max_length: Maximum length of strips to calculate
    :return:
    """
    if min_length < 1:
        raise StripError("Invalid minimum strip length")
    connection, cur = open_database()
    merge_batch = 0
    for length in range(min_length, max_length + 1):
        for creases in range(2 ** (length - 1)):
            for mv_assignment in range(2 ** bin(creases).count('1')):
                # Construct the strip string
                strip_str: str = construct_strip_str(length, creases, mv_assignment)
                if debug:
                    print(f'Length {length} | creases: {bin(creases)} | mv: {bin(mv_assignment)} | Strip: {strip_str}')
                strip: Strip = get_strip_from_str(strip_str)
                # Calculate all valid simple foldable sequences
                if not strip.all_simple_folds():
                    return False
                # Add data to the database
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


def calculate_some_fold(strip: str):
    """
    Calculate if some strip has a simple foldable sequence.
    Add that foldable sequence to the database.
    :param strip: Strip string
    :return:
    """
    strip_object: Strip = get_strip_from_str(strip)
    if strip_object.is_simple_foldable():
        merge_databases(strip_object.get_db())


def read_database_layers(layers: Dict[str, List[int]]) -> Dict[Tuple[int, int, int], List[int]]:
    """
    Transform string key representation to tuple representation.
    :param layers:
    :return:
    """
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
    """
    Check whether there exists a cycle in a given layer dictionary.
    :param adjacency_dict:
    :param face:
    :param visited:
    :param rec_stack:
    :return:
    """
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
    """
    Check if there exists a layer cycle in the database.
    :return:
    """
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
    """
    Check how many distinct orders order some layer dictionary contains.
    :param layer_dict: Layer dictionary
    :param all_orders: All orders in the dictionary
    :return: Amount of distinct orders in layer_dict
    """
    orders: Set[str] = set()
    for order in all_orders:
        state_string: str = ''
        for _, layers in layer_dict.items():
            state_string += layers[order]
        orders.add(state_string)
    return len(orders)


def get_all_orders(layer_dict: Dict[str, Dict[str, str]]) -> Set[str]:
    """
    Return all orders contained in a layer dictionary
    :param layer_dict: Layer dictionary
    :return:
    """
    all_orders: Set[str] = set()
    for _, layers in layer_dict.items():
        for order in layers:
            if len(order) > 0:
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
                f'FROM strips WHERE crease_direction=?', (0, ))
    write_cursor = connection.cursor()
    n_states = []
    n_orders = []
    m_creases = []
    length = []
    n_creases = []
    mv_assignment = []
    counter = 0
    analyze_states_length_intersection()
    least_orders = {}
    for row in cur:
        if '0' in row[0]:
            print(row[0])
        orders = row[5]
        json_object = json.loads(row[1])
        all_orders: Set[str] = get_all_orders(json_object)
        if row[4] not in least_orders or least_orders[row[4]][1] > len(all_orders):
            least_orders[row[4]] = (row[0], len(all_orders))
        if row[6] == -1:
            strip: Strip = get_strip_from_str(row[0])
            print(f'Folds {row[0]}: {row[6]} -> {strip.get_original_creases()}')
            write_cursor.execute(f'UPDATE strips SET crease_direction = {strip.get_original_creases()} '
                                 f'WHERE strip_name = "{row[0]}"')
            connection.commit()
        n_states.append(orders)
        m_creases.append(row[2])
        n_orders.append(len(all_orders))
        length.append(row[3])
        n_creases.append(row[4])
        mv_assignment.append(row[6])

        counter += 1
    print(f'Least orders: {least_orders}')
    print(f'Max states: {max(n_states)}')
    plt.hist2d(n_orders, n_states, norm=mcl.LogNorm(), cmap=plt.cm.get_cmap('jet').copy(), cmin=1,
               bins=(100, 100))  # bins=(max(n_orders), max(n_states)))
    plt.xlabel('Number of orders')
    plt.ylabel('Number of states')
    plt.colorbar()
    plt.show()
    return True


def visualize_order_amount():
    """
    Visualize a 2D histogram with the amount of valid flat folding orders
    in relation to the percentage of mountain creases.
    :return:
    """
    connection, cur = open_database()
    # Get strips
    cur.execute(f'SELECT strip_name, layers, crease_direction, n_creases FROM strips '
                f'WHERE n_creases>? AND n_creases<?', (1, 11))
    percentages: List[float] = []
    n_orders: List[int] = []
    counter: int = 0
    for row in cur:
        mv_assignment: int = row[2]
        p_mountain: float = (bin(mv_assignment).count('1') / row[3])
        percentages.append(p_mountain)

        # Get all orders
        json_object = json.loads(row[1])
        orders: int = len(get_all_orders(json_object))
        n_orders.append(orders)
        if counter > 1000000:
            break
        counter += 1
    my_cmap = plt.cm.get_cmap('jet').copy()
    my_cmap.set_bad('w')
    plt.hist2d(x=percentages, y=n_orders, bins=50, norm=mcl.LogNorm(), cmap=my_cmap, cmin=1)
    plt.colorbar()
    plt.xlabel('Mountain folds (%)')
    plt.ylabel('Amount of valid folding orders')
    plt.show()
    return True


def fold_least_crease_strategy(strip: str) -> bool:
    """
    Fold the crease which is adjacent to the shortest face.
    :param strip:
    :return:
    """
    strip_object: Strip = get_strip_from_str(strip)
    strip_scores: List[Tuple[int, int]] = []
    for face in range(len(strip_object.get_faces()) - 1):
        strip_scores.append((face, strip_object.get_faces()[face].get_length()))
    strip_scores = sorted(strip_scores, key=lambda tup: tup[1])
    fold_order: List[int] = list(map(lambda creases: creases[0], strip_scores))
    print(fold_order)
    return strip_object.is_simple_foldable_order(fold_order, visualization=False)


def __is_subset_of(strip_1: str, strip_2: str) -> bool:
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


def construct_order_lattice(order_dict: Dict[str, Set[str]]) -> Dict[str, List[str]]:
    """
    Construct a lattice from all given orders.
    :param order_dict:
    :return: A lattice with all orders
    """
    # Construct a lattice adjacency matrix if the strip_2 is a subset of strip_1
    lattice: Dict[str, List[str]] = {}
    for strip_1 in order_dict:
        lattice[strip_1] = []
        for strip_2 in order_dict:
            if strip_2 != strip_1 and __is_subset_of(strip_2, strip_1):
                lattice[strip_1].append(strip_2)
        print(f'{strip_1}: {lattice[strip_1]}')
    # Find intersections between the strip and its sub-strips
    for strip, adj in lattice.items():
        intersection: Set[str] = reduce(lambda a, b: a.intersection(order_dict[b]), adj, order_dict[strip])
        print(f'Intersection {strip}: {intersection}')
        if len(intersection) == 0:
            raise ValueError  # Create custom exception for this
    # Clean up lattice to only include roots
    for ele, adj in lattice.items():
        to_remove = []
        for strip in adj:
            to_remove.extend(lattice[strip])
        for strip in to_remove:
            try:
                lattice[ele].remove(strip)
            except ValueError:
                pass
    return lattice


def analyze_same_crease_patterns():
    """
    Check for missing similar orders in lattice ordered strips.
    :return:
    """
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
                    all_orders = get_all_orders(json_object)
                    order_dict[row[0]] = all_orders
                    if len(minimum_orders) == 0:
                        minimum_orders = all_orders
                    if len(orders) == 0:
                        orders = all_orders
                    else:
                        orders = get_order_intersection(json_object, orders)
                    # Check if there exists an order which is valid for this and all previous strips
                    minimum_intersection = get_order_intersection(json_object, minimum_orders)
                    if len(minimum_intersection) == 0 or len(orders) == 0:
                        print(f'Not all intersecting: {row[0]}')
                        print(f'N_creases: {n_creases}, crease type: {crease_type}, '
                              f'crease assignment: {crease_assignment}')
                        return False
                # Construct a lattice adjacency matrix if the strip_2 is a subset of strip_1
                try:
                    lattice: Dict[str, List[str]] = construct_order_lattice(order_dict)
                except ValueError:
                    return False
                print(f'Lattice: {lattice}')
                for strip, fold_orders in order_dict.items():
                    print(f'{strip}: {fold_orders}')
    return True


def insert_same_crease_patterns():
    """
    Insert the crease directions (North or South facing) to the database
    :return:
    """
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


def get_order_from_str(order: str) -> List[int]:
    return list(map(lambda x: int(x), order.split('|')))


def analyze_no_two_direction_fold():
    """
    Check if we can always simple fold a strip by only folding creases which move the paper either up or down, not both.
    Might be usefull for a foldability proof.
    :return:
    """
    connection, cur = open_database()
    # Get strips
    cur.execute(f'SELECT strip_name, layers, len, n_creases, crease_direction FROM strips')
    for row in cur:
        print(f'Testing {row[0]}')
        json_object = json.loads(row[1])
        orders: Set[str] = get_all_orders(json_object)
        if len(orders) > 0:
            strip: Strip = get_strip_from_str(row[0])
            found_one_way_order: bool = False
            for order in orders:
                if strip.is_simple_foldable_order(get_order_from_str(order), one_way_fold=True, visualization=False):
                    found_one_way_order = True
                    break
                strip.reset_strip()
            if not found_one_way_order:
                print(f'Found unfoldable strip: {row[0]}')
                return False
    return True


def analyze_strip(strip_str: str) -> bool:
    connection, cur = open_database()
    cur.execute(f'SELECT strip_name, layers FROM strips WHERE strip_name=?',
                (strip_str,))
    strip: Strip = get_strip_from_str(strip_str)
    data = cur.fetchone()
    if data is None:
        print(f'Getting new strip information: {strip_str}')
        strip.all_simple_folds()
        data = (strip.get_strip_string(),
                strip.get_length(),
                strip.get_crease_amount(),
                strip.get_n_mountain_folds(),
                strip.get_original_creases(),
                strip.get_original_folds(),
                json.dumps(strip.get_db())
                )
        insert_data(data, cur)
        data = (strip.get_strip_string(), json.dumps(strip.get_db()))
    else:
        print(f'Found in database: {strip_str}')
    json_object = json.loads(data[1])
    orders: Set[str] = get_all_orders(json_object)
    random_order: str = next(iter(orders))
    print(f'Strip {data[0]}\n'
          f'Number of orders: {len(orders)}\n'
          f'Visualizing: {random_order}')
    visualize_layers(json_object, random_order)
    return True


def analyze_stamp_folding():
    connection, cur = open_database()
    for length in range(2, 11):
        all_orders: set[str] = set()
        cur.execute(f'SELECT strip_name, layers, len, n_creases FROM strips WHERE len=? AND n_creases=?',
                    (length, length-1))
        for row in cur:
            json_object = json.loads(row[1])
            all_orders.update(get_all_orders(json_object))
        print(f'Strip length: {length}\n'
              f'Number of orders: {len(all_orders)}\n')
    return True
