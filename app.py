import json
from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import RadioField, StringField
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'key'
with app.app_context():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///base.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db = SQLAlchemy(app)

    class Teachers(db.Model):
        __tablename__ = 'teachers'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String, nullable=False)
        about = db.Column(db.String, nullable=False)
        rating = db.Column(db.Float, nullable=False)
        picture = db.Column(db.String, nullable=False)
        price = db.Column(db.Integer, nullable=False)
        lesson_time = db.Column(db.String)
        # Ссылка на поле в модели цели (One-to-Many)
        goals = db.relationship("Goals", back_populates="goal")
        # Ссылка на поле в модели рассписание (One-to-Many)
        week_day = db.relationship("TimetableTeachers", back_populates="week")

    class Goals(db.Model):
        __tablename__ = 'goals'
        id = db.Column(db.Integer, primary_key=True)
        key = db.Column(db.String, nullable=False)
        # Ссылка на модель преподавателя (One-to-Many)
        teachers_id = db.Column(db.Integer, db.ForeignKey("teachers.id"))
        goal = db.relationship("Teachers", back_populates="goals", uselist=False)

        # Ссылка на поле в модели подбора преподавателя (One-to-Many)
        search_teacher = db.relationship("SearchTeacher", back_populates="goal", uselist=False)

    class TimetableTeachers(db.Model):
        __tablename__ = 'timetables'
        id = db.Column(db.Integer, primary_key=True)
        day_times = db.Column(db.String, nullable=False)
        status = db.Column(db.Boolean, nullable=False)
        # ссылка на поле id в модели преподавателя (One-to-Many)
        teachers_id = db.Column(db.Integer, db.ForeignKey("teachers.id"))
        week = db.relationship("Teachers", back_populates="week_day", uselist=False)
        # ссылка на поле id в модели booking (One-to-Many)
        booking = db.relationship("Booking", back_populates='day_times', uselist=False)


    class SearchTeacher(db.Model):
        __tablename__ = 'search_teachers'
        id = db.Column(db.Integer, primary_key=True)
        how_time = db.Column(db.String(20), nullable=False)
        client_name = db.Column(db.String(25), nullable=False)
        client_phone = db.Column(db.String(10), nullable=False)
        # Ссылка на поле в модели цели (One-to-Many)
        goal_id = db.Column(db.Integer, db.ForeignKey("goals.id"))
        goal = db.relationship("Goals", back_populates="search_teacher", uselist=False)


    class Booking(db.Model):
        __tablename__ = 'booking'
        id = db.Column(db.Integer, primary_key=True)
        client_name = db.Column(db.String(25), nullable=False)
        client_phone = db.Column(db.String(10), nullable=False)
        # ссылка на поле id в модели Teachers (One-to-Many)
        timetable_id = db.Column(db.Integer, db.ForeignKey("timetables.id"))
        # ссылка на поле free и day в модели TimetableTeachers (One-to-One)
        day_times = db.relationship("TimetableTeachers", back_populates="booking", uselist=False)

    db.create_all()

    def add_record(name, about, rating, price, goal, lesson_time):
        teacher = Teachers(name=name, about=about, rating=rating, price=price, goal=goal, lesson_time=lesson_time)
        db.session.add(teacher)
        db.session.commit()
        return teacher.id # id нового преподавателя в БД

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
                                                          ('3', 'Для переезда'),
                                                          ('4', 'Для программирования')])
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
                        '3': 'Для переезда',
                        '4': 'Для программирования'}
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

