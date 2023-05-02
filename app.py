import json
from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import RadioField, StringField

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
def update_timetable_teacher(id_teacher, day, times, client_name, client_phone):
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
    with open('booking.json', 'r') as r:
        records = json.load(r)
        records.append([id_teacher, day, times, client_name, client_phone])
        r.close()
    with open('booking.json', 'w') as w:
        json.dump(records, w)
        w.close()

class RequestForm(FlaskForm):   # объявление класса формы для WTForms
    name = StringField('name')
    phone = StringField('phone')
    goal = RadioField("Какая цель занятий?", choices=[('0', 'Для путешествий'),
                                                      ('1', 'Для школы'),
                                                      ('2', 'Для работы'),
                                                      ('3', 'Для переезда')])
    time = RadioField("Сколько времени есть?",
                      choices=[('0', '1-2 часа в неделю'),
                               ('1', '3-5 часов в неделю'),
                               ('2', '5-7 часов в неделю'),
                               ('3', '7-9 часов в неделю')])

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
    form_request = RequestForm()  # Форма для страницы ('/request')
    return render_template("request.html", form=form_request, all_data=all_data)

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
    client_weekday = request.form["clientWeekday"]
    client_time = request.form["clientTime"]
    client_teacher = request.form["clientTeacher"]
    client_name = request.form["clientName"]
    client_phone = request.form["clientPhone"]

    # Обновляем расписание свободного времени репетитора
    update_timetable_teacher(client_teacher, client_weekday, client_time, client_name, client_phone)

    return render_template("booking_done.html", clientName=client_name, clientPhone=client_phone, clientTime=client_time,
                           clientTeacher=client_teacher, clientWeekday=client_weekday)
if __name__ == "__main__":
    app.run(debug=True)

