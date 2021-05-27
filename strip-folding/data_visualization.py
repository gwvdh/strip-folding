from data_processing import open_database, calculate_some_fold
from typing import Dict, Tuple, List
from visualization import visualize_layers
import matplotlib.pyplot as plt


def random_simple_foldable(strip: str):
    data = open_database()
    print('Database opened')
    # for strip, s in data.iteritems():
    #     print(strip)
    #     print(s)
    if strip in data:
        iterator = iter(data[strip].values())
        value = next(iterator)
        print('Strip found in database')
        print(f'Crease order: {value["order"]}')
        visualize_layers(value['layers'])
    else:
        print('Strip not in database')
        print('Calulating...')
        calculate_some_fold(strip)
        iterator = iter(data[strip].values())
        value = next(iterator)
        print(f'Crease order: {value["order"]}')
        visualize_layers(value['layers'])

