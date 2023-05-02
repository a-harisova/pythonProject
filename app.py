import json
from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import RadioField, TextAreaField

app = Flask(__name__)
app.secret_key = 'key'

with open('data.json', 'r') as r:
    all_data = json.load(r)
    r.close()

# Запись нового запроса в файл all_requests.json
def add_request(name, phone, goal, times):
    with open('all_requests.json', 'r') as r:
        records = json.load(r)
    records.append({'name': name, 'phone': phone, 'goal': goal, 'times': times})
    r.close()
    with open('all_requests.json', 'w') as w:
        json.dump(records, w)
    w.close()

# Запись нового брони в файл data.json
def update_timetable_teacher(id_teacher, day, times):
    with open('data.json', 'r') as r:
        records = json.load(r)
        records[1][int(id_teacher)]['free'][day][times] = False
        r.close()

    with open('data.json', 'w') as w:
        json.dump(records, w)
        w.close()
    with open('data.json', 'r') as r:
        global all_data
        all_data = json.load(r)
        r.close()

def update_data():
    with open('data.json', 'r') as r:
        global all_data
        all_data = json.load(r)
        r.close()

update_data()
class RequestForm(FlaskForm):   # объявление класса формы для WTForms
    name = TextAreaField('name')
    phone = TextAreaField('phone')
    goal = RadioField("Какая цель занятий?", choices=[('0', 'Для путешествий'),
                                                      ('1', 'Для школы'),
                                                      ('2', 'Для работы'),
                                                      ('3', 'Для переезда')])
    time = RadioField("Сколько времени есть?",
                      choices=[('0', '1-2 часа в неделю'),
                               ('1', '3-5 часов в неделю'),
                               ('2', '5-7 часов в неделю'),
                               ('3', '7-10 часов в неделю')])

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
    ReqForm = RequestForm()  # Форма для страницы ('/request')
    return render_template("request.html", form=ReqForm, all_data=all_data)

@app.route('/request_done/', methods=['POST'])  # заявка на подбор отправлена
def render_request_done():
    form = RequestForm()
    name = form.name.data
    phone = form.phone.data
    goal = form.goal.data
    times = form.time.data

    goal_choices = {'0': 'Для путешествий',
                    '1': 'Для школы',
                    '2': 'Для работы',
                    '3': 'Для переезда'}
    time_choices = {'0': '1-2 часа в неделю',
                    '1': '3-5 часов в неделю',
                    '2': '5-7 часов в неделю',
                    '3': '7-10 часов в неделю'}

    add_request(name, phone, goal_choices[goal], time_choices[times])
    return render_template("request_done.html", username=name, userphone=phone, goal=goal_choices[goal],
                           time=time_choices[times])

@app.route('/booking/<int:teacher_id>/<day>/<time>/') # здесь будет форма бронирования <id учителя>
def render_booking(teacher_id, day, time):
    return render_template("booking.html", teacher_id=teacher_id, day=day, time=time, all_data=all_data)

@app.route('/booking_done/', methods=['POST']) # заявка отправлена
def render_booking_done():
    clientWeekday = request.form["clientWeekday"]
    clientTime = request.form["clientTime"]
    clientTeacher = request.form["clientTeacher"]
    clientName = request.form["clientName"]
    clientPhone = request.form["clientPhone"]

    update_timetable_teacher(clientTeacher, clientWeekday, clientTime)  # Обновляем расписание свободного времени репетитора
    update_data()
    return render_template("booking_done.html", clientName=clientName, clientPhone=clientPhone, clientTime=clientTime,
                           clientTeacher=clientTeacher, clientWeekday=clientWeekday)
if __name__ == "__main__":
    app.run(debug=True)

