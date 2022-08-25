from utils import *
from location import Location, distances_lookup_table
from person import Driver, Student
from algorithm import stable_student, stable_driver
from debug_numbers import print_scores_to_file
from boost import *
import time
from collections import Counter
from tqdm import tqdm
import math


def print_testing_data(drivers, students):
    for driver in drivers:
        print('Driver', driver)
        for student in driver.sorted_by_criterion(students, "student_dist_score"):
            print(f'{student.get_name()}: {round(driver.student_dist_score(student), 3)}')
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++")
    for student in students:
        print('Student', student)
        for driver in student.sorted_by_criterion(drivers, "driver_dist_score"):
            print(f'{driver.get_name()}: {round(student.driver_dist_score(driver), 3)}')
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++")
    for driver in drivers:
        print('Driver', driver)
        for student in driver.sorted_by_criterion(students, "dist_score"):
            print(f'{student.get_name()}: {round(driver.dist_score(student), 3)}')


def populate_dist_lookup_with_google(drivers, students):
    center_coords = drivers[0].center_coords
    center_loc = Location(center_coords[0], center_coords[1], center_coords)
    driver_locations = [driver.loc for driver in drivers]
    student_locations = [student.loc for student in students]
    for driver in tqdm(drivers):
        driver.loc.populate_dist_lookup_with_google(student_locations)
    center_loc.populate_dist_lookup_with_google(driver_locations)
    center_loc.populate_dist_lookup_with_google(student_locations)


def process_data(drivers_df, students_df, center_coords, consider_gates):
    drivers, students = read_data(drivers_df, students_df, center_coords)
    populate_dist_lookup_with_google(drivers, students)
    week_days = {"sa", "su", "mo", "tu", "we", "th"}
    student_columns = list(students_df.columns)
    # when number of students is small considering gates would result in bad pickups, so consider_gates is deactivated
    if len(students_df) < 200:
        consider_gates = False
        print("consider_gates was deactivated due to small number of students")
    if any(ele in week_days for ele in student_columns):  # if any of week days are in students columns
        # drivers, students = daily_matching(drivers, students, consider_gates, students_df)
        drivers, students = new_daily_matching(drivers, students, consider_gates, students_df)
    else:
        create_preferences(students, drivers, True, consider_gates, False, False)
        print_testing_data(drivers, students)
        drivers, students = apply_algorithm(students, drivers, consider_gates, print_to_scores_file=False)
        # drivers, students = remove_worst_drivers(drivers, students, consider_gates)
    return drivers, students


def read_data(drivers_df, students_df, center_coords):
    students_df['gate_group'] = (students_df['gate_group']).astype(np.int8)
    num_gates = int(students_df['gate_group'].max() + 1)
    drivers = []
    driver_names = []
    # drivers_df = drivers_df.sample(15, replace=False)  # randomly choose fraction of drivers for better testing
    for index, row in drivers_df.iterrows():
        drivers_id = index  # instead of row['id']
        x = row['x']
        y = row['y']
        phone = row["phone"]
        name = row['name'].strip()
        driver_names.append(name)
        district = row['district']
        loc = Location(x, y, center_coords)
        drivers.append(Driver(drivers_id, loc, center_coords, name, district, num_gates, phone))
    students = []
    # students_df = students_df.sample(60, replace=False)  # randomly choose fraction of students for better testing
    for index, row in students_df.iterrows():
        student_id = index  # instead of row['id']
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
        student = Student(student_id, loc, center_coords, leave_time, name, district, gate, phone, friend_names)
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


