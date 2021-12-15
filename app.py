from models import *
from flask import render_template, jsonify, request
import json
from processing import *

db.init_app(app)


@app.route('/')
def home_page():
    return render_template('index.html')


@app.route('/algorithm/data', methods=['POST'])
def algorithm_data():
    if request.method != 'POST':
        return "You must use POST method", 405
    data = request.get_json()
    key = data['api_key']
    if key != "ksdjf34234a23423":
        return "You are not authorized", 404
    drivers_data = json.loads(data['drivers'])
    students_data = json.loads(data['students'])
    consider_gates = data['consider_gates']
    center_coords = data['center_coords']
    drivers, students = read_data(drivers_data, students_data, center_coords)
    apply_algorithm(students, drivers, consider_gates, print_to_scores_file=False)
    stats = statistics(students, drivers)
    serialized_drivers = [driver.serialize() for driver in drivers]
    return jsonify(stats=stats, drivers=serialized_drivers)


if __name__ == "__main__":
    app.run(debug=True)
