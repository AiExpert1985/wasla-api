from models import *
from flask import render_template, jsonify, request

db.init_app(app)


@app.route('/')
def home_page():
    example_embed = 'This string is from python'
    return render_template('index.html', embed=example_embed)


@app.route("/algorithm")
def algorithm():
    print("hi")
    return jsonify(student_id=33, driver_id=42)


@app.route('/test', methods=['POST'])
def testfn():
    if request.method != 'POST':
        return "You must use POST method", 405
    data = request.get_json()
    key = data['api_key']
    if key != "ksdjf34234a23423":
        return "You are not authorized", 404
    drivers = data['drivers']
    students = data['students']
    consider_gates = data['consider_gates']
    consider_boost = data['consider_boost']
    return jsonify(successful="all were uploaded!")


if __name__ == "__main__":
    app.run(debug=True)