def daily_matching(drivers, students, consider_gates, students_df):
    """" daily matching when trying to keep same drivers for each student as much as possible """
    student_drivers = {}
    driver_students = {}
    students_per_day = {}
    for student in students:
        student_drivers[student.get_id()] = []
    for driver in drivers:
        driver_students[driver.get_id()] = []
    for day in ["sa", "su", "mo", "tu", "we", "th"]:
        day_students = []
        for i, val in enumerate(students_df[day].to_numpy()):
            if val == 1.0:
                day_students.append(students[i])
        create_preferences(day_students, drivers, True, consider_gates, False, False)
        drivers, day_students = apply_algorithm(day_students, drivers, consider_gates, print_to_scores_file=False)
        for driver in drivers:
            for student in driver.picked_students():
                student_drivers[student.get_id()].append(driver)
                driver_students[driver.get_id()].append(student)
                student.reset_calculations()
            driver.reset_calculations()
        students_per_day[day] = day_students
    create_preferences(students, drivers, True, consider_gates, False, False)
    for student_key, driver_list in student_drivers.items():
        student = students[student_key]
        driver_counts = dict(Counter(driver_list))
        # remove any driver not repeated at least two times
        keys_to_remove = []
        for key, val in driver_counts.items():
            if val < 2:
                keys_to_remove.append(key)
        for key in keys_to_remove:
            del driver_counts[key]
        # sort drivers by count
        ds = np.array(list(driver_counts.keys()))
        cs = np.array(list(driver_counts.values()))
        ds = list(ds[np.argsort(cs)])
        # update preferences
        preferences = student.get_preferences()
        for driver in ds:
            preferences.remove(driver)
            preferences.insert(0, driver)
    for driver_key, student_list in driver_students.items():
        driver = drivers[driver_key]
        student_counts = dict(Counter(student_list))
        # remove any student not repeated at least two times
        keys_to_remove = []
        for key, val in student_counts.items():
            if val < 2:
                keys_to_remove.append(key)
        for key in keys_to_remove:
            del student_counts[key]
        ss = np.array(list(student_counts.keys()))
        cs = np.array(list(student_counts.values()))
        ss = list(ss[np.argsort(cs)])
        preferences = driver.get_preferences()
        for student in ss:
            preferences.remove(student)
            preferences.insert(0, student)
    for day in ["sa", "su", "mo", "tu", "we", "th"]:
        day_students = students_per_day[day]
        for student in day_students:
            student.leave_driver()
            student.iterable_preferences = iter(student.preferences.copy())
        for driver in drivers:
            driver.set_picked_students([])
            driver.iterable_preferences = iter(driver.preferences.copy())
        drivers, day_students = apply_algorithm(day_students, drivers, consider_gates, print_to_scores_file=False)
        for driver in drivers:
            picked_students = driver.picked_students()
            driver.add_picked_students_weekly(day, picked_students)
            for student in picked_students:
                student.add_driver_weekly(day, driver)
    return drivers, students


def new_daily_matching(drivers, students, consider_gates, students_df):
    """ same as daily_matching but without trying to keep same drivers for students """
    for day in ["sa", "su", "mo", "tu", "we", "th"]:
        if day in list(students_df.columns):
            for driver in drivers:
                for student in driver.picked_students():
                    student.reset_calculations(False)
                driver.reset_calculations()
            day_students = []
            for i, val in enumerate(students_df[day].to_numpy()):
                if val == 1.0:
                    day_students.append(students[i])
            create_preferences(day_students, drivers, True, consider_gates, False, False)
            drivers, day_students = apply_algorithm(day_students, drivers, consider_gates, print_to_scores_file=False)
            for driver in drivers:
                picked_students = driver.picked_students()
                driver.add_picked_students_weekly(day, picked_students)
                for student in picked_students:
                    student.add_driver_weekly(day, driver)
    return drivers, students


