import numpy as np


def get_center_coords(is_geographic_data):
    if is_geographic_data:
        return 43.146406822212754, 36.37665963355008
    else:
        return 0, 0


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


def routes(drivers, is_real_data):
    return [driver.get_route(is_real_data)[0] for driver in drivers]


def specific_route(drivers, driver_coords, is_real_data):
    for driver in drivers:
        if driver.get_coords() == driver_coords:
            return driver.get_route(is_real_data)[0]
    raise LookupError("Driver not found")


def get_shortest_path(drivers, is_real_data):
    distances = [driver.get_route(is_real_data)[1] for driver in drivers]
    idx = np.argmin(distances)
    return drivers[idx].get_route[0]


def get_longest_path(drivers, is_real_data):
    distances = [driver.get_route(is_real_data)[1] for driver in drivers]
    idx = np.argmax(distances)
    return drivers[idx].get_route(is_real_data)[0]


def get_total_distance(drivers, is_real_data):
    distance = 0
    for driver in drivers:
        distance += driver.get_route(is_real_data)[1]
    return round(distance, 2)


def get_total_time(drivers):
    return sum([driver.get_wait_time() for driver in drivers])


def get_shortest_dist_driver(drivers, is_real_data):
    idx = np.argmin([driver.get_route(is_real_data)[1] for driver in drivers])
    return drivers[idx]


def get_longest_dist_driver(drivers, is_real_data):
    idx = np.argmax([driver.get_route(is_real_data)[1] for driver in drivers])
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