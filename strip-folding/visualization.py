from grid import Grid
from typing import Tuple
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap, ScalarMappable
from matplotlib.colors import Normalize, LogNorm
import numpy as np
import os


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
        plt.savefig(f'figures/{folder_name}/{vis_name}', dpi=300)
    if show_vis:
        if vis_name:
            plt.title(vis_name)
        plt.show()
    plt.close()
