def print_scores_to_file(students, drivers):
    try:
        f = open('scores.txt', 'w')
        lines = ""
        for driver in drivers:
            lines += f"{driver}\n"
            lines += f"base_time = {round(driver.get_base_time(), 2)}\n"
            lines += f"wait time = {round(driver.get_wait_time(), 2)} hours\n"
            lines += f"{driver.picked_students()}\n"
            lines += ("x" * 40) + "\n\n"
        lines += "\n\n"
        for driver in drivers:
            lines += f"{driver} base_time = {round(driver.get_base_time(), 2)}\n"
            preferences = driver.get_preferences()
            for student in preferences:
                lines += f"{student} = {round(driver.final_score(student), 3)}\n"
            lines += ("o" * 40) + "\n\n"
        lines += "\n\n"
        for student in students:
            lines += f"{student}\n"
            preferences = student.get_preferences()
            for driver in preferences:
                lines += f"{driver} = {round(student.final_score(driver), 3)}\n"
            lines += ("#" * 40) + "\n\n"
        f.write(lines)
        f.close()
    except Exception as e:
        print("error during writing to scores file")
        print(e)