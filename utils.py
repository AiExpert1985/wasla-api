import numpy as np


def string_to_numeric_time(x):
    try:
        if len(x) > 5:
            x = x[:-3]
        hours = int(x[:-3])
        minutes = int(x[-2:]) / 60.0
        # if hours 1 to 6, then it will be considered as PM and converted 12 hours will be added
        if hours < 7.0:
            hours += 12.0
        numeric_time = hours + minutes
    except ValueError:
        numeric_time = 13.0
    return numeric_time


# def routes(drivers):
#     return [driver.get_route()[0] for driver in drivers]


def routes(drivers):
    all_routes = {}
    for driver in drivers:
        points = []
        for loc in driver.get_route()[0]:
            x, y = loc.get_coords()
            points.append({'lat': y, 'lng':x})
        all_routes[driver.get_name()] = points
    return all_routes


def specific_route(drivers, driver_coords):
    for driver in drivers:
        if driver.get_coords() == driver_coords:
            return driver.get_route()[0]
    raise LookupError("Driver not found")


def get_shortest_path(drivers):
    distances = [driver.get_route()[1] for driver in drivers]
    idx = np.argmin(distances)
    return drivers[idx].get_route[0]


def get_longest_path(drivers):
    distances = [driver.get_route()[1] for driver in drivers]
    idx = np.argmax(distances)
    return drivers[idx].get_route()[0]


def get_total_distance(drivers):
    distance = 0
    for driver in drivers:
        distance += driver.get_route()[1]
    return round(distance, 2)


def get_total_time(drivers):
    return sum([driver.get_wait_time() for driver in drivers])


def get_shortest_dist_driver(drivers):
    idx = np.argmin([driver.get_route()[1] for driver in drivers])
    return drivers[idx]


def get_longest_dist_driver(drivers):
    idx = np.argmax([driver.get_route()[1] for driver in drivers])
    return drivers[idx]


def get_shortest_time_driver(drivers):
    idx = np.argmin([driver.get_wait_time() for driver in drivers])
    return drivers[idx]


def get_longest_time_driver(drivers):
    idx = np.argmax([driver.get_wait_time() for driver in drivers])
    return drivers[idx]


def naive_probability(vector):
    return vector / np.sum(vector)


def softmax(vector):
    exp = np.exp(vector)
    return exp / np.sum(exp)


def min_max_scaling(vector):
    vector = np.array(vector)
    min_val = np.min(vector)
    max_val = np.max(vector)
    return (vector - min_val) / (max_val - min_val)


def squared_probability(vector):
    squared_values = np.square(vector)
    return squared_values/np.sum(squared_values)


def cubed_probability(vector):
    squared_values = np.power(vector, 3)
    return squared_values/np.sum(squared_values)


def power_4_probability(vector):
    squared_values = np.power(vector, 4)
    return squared_values/np.sum(squared_values)
