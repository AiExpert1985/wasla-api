import pandas as pd
from utils import *
from location import Location
from person import Driver, Student
from algorithm import stable_student, stable_driver
import time
from debug_numbers import print_scores_to_file
from boost import enhanced_by_dropping_worst


def read_data(drivers_data, students_data, center_coords):
    students_df = pd.DataFrame(students_data)
    drivers_df = pd.DataFrame(drivers_data)
    num_gates = students_df['gate_group'].max() + 1
    drivers = []
    driver_names = []
    drivers_df = drivers_df.sample(30, replace=False)  # randomly choose 50 drivers for better testing
    for index, row in drivers_df.iterrows():
        id = row['id']
        x = row['x']
        y = row['y']
        name = row['name'].strip()
        driver_names.append(name)
        district = row['district']
        loc = Location(x, y, center_coords)
        drivers.append(Driver(id, loc, center_coords, name, district, num_gates))
    students = []
    students_df = students_df.sample(150, replace=False)  # randomly choose 50 drivers for better testing
    for index, row in students_df.iterrows():
        id = row['id']
        x = row['x']
        y = row['y']
        leave_time = str(row['leave_time'])
        gate = row['gate_group']
        name = str(row['name']).strip()
        district = row['district']
        phone = row['phone']
        if 'friends' in students_df.columns:
            friend_names = [f.strip() for f in str(row['friends']).split('&')]
        else:
            friend_names = ""
        loc = Location(x, y, center_coords)
        student = Student(id, loc, center_coords, leave_time, name, district, gate, phone, friend_names)
        students.append(student)
        # if already has driver name in the sheet, add student to that driver
        if 'driver' in students_df.columns:
            driver_name = str(row['driver']).strip()
            if (driver_name is not np.nan) and (driver_name in driver_names):
                idx = driver_names.index(driver_name)
                driver = drivers[idx]
                driver.add_student(student)
    if 'friends' in students_df.columns:
        student_names = []
        for student in students:
            student_names.append(student.get_name())
        for student in students:
            for friend_name in student.get_friend_names():
                if not friend_name == "":
                    idx = student_names.index(friend_name)
                    friend = students[idx]
                    if friend not in student.get_friends():
                        student.add_friend(friend)
                    if student not in friend.get_friends():
                        friend.add_friend(student)
    return drivers, students


def create_preferences(students, drivers, consider_dist, consider_gate, consider_time, consider_friends):
    for driver in drivers:
        driver.calculate_student_dist_scores(students)
    for student in students:
        student.calculate_driver_dist_scores(drivers)
    for driver in drivers:
        driver.set_preferences(students, consider_dist, consider_gate, consider_time, consider_friends)
    for student in students:
        student.set_preferences(drivers)


def apply_algorithm(students, drivers, consider_gates, print_to_scores_file=False):
    t0 = time.time()
    consider_dist = True
    consider_time = False
    consider_friends = False
    create_preferences(students, drivers, consider_dist, consider_gates, consider_time, consider_friends)
    # remove pre-picked students before applying the algorithm
    pre_picked_students = []
    for student in students:
        if student.current_driver() is not None:
            students.remove(student)
            pre_picked_students.append(student)
    # the default algorithm is stable_student, but stable_driver will be used if below conditions were satisfied
    if len(drivers) <= len(students) / 4:
        algorithm = stable_driver
    else:
        algorithm = stable_student
    algorithm(drivers, students)
    if len(drivers) < len(students) / 4:
        gate_weight = 0.2 if consider_gates else 0.0
        num_repetition = 10
        num_gates = len(drivers[0].gate_score_list)
        students, drivers = enhanced_by_dropping_worst(drivers, students, num_gates, gate_weight, num_repetition)
    t1 = time.time()
    execution_time = t1 - t0
    print(f"\nTotal execution time = {round(execution_time, 2)} seconds")
    if print_to_scores_file:
        print_scores_to_file(students, drivers)
    return students, drivers


def statistics(students, drivers):
    num_gates = len(drivers[0].gate_score_list)
    stats = {}
    drivers_without_students = [driver for driver in drivers if len(driver.picked_students()) == 0]
    message_drivers_without_students = f"Drivers with no students  =  {len(drivers_without_students)}"
    stats['num_drivers_without_students'] = message_drivers_without_students
    drivers = [driver for driver in drivers if len(driver.picked_students()) > 0]
    drivers_not_full = [driver for driver in drivers if len(driver.picked_students()) < 4]
    message_drivers_not_full = f"Drivers with less than 4 students  =  {len(drivers_not_full)}"
    stats['num_drivers_not_full'] = message_drivers_not_full
    unpicked_students = [student for student in students if student.driver is None]
    message_unpicked_students = f"Unpicked students  =  {len(unpicked_students)}"
    stats['num_unpicked_students'] = message_unpicked_students
    # distance
    total_distance = get_total_distance(drivers)
    avg_distance = total_distance / len(drivers)
    message_total_dist = f"Total distance  =  {round(total_distance, 2)} km"
    message_avg_dist = f"Average distance per driver  =  {round(avg_distance, 2)} km"
    stats['total_distance'] = message_total_dist
    stats['average_distance'] = message_avg_dist
    shortest_dist_driver = get_shortest_dist_driver(drivers)
    longest_dist_driver = get_longest_dist_driver(drivers)
    message_shortest_dist = \
        f"Shortest distance = {round(shortest_dist_driver.get_route()[1], 2)} km : {shortest_dist_driver.get_name()}"
    message_longest_dist = \
        f"Longest distance = {round(longest_dist_driver.get_route()[1], 2)} km: {longest_dist_driver.get_name()}"
    stats['shorted_distance'] = message_shortest_dist
    stats['longest_distance'] = message_longest_dist
    # # time
    # total_time = get_total_time(drivers)
    # avg_time = total_time / len(drivers)
    # message_total_time = f"Total waiting time = {round(total_time, 2)} hrs"
    # message_avg_time = f"Average time per driver = {round(avg_time, 2)} hrs"
    # stats['total_time'] = message_total_time
    # stats['average_time'] = message_avg_time
    # lease_time_driver = get_shortest_time_driver(drivers)
    # most_time_driver = get_longest_time_driver(drivers)
    # message_shortest_time = \
    #     f"Shortest waiting time = {round(lease_time_driver.get_wait_time(), 2)} hrs: {lease_time_driver.get_name()}"
    # message_longest_time = \
    #     f"longest waiting time = {round(most_time_driver.get_wait_time(), 2)} hrs: {most_time_driver.get_name()}"
    # stats['shortest_time'] = message_shortest_time
    # stats['longest_time'] = message_longest_time
    # gates
    drivers_with_single_gate = 0
    drivers_with_one_gate = 0
    drivers_with_three_or_more_gates = 0
    for driver in drivers:
        gates = [0] * num_gates
        for student in driver.picked_students():
            gates[student.get_gate_group()] = 1
        if sum(gates) == 1:
            drivers_with_single_gate += 1
        elif sum(gates) == 2:
            drivers_with_one_gate += 1
        else:
            drivers_with_three_or_more_gates += 1
    message_one_gate = f"Drivers with one gate  =  {round(100*drivers_with_single_gate/len(drivers))} %"
    message_two_gates = f"Drivers with two gates  =  {round(100*drivers_with_one_gate/len(drivers))} %"
    message_more_gates = f"Drivers with 3 or more gates  =  {round(100*drivers_with_three_or_more_gates/len(drivers))} %"
    stats['one_gate'] = message_one_gate
    stats['two_gates'] = message_two_gates
    stats['more_gates'] = message_more_gates
    return stats
