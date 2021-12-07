import pandas as pd
from utils import *
from location import Location
from person import Driver, Student
from algorithm import stable_student, stable_driver
import time
from debug_numbers import print_scores_to_file


def read_data(drivers_data, students_data):
    students_df = pd.DataFrame(students_data)
    drivers_df = pd.DataFrame(drivers_data)
    print(students_df.columns)
    is_real_data = True if 43 <= drivers_df['x'].mean() < 44 else False
    num_gates = students_df['gate_group'].max() + 1
    drivers = []
    driver_names = []
    center_coords = get_center_coords(is_real_data)
    for index, row in drivers_df.iterrows():
        x = row['x']
        y = row['y']
        name = row['name'].strip()
        driver_names.append(name)
        district = row['district']
        loc = Location(x, y, center_coords, is_real_data)
        drivers.append(Driver(loc, center_coords, name, district, num_gates))
    students = []
    for index, row in students_df.iterrows():
        x = row['x']
        y = row['y']
        leave_time = str(row['leave_time'])
        gate = row['gate_group']
        name = str(row['name']).strip()
        district = row['district']
        phone = row['phone']
        friend_names = [f.strip() for f in str(row['friends']).split('&')]
        loc = Location(x, y, center_coords, is_real_data)
        student = Student(loc, center_coords, leave_time, name, district, gate, phone, friend_names)
        students.append(student)
        # if already has driver name in the sheet, add student to that driver
        if 'driver' in students_df.columns:
            driver_name = str(row['driver']).strip()
            if (driver_name is not np.nan) and (driver_name in driver_names):
                idx = driver_names.index(driver_name)
                driver = drivers[idx]
                driver.add_student(student)
    # add friends by their names
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


def create_preferences(consider_dist, consider_gate, consider_time, consider_friends):
    global students
    global drivers
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
    create_preferences(consider_dist, consider_gates, consider_time, consider_friends)
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
        algorithm = stable_student()
    algorithm(drivers, students)
    # we must make sure all students will be included in visualization functions
    students += pre_picked_students
    t1 = time.time()
    execution_time = t1 - t0
    print(f"\nTotal execution time = {round(execution_time, 2)} seconds")

    if print_to_scores_file:
        print_scores_to_file(students, drivers)
