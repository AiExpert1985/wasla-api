from models import *
from flask import render_template, jsonify, request
import json
from processing import *

db.init_app(app)


@app.route('/')
def home_page():
    return render_template('index.html')


@app.route('/algorithm', methods=['POST'])
def testfn():
    if request.method != 'POST':
        return "You must use POST method", 405
    key = request.form['api_key']
    # if key != "ksdjf34234a23423":
    #     return "You are not authorized", 404
    drivers_data = json.loads(request.form['drivers'])
    print(drivers_data)
    students_data = request.form['students']
    consider_gates = request.form['consider_gates']
    drivers, students = read_data(drivers_data, students_data)
    apply_algorithm(students, drivers, consider_gates, print_to_scores_file=False)
    return jsonify(successful="all were uploaded!")


if __name__ == "__main__":
    app.run(debug=True)
