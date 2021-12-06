import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
from matplotlib.colors import CSS4_COLORS
from scipy import spatial
import numpy as np
from utils import get_center_coords


def coord_frequencies(array):
    freqs = {}
    for v1 in array:
        freq = 0
        for v2 in array:
            if spatial.distance.euclidean(v1, v2) == 0:
                freq += 1
        freqs[(v1[0], v1[1])] = freq
    return freqs


def plot_path(path, color):
    """
    path: List of Location
    """
    for i in range(len(path) - 1):
        x1, y1 = path[i + 1].get_coords()
        x2, y2 = path[i].get_coords()
        plt.annotate("", xy=(x1, y1), xytext=(x2, y2),
                     arrowprops=dict(width=0.01, shrink=0.05, headwidth=5, color=color))


def plot_frequencies(coords_array, x_offset, y_offset, color):
    freq_dict = coord_frequencies(coords_array)
    for x, y in coords_array:
        plt.annotate(freq_dict[(x, y)], (x, y), xytext=(x + x_offset, y + y_offset), c=color)


def plot_center(coords):
    plt.annotate("Center", coords, c='green')


def plot_map(paths, students, drivers, is_geographic_data):
    """
    paths: a list of lists of Location
    """
    center_coords = get_center_coords(is_geographic_data)
    student_coords = np.array([student.get_coords() for student in students])
    driver_coords = np.array([driver.get_coords() for driver in drivers])
    chosen_colors = ["red", "blue", "green", "yellow", "purple", "forestgreen", "black"]
    if len(paths) > len(chosen_colors):
        colors = list(CSS4_COLORS.keys())
        colors.remove("white")
        replace = True if len(paths) > len(colors) else False
        chosen_colors = np.random.choice(colors, size=len(paths), replace=replace)
    figure(figsize=(16, 12), dpi=80)
    if is_geographic_data:
        plot_frequencies(student_coords, 0.001, 0.001, "blue")
        plot_frequencies(driver_coords, -0.002, 0.001, "red")
    else:
        plot_frequencies(student_coords, 0.15, 0.1, "blue")
        plot_frequencies(driver_coords, -0.25, 0.1, "red")
    plt.scatter(student_coords[:, 0], student_coords[:, 1], marker='o', c='green')
    plt.scatter(driver_coords[:, 0], driver_coords[:, 1], c='red', marker='x')
    plot_center(center_coords)
    for i, path in enumerate(paths):
        plot_path(path, chosen_colors[i])
    plt.show()
    return plt
