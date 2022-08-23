def stable_student(drivers, students):
    flags = [1] * len(students)
    while sum(flags) > 0:
        for student in students:
            if not student.current_driver() is None:
                flags[students.index(student)] = 0
            else:
                driver = student.next_preference()
                if not driver.is_full():
                    driver.add_sorted_student(student)
                    continue
                if driver.is_better_student(student):
                    old_student = driver.remove_least_score_student()
                    driver.add_sorted_student(student)
                    flags[students.index(old_student)] = 1


def stable_driver(drivers, students):
    flags = [1] * len(drivers)
    while sum(flags) > 0:
        for driver in drivers:
            if driver.is_full():
                flags[drivers.index(driver)] = 0
            else:
                student = driver.next_preference()
                previous_driver = student.current_driver()
                if previous_driver is None:
                    driver.add_student(student)
                else:
                    if student.is_better_driver(driver):
                        previous_driver.remove_student(student)
                        driver.add_student(student)
                        if flags[drivers.index(previous_driver)] == 0:
                            flags[drivers.index(previous_driver)] = 1
