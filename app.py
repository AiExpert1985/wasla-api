from flask import Flask, render_template, jsonify, request
from processing import *
import pandas as pd

app = Flask(__name__)


@app.route('/')
def home_page():
    return render_template("index.html")


@app.route('/eshtirakat/algorithm/data', methods=['POST'])
@app.route('/algorithm/data', methods=['POST'])
def algorithm_data():
    if request.method != 'POST':
        return "You must use POST method", 405
    data = request.get_json()
    key = data['api_key']
    if key != "ks2drf34234b":
        return "You are not authorized", 404
    drivers_data = data['drivers']
    students_data = data['students']
    consider_gates = data['consider_gates']
    center_coords = data['center_coords']
    students_df = pd.DataFrame(students_data)
    students_df.dropna(subset=["name"], inplace=True)  # drop rows with no student name
    drivers_df = pd.DataFrame(drivers_data)
    drivers_df.dropna(subset=["name"], inplace=True)  # drop rows with no driver name
    drivers, students = process_data(drivers_df, students_df, center_coords, consider_gates)
    # next two lines to check whether its daily or weekly
    student_columns = list(students_df.columns)
    mask = np.array([ele in {"sa", "su", "mo", "tu", "we", "th"} for ele in student_columns])
    week_days = list(np.array(list(student_columns))[mask])
    if any(mask):
        serialized_students = [student.serialize_weekly() for student in students]
        serialized_drivers = [driver.serialize_weekly() for driver in drivers]
        stats = {}
        for day in week_days:
            for driver in drivers:
                day_students = driver.picked_students_weekly_on(day)
                driver.set_picked_students(day_students)
            stats[day] = statistics(students, drivers)
        result = jsonify(students=serialized_students, drivers=serialized_drivers,
                         daily=True, stats=stats, week_days=week_days)
    else:
        serialized_drivers = [driver.serialize() for driver in drivers]
        stats = statistics(students, drivers)
        result = jsonify(stats=stats, drivers=serialized_drivers, daily=False)
    return result


if __name__ == "__main__":
    app.run()
