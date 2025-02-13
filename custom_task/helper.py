import json
import numpy as np
import os
import random
import copy


class NpEncoder(json.JSONEncoder):
    """Custom JSON encoder subclass to handle numpy data types."""

    def default(self, obj):
        if isinstance(obj, (np.integer, np.floating)):
            return obj.item()
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


def interleave_lists(lists):
    """
    Interleaves elements from a list of lists into a list of sublists, where each sublist contains
    one element from each of the input lists, in order.

    Parameters:
        lists (list of lists): List containing several sublists from which elements are interleaved.

    Returns:
        list: A list of sublists, each containing one element from each input sublist.
    """
    # Ensure all lists are mutable (not necessary unless lists are tuples or other immutable types)
    lists = [list(sublist) for sublist in lists]
    
    combined = []
    # Continue looping until all lists are exhausted
    while any(lists):  # any() is true if at least one list still has items
        sublist = []
        for sublist_index in range(len(lists)):
            if lists[sublist_index]:  # Check if the current sublist has any items left
                sublist.append(lists[sublist_index].pop(0))  # Pop the first element if available
        combined.append(sublist)
    return combined


def translate_to_coordinates(index):
    """Convert a linear index to a 4x4 grid coordinate."""
    return index % 4, index // 4


def initialize_output_directory(path):
    """Ensure the output directory exists; create if it does not."""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        
def select_items(item_dict, n_items):
    """
    Selects a random set of items from a given dictionary.

    Parameters:
        item_dict (dict): Dictionary where keys are tool names and values are another dictionary of items.
        n_items (int): Number of random items to select.

    Returns:
        list: List of tuples, each containing a tool and an item.
    """
    items = [(tool, item) for tool, items in item_dict.items() for item in items.keys()]
    return random.choices(items, k=n_items)


def sample_dict_item(dict):
    """Randomly select a key-value pair from a dictionary."""
    key = random.choice(list(dict.keys()))
    return dict[key]

def translate_to_coordinates(spot, width=4, depth=4, height=3):
        """
        Translate a 1D spot index to 3D coordinates.
        """
        z = spot // (width * depth)
        y = (spot % (width * depth)) // width
        x = spot % width
        return x, y, z

def is_block_accessible(x, y, z, grid):
    """
    Check if a block at (x, y, z) is accessible in a 3D grid.
    """
    if z > 0 and grid[x][y][z-1] == 0:
        return False  # No floating blocks allowed
    directions = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    for dx, dy, dz in directions:
        nx, ny, nz = x + dx, y + dy, z + dz
        if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and 0 <= nz < len(grid[0][0]):
            if grid[nx][ny][nz] == 0:
                return True
    return False

def will_block_previous(x, y, z, grid):
    """
    Check if placing a block at (x, y, z) will block any previous placements.
    """
    directions = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    for dx, dy, dz in directions:
        nx, ny, nz = x + dx, y + dy, z + dz
        if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and 0 <= nz < len(grid[0][0]):
            if grid[nx][ny][nz] == 1 and not is_block_accessible(nx, ny, nz, grid):
                return True
    return False

def hide_other(x, y, z, grid, base_shape):
    if base_shape == [2,3,2]:
        if x == 1 and y == 1 and z == 1:
            return True
        if x == 1 and y == 0 and z == 1:
            return True
    if base_shape == [2,2,2]:
        if x == 1 and y == 0 and z == 1:
            return True
    return False
    
    
def translate_to_index(x, y, z, width=4, depth=4, height=3):
    """
    Translate 3D coordinates (x, y, z) back to a 1D spot index.
    """
    return z * (width * depth) + y * width + x


def generate_playground_config(name, center, size=5):
    """
    Generate a configuration dictionary for a playground based on the given parameters.

    Parameters:
    name (str): The name of the playground location.
    center (list[int]): A list containing the x, y, and z coordinates of the center of the playground.
    size (int, optional): The size of the playground in both x and z directions. Default is 5x5.

    Returns:
    dict: A dictionary containing the playground configuration.
    """
    
    x, y, z = center
    half_size = size // 2
    
    config = {
        "name": name,
        "x": [x - half_size, x + half_size],
        "z": [z - half_size, z + half_size],
        "y": y,
        "bot_range": [[x + half_size + 1, x + half_size + 4], [z - half_size + 1, z + half_size + 4], y + 2],
        "center": [x, y, z]
    }
    
    return config
    
    
def generate_multiple_playgrounds(playgrounds):
    """
    Generate a dictionary containing multiple playground configurations.

    Parameters:
    playgrounds (list[tuple]): A list of tuples where each tuple contains a name (str), center (list[int]), 
                               and optional size (int) for the playground.

    Returns:
    dict: A dictionary mapping playground names to their configuration dictionaries.
    """
    return {name: generate_playground_config(name, center, size) for name, center, size in playgrounds}
