import numpy as np


def driver_num_gates(students, num_gates):
    gates = [0] * num_gates
    for student in students:
        gates[student.get_gate_group()] = 1
    return sum(gates)


def gate_students_ratio(students, num_gates):
    """" this function is used by other code to give added students better weight if they join majority group
     when there are only two groups and total number of gates is not changed """
    gates = [0] * num_gates
    for student in students:
        gates[student.get_gate_group()] += 1
    gates = sorted(gates, reverse=True)
    ratio = gates[0] if gates[1] == 0 else gates[0]/gates[1]
    return ratio


def dist_student_to_be_deleted(driver, student, num_gates, gate_weight):
    picked_students = driver.picked_students().copy()
    num_gates_before = driver_num_gates(picked_students, num_gates)
    picked_students.remove(student)
    num_gates_after = driver_num_gates(picked_students, num_gates)
    distance = driver.distance_to_center_through(student)
    # if removing student improve driver_num_gates, then we give it bad weight (increase his distance)
    if num_gates_after < num_gates_before:
        distance *= 1 + gate_weight
    return distance


def dist_student_to_be_added(driver, student, num_gates, gate_weight):
    picked_students = driver.picked_students().copy()
    num_gates_before = driver_num_gates(picked_students, num_gates)
    picked_students.append(student)
    num_gates_after = driver_num_gates(picked_students, num_gates)
    distance = driver.distance_to_center_through(student)
    # if adding student worsen driver_num_gates, then we give it bad weight (increase his distance)
    if num_gates_after > num_gates_before:
        distance *= 1.0 + gate_weight
    # if student gate is same as majority, reduce his distance a little
    elif gate_students_ratio(picked_students, num_gates) == 3 and gate_weight != 0:
        distance *= (1.0 - (gate_weight / 2.5))
    return distance


def drop_worst_student(driver, num_gates, gate_weight):
    """return worst student in driver based on distance and number of gates in that driver"""
    worst_student = None
    worst_distance = 0
    for student in driver.picked_students():
        distance = dist_student_to_be_deleted(driver, student, num_gates, gate_weight)
        if distance > worst_distance:
            worst_distance = distance
            worst_student = student
    driver.remove_student(worst_student)
    return worst_student


def set_new_preferences(driver, unpicked_students, num_gates, gate_weight):
    students = np.array(unpicked_students)
    sorted_by_dist = [dist_student_to_be_added(driver, student, num_gates, gate_weight) for student in students]
    sorted_by_dist = np.array(sorted_by_dist)
    sorted_students = students[np.argsort(sorted_by_dist)]
    driver.preferences = sorted_students
    driver.iterable_preferences = iter(driver.preferences.copy())


def enhanced_by_dropping_worst(drivers, students, num_gates, gate_weight, num_repetition):
    for _ in range(num_repetition):
        unpicked_students = [student for student in students if student.current_driver() is None]
        satisfaction_flags = [1] * len(drivers)  # drivers become satisfied (flag=0) only when they find a student
        selected_students = [None] * len(drivers)  # each driver add idx of student chosen (conflicts to be solved)
        for driver in drivers:
            if len(driver.picked_students()) == 0:
                continue
            worst_student = drop_worst_student(driver, num_gates, gate_weight)
            unpicked_students.append(worst_student)
        for driver in drivers:
            set_new_preferences(driver, unpicked_students, num_gates, gate_weight)
        while sum(satisfaction_flags) > 0:
            for i, driver in enumerate(drivers):
                if satisfaction_flags[i] == 0:
                    continue
                candidate_student = driver.next_preference()
                if candidate_student not in selected_students:
                    satisfaction_flags[i] = 0
                    selected_students[i] = candidate_student
                else:
                    j = selected_students.index(candidate_student)
                    dist_to_new_driver = dist_student_to_be_added(driver, candidate_student, num_gates, gate_weight)
                    dist_to_old_driver = dist_student_to_be_added(drivers[j], candidate_student, num_gates, gate_weight)
                    if dist_to_new_driver < dist_to_old_driver:
                        satisfaction_flags[i] = 0
                        selected_students[i] = candidate_student
                        satisfaction_flags[j] = 1
                        selected_students[j] = None
        for i, driver in enumerate(drivers):
            driver.add_student(selected_students[i])
    return students, drivers


def new_enhanced_by_dropping_worst(drivers, students, num_gates, gate_weight, num_repetition):
    for _ in range(num_repetition):
        unpicked_students = [student for student in students if student.current_driver() is None]
        satisfaction_flags = [1] * len(drivers)  # drivers become satisfied (flag=0) only when they find a student
        selected_students = [None] * len(drivers)  # each driver add idx of student chosen (conflicts to be solved)
        for driver in drivers:
            if len(driver.picked_students()) == 0:
                continue
            worst_student = drop_worst_student(driver, num_gates, gate_weight)
            unpicked_students.append(worst_student)
        for driver in drivers:
            set_new_preferences(driver, unpicked_students, num_gates, gate_weight)
        while sum(satisfaction_flags) > 0:
            for i, driver in enumerate(drivers):
                if satisfaction_flags[i] == 0:
                    continue
                # if driver checked all students and cant get one, then its satisfaction flag is raised
                try:
                    candidate_student = driver.next_preference()
                except:
                    satisfaction_flags[i] = 0
                    continue
                if candidate_student not in selected_students:
                    satisfaction_flags[i] = 0
                    selected_students[i] = candidate_student
                else:
                    j = selected_students.index(candidate_student)
                    dist_to_new_driver = dist_student_to_be_added(driver, candidate_student, num_gates, gate_weight)
                    dist_to_old_driver = dist_student_to_be_added(drivers[j], candidate_student, num_gates, gate_weight)
                    if dist_to_new_driver < dist_to_old_driver:
                        satisfaction_flags[i] = 0
                        selected_students[i] = candidate_student
                        satisfaction_flags[j] = 1
                        selected_students[j] = None
        for i, driver in enumerate(drivers):
            if selected_students[i] is not None:
                driver.add_student(selected_students[i])
    return students, drivers
