from data_processing import open_database, calculate_some_fold
from visualization import visualize_layers
import json


def random_simple_foldable(strip: str):
    conn, cur = open_database()
    print('Database opened')
    # for strip, s in data.iteritems():
    #     print(strip)
    #     print(s)
    cur.execute(f'SELECT layers FROM strips WHERE strip_name="{strip}"')
    data = cur.fetchall()
    if len(data) > 1:
        raise Exception(f'Too many values: {len(data)}, expected 1 or 0')
    elif len(data) == 0:
        print('Strip not in database')
        print('Calulating...')
        calculate_some_fold(strip)
    cur.execute(f'SELECT layers FROM strips WHERE strip_name="{strip}"')
    data = cur.fetchall()
    data = json.loads(data[0][0])
    print(f'Found data: {data}')
    order: str = ''
    for _, order_layers in data.items():
        for order_str in order_layers:
            order = order_str
            break
    visualize_layers(data, order)
