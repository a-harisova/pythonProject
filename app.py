import json
from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField

app = Flask(__name__)

with open('data.json', 'r') as r:
    all_data = json.load(r)
    r.close()
for key in all_data[1]:
    if 'work' in key['goals']:
        print(key['name'])

@app.route('/') # главная
def render_main():
    return render_template("index.html", all_data=all_data)

@app.route('/teachers/') # все репетиторы
def render_teachers():
    return render_template("teachers.html", all_data=all_data)

@app.route('/goals/<goal>/') # здесь будет цель <goal>
def render_goals(goal):
    return render_template("goals.html", goal=goal, all_data=all_data)

@app.route('/profiles/<int:teacher_id>/') #  здесь будет преподаватель <id учителя>
def render_profiles(teacher_id):
    return render_template("profile.html", teacher_id=teacher_id, all_data=all_data)

@app.route('/request/') # здесь будет заявка на подбор
def render_request():
    return render_template("request.html")

@app.route('/request_done/') # заявка на подбор отправлена
def render_request_done():
    return render_template("request_done.html")

@app.route('/booking/<int:teacher_id>/<day>/<time>/') # здесь будет форма бронирования <id учителя>
def render_booking(teacher_id, day, time):
    return render_template("booking.html")

@app.route('/booking_done/') # заявка отправлена
def render_booking_done():
    return render_template("booking_done.html")

if __name__ == "__main__":
    app.run(debug=True)

