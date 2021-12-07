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
    if request.method == 'POST':
        drivers = request.form['drivers']
        students = request.form['students']
        gates = request.form['gates']
        boost = request.form['boost']
        print(gates, 'gates')
        print(boost, 'boost')
        return jsonify(successful="all were uploaded!")


if __name__ == "__main__":
    app.run(debug=True)
