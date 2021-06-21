from grid import Grid, Triangle
from typing import Tuple, List, Dict
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap, ScalarMappable
from matplotlib.colors import Normalize, LogNorm
import numpy as np
import os
from folding_operations import transform_coordinate, is_upside_down


def visualize_grid(grid: Grid, folder_name: str = '', file_name: str = 'visualization',
                   log_scale: bool = False):
    __draw_shapes(grid, log_scale=log_scale)
    __show_save_visualization(folder_name=folder_name, vis_name=file_name, show_vis=True)


def __draw_board(board_shape: Tuple[int, int, int, int], extra_space: int = 2):
    """
    Draw the figure and set the size of the canvas.

    :param board_shape: Shape and size of the board
    :param extra_space: Extra space to add to the figure
    :return:
    """
    fig, axs = plt.subplots(1)
    axs.axis('off')
    fig.gca().set_aspect('equal', adjustable='box')

    axs.set_xticks(np.arange(board_shape[0] - extra_space, board_shape[2] + extra_space, 1))
    axs.set_yticks(np.arange(board_shape[1] - extra_space, board_shape[3] + extra_space, 1))

    axs.grid(True, which='both')
    return fig, axs


def __draw_shapes(grid: Grid, log_scale: bool = True):
    """
    Create the figures and draw the triangles with a color map.

    :param grid: The grid containing all triangles with their scores
    :return:
    """
    if log_scale:
        color_map = get_cmap('Spectral', lut=grid.get_max_score() + 1)
    else:
        color_map = get_cmap('Oranges', lut=grid.get_max_score() + 1)

    fig, axs = __draw_board(grid.get_grid_shape())

    norm = Normalize(vmin=0, vmax=grid.get_max_score() + 1)
    if log_scale:
        norm = LogNorm(vmin=1, vmax=grid.get_max_score() + 1)

    fig.colorbar(ScalarMappable(norm=norm, cmap=color_map), ax=axs)

    for t in grid.get_shapes():
        coordinates = t.get_coordinates(grid.side_lengths)
        shape = plt.Polygon(coordinates, facecolor=color_map(norm(t.get_score())))
        axs.add_patch(shape)
        # axs.text(*t.get_center(1.), '{}'.format(t.get_score()), fontsize=17)


def __show_save_visualization(show_vis: bool = True, save_vis: bool = True, vis_name: str = '', folder_name: str = ''):
    """
    Show the visualization and save the visualization as a png in folder folder/.

    :param show_vis: Show the visualization in a screen
    :param save_vis: Save the visualization to a file
    :param vis_name: The name of the visualization, which is also the name of the file
    :param folder_name: The name of the folder to put the figure in
    :return:
    """
    if save_vis:
        if not os.path.exists(f'figures/{folder_name}'):
            os.makedirs(f'figures/{folder_name}')
        # plt.title(vis_name)
        # plt.savefig(f'figures/{folder_name}/{vis_name}', dpi=300)
    if show_vis:
        if vis_name:
            plt.title(vis_name)
        plt.show()
    plt.close()


def visualize_layers(layers: Dict[str, Dict[str, str]], order: str):
    min_x: int = 1000000
    max_x: int = -1000000
    min_y: int = 1000000
    max_y: int = -1000000
    for coordinate, _ in layers.items():
        coordinate = coordinate.split('|')
        coordinate = tuple([int(c) for c in coordinate])
        x, y = transform_coordinate(coordinate)
        min_x = min(min_x, x)
        max_x = max(max_x, x)
        min_y = min(min_y, y)
        max_y = max(max_y, y)
    lines: List = []
    fig = plt.figure(figsize=[10, 9])
    ax = fig.add_axes([0, 0, 1, 1])
    for coordinate, orders in layers.items():
        coordinate = coordinate.split('|')
        coordinate = tuple([int(c) for c in coordinate])
        top_face: int = int(orders.get(order).split('|')[-1])
        coordinate_list = Triangle(*transform_coordinate(coordinate)).get_coordinates(1.0)
        if (top_face % 2) == 1:
            shape = plt.Polygon(coordinate_list, facecolor='grey')
            ax.add_patch(shape)
        if is_upside_down(coordinate):
            left_top = layers.get(f'{coordinate[0]-1}|{coordinate[1]-1}|{coordinate[2]}')
            if left_top is None or int(left_top.get(order).split('|')[-1]) != top_face:
                lines.append((coordinate_list[0][0], coordinate_list[1][0]))
                lines.append((coordinate_list[0][1], coordinate_list[1][1]))
                # plt.plot((coordinate_list[0][0]), coordinate_list[1])
            right_top = layers.get(f'{coordinate[0]-1}|{coordinate[1]}|{coordinate[2]+1}')
            if right_top is None or int(right_top.get(order).split('|')[-1]) != top_face:
                lines.append((coordinate_list[2][0], coordinate_list[1][0]))
                lines.append((coordinate_list[2][1], coordinate_list[1][1]))
                # plt.plot(coordinate_list[2], coordinate_list[1])
            up_top = layers.get(f'{coordinate[0]}|{coordinate[1]-1}|{coordinate[2]+1}')
            if up_top is None or int(up_top.get(order).split('|')[-1]) != top_face:
                lines.append((coordinate_list[0][0], coordinate_list[2][0]))
                lines.append((coordinate_list[0][1], coordinate_list[2][1]))
                # plt.plot(coordinate_list[0], coordinate_list[2])
        else:
            left_top = layers.get(f'{coordinate[0]+1}|{coordinate[1]}|{coordinate[2]-1}')
            if left_top is None or int(left_top.get(order).split('|')[-1]) != top_face:
                lines.append((coordinate_list[0][0], coordinate_list[1][0]))
                lines.append((coordinate_list[0][1], coordinate_list[1][1]))
                # plt.plot(coordinate_list[0], coordinate_list[1])
            right_top = layers.get(f'{coordinate[0]+1}|{coordinate[1]+1}|{coordinate[2]}')
            if right_top is None or int(right_top.get(order).split('|')[-1]) != top_face:
                lines.append((coordinate_list[2][0], coordinate_list[1][0]))
                lines.append((coordinate_list[2][1], coordinate_list[1][1]))
                # plt.plot(coordinate_list[2], coordinate_list[1])
            up_top = layers.get(f'{coordinate[0]}|{coordinate[1]+1}|{coordinate[2]-1}')
            if up_top is None or int(up_top.get(order).split('|')[-1]) != top_face:
                lines.append((coordinate_list[0][0], coordinate_list[2][0]))
                lines.append((coordinate_list[0][1], coordinate_list[2][1]))
                # plt.plot(coordinate_list[0], coordinate_list[2])
    ax.axis('equal')
    ax.plot(*lines, color='black')
    plt.show()