def remove_worst_drivers(drivers, students, consider_gates):
    required_drivers = math.ceil(len(students)/4)
    if required_drivers < len(drivers):
        n_to_remove = len(drivers) - required_drivers
        print(f"{n_to_remove} extra drivers have been removed")
        scores = []
        for driver in drivers:
            scores.append(np.sum([driver.dist_score(student) for student in driver.students]))
        drivers = np.array(drivers)
        scores = np.array(scores)
        sorted_drivers = np.flip(drivers[np.argsort(scores)])
        drivers = sorted_drivers[:-n_to_remove]
        for driver in drivers:
            for student in driver.picked_students():
                student.reset_calculations(False)
            driver.reset_calculations()
        create_preferences(students, drivers, True, consider_gates, False, False)
        drivers, students = apply_algorithm(students, drivers, consider_gates, print_to_scores_file=False)
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
    print("Applying algorithm ...")
    t0 = time.time()
    # remove pre-picked students before applying the algorithm
    pre_picked_students = []
    for student in students:
        if student.current_driver() is not None:
            students.remove(student)
            pre_picked_students.append(student)
    for student in pre_picked_students:
        pre_driver = student.current_driver()
        student_pref = student.get_preferences()
        student_pref.remove(pre_driver)
        student_pref.insert(0, pre_driver)
        driver_pref = pre_driver.get_preferences()
        driver_pref.remove(student)
        driver_pref.insert(0, student)
    # the default algorithm is stable_student, but stable_driver will be used if below conditions were satisfied
    if len(drivers) <= len(students) / 4:
        algorithm = stable_driver
    else:
        algorithm = stable_student
    algorithm(drivers, students)
    # if len(drivers) < len(students) / 4:
    #     gate_weight = 0.2 if consider_gates else 0.0
    #     num_repetition = 10
    #     num_gates = len(drivers[0].gate_score_list)
    #     students, drivers = enhanced_by_dropping_worst(drivers, students, num_gates, gate_weight, num_repetition)
    # --------
    # gate_weight = 0.2 if consider_gates else 0.0
    # num_repetition = 10
    # num_gates = len(drivers[0].gate_score_list)
    # students, drivers = new_enhanced_by_dropping_worst(drivers, students, num_gates, gate_weight, num_repetition)
    # --------
    t1 = time.time()
    execution_time = t1 - t0
    print(f"\nTotal execution time = {round(execution_time, 2)} seconds")
    if print_to_scores_file:
        print_scores_to_file(students, drivers)
    return drivers, students


def statistics(students, drivers):
    num_gates = len(drivers[0].gate_score_list)
    stats = {}
    drivers_without_students = [driver for driver in drivers if len(driver.picked_students()) == 0]
    message_drivers_without_students = f"Empty Drivers  =  {len(drivers_without_students)}"
    stats['num_drivers_without_students'] = message_drivers_without_students
    drivers = [driver for driver in drivers if len(driver.picked_students()) > 0]
    drivers_not_full = [driver for driver in drivers if len(driver.picked_students()) < 4]
    message_drivers_not_full = f"Not Full Drivers  =  {len(drivers_not_full)}"
    stats['num_drivers_not_full'] = message_drivers_not_full
    # I removed unpicked_students because it causes a problem in weekly matching
    # unpicked_students = [student for student in students if student.driver is None]
    # message_unpicked_students = f"Unpicked Students  =  {len(unpicked_students)}"
    # stats['num_unpicked_students'] = message_unpicked_students
    # distance
    total_distance = get_total_distance(drivers)
    avg_distance = total_distance / len(drivers)
    message_total_dist = f"Total distance  =  {round(total_distance, 1)} km"
    message_avg_dist = f"Average distance  =  {round(avg_distance, 1)} km"
    stats['total_distance'] = message_total_dist
    stats['average_distance'] = message_avg_dist
    shortest_dist_driver = get_shortest_dist_driver(drivers)
    longest_dist_driver = get_longest_dist_driver(drivers)
    message_shortest_dist = \
        f"Shortest distance = {round(shortest_dist_driver.get_route()[1], 1)} km"
    message_longest_dist = \
        f"Longest distance = {round(longest_dist_driver.get_route()[1], 1)} km"
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
    message_more_gates = f"Drivers with more gates  =  {round(100*drivers_with_three_or_more_gates/len(drivers))} %"
    stats['one_gate'] = message_one_gate
    stats['two_gates'] = message_two_gates
    stats['more_gates'] = message_more_gates
    return stats
