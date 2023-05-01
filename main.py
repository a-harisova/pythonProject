from flask import Flask

app = Flask(__name__)

@app.route('/')
def render_main():
    return "здесь будет главная"

@app.route('/teachers/')
def render_teachers():
    return "здесь будут преподаватели"

@app.route('/goals/<string:goal>/')
def render_goals(goal):
    return "здесь будет цель <goal>"

@app.route('/profiles/<int:teacher_id>/')
def render_profiles(teacher_id):
    return "здесь будет преподаватель <id учителя>"

@app.route('/request/')
def render_request():
    return "здесь будет заявка на подбор"

@app.route('/request_done/')
def render_request_done():
    return "заявка на подбор отправлена"

@app.route('/booking/<int:teacher_id>/<day>/<time>/')
def render_booking(teacher_id, day, time):
    return "здесь будет форма бронирования <id учителя>"

@app.route('/booking_done/')
def render_booking_done():
    return "заявка отправлена"

if __name__ == "__main__":
    app.run(debug=True)

