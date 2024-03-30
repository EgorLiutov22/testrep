import flask
from flask import render_template, url_for, redirect
import requests
import datetime

from flask_sqlalchemy import SQLAlchemy

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, EmailField, SelectField, SubmitField
from  wtforms.validators import DataRequired, Optional

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'SECRET_KEY'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

db = SQLAlchemy(app)

news = [{'title': 'Удивительное событие в школе',
         'text': 'Вчера в местной школе произошло удивительное событие - все '
                 'ученики одновременно зевнули на уроке математики. '
                 'Преподаватель был так поражен этим коллективным зевком, '
                 'что решил отменить контрольную работу.'},
        {'title': 'Случай в зоопарке',
         'text': 'В зоопарке города произошел необычный случай - ленивец '
                 'решил не лениться и взобрался на самое высокое дерево в '
                 'своем вольере. Посетители зоопарка были поражены такой '
                 'активностью и начали снимать ленивца на видео. В итоге он '
                 'получил свой собственный канал на YouTube, где он размещает '
                 'свои приключения.'},
        {'title': 'Самый красивый пёс',
         'text': 'Сегодня в парке прошел необычный конкурс - "Самый красивый '
                 'пёс". Участники конкурса были так красивы, что судьи не '
                 'могли выбрать победителя. В итоге, конкурс был объявлен '
                 'ничейным, а участники получили награды за участие, '
                 'в том числе - пакетики конфет и игрушки в виде косточек. '
                 'Конкурс вызвал большой интерес у посетителей парка, '
                 'и его решили повторить в более масштабном формате.'}]


class Feedback(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(127), nullable=False)
    text = db.Column(db.Text(), nullable=False)
    email = db.Column(db.String(127), nullable=False)
    rating = db.Column(db.Integer())

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    news = db.relationship('News', back_populates='category')

    def __repr__(self):
        return f'Category {self.id}: ({self.title})'

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=True, nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    category = db.relationship('Category', back_populates='news')

    def __repr__(self):
        return f'News {self.id}: ({self.title[:20]}...)'

with app.app_context():
    db.create_all()

def get_categories():
    c = Category.query.all()
    return [(category.id, category.title) for category in c]


class Opinion(FlaskForm):
    name = StringField('Имя', validators=[DataRequired(message="Поле не должно быть пустым")])
    text = TextAreaField('Текст отзыва',
                         validators=[DataRequired(message="Поле не должно быть пустым")])
    email = EmailField('Ваш email', validators=[Optional()])
    rating = SelectField('Ваша оценка?', choices=[1, 2, 3, 4, 5])
    submit = SubmitField('Отправить')


class AddNews(FlaskForm):
    name = StringField('Заголовок', validators=[DataRequired(message="Поле не должно быть пустым")])
    message = TextAreaField('Текст новости', validators=[DataRequired(message="Поле не должно быть пустым")])
    category = SelectField(choices=get_categories())
    submit = SubmitField('Отправить')


def isPrime(n):
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n and n % d != 0:
        d += 2
    return d * d > n


def get_primes(n):
    res = []
    i = 1
    while len(res) < n:
        if isPrime(i):
            res.append(str(i))
        i += 1
    return ' '.join(res)


def get_course():
    response = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()
    result = ''
    print(response['Valute'])
    for _, data in response['Valute'].items():
        result += f'{data["Nominal"]} {data["Name"]} стоит {data["Value"]} руб.<br>'
    return result


def get_date_or_time(mode):
    dt = datetime.datetime.now()
    if mode == 'date':
        return f'<h1>Текущая дата: {dt.strftime("%d.%m.%Y")}</h1>'
    elif mode == 'time':
        return f'<h1>Текущее время: {dt.strftime("%H:%M")}</h1>'
    else:
        return '<h1>Простите, но я вас не понимать.</h1>'


@app.route('/news/<int:id>/')
def news_detail(id):
    title = news[id - 1]['title']
    text = news[id - 1]['text']
    return render_template('news_details.html', title=title, text=text)


@app.route('/add_news', methods=['GET', 'POST'])
def add_news():
    form = AddNews()
    chat_messages = []
    if form.validate_on_submit():
        name = form.name.data
        message = form.message.data
        chat_messages.append({'name': name, 'message': message})
        news.category_id = form.category.data

        return redirect(url_for('index'))
    return render_template('add_news.html',
                           chat_messages=chat_messages,
                           form=form)


@app.route('/')
def index():
    form = Opinion()
    chat_messages = []
    feedbacks = Feedback.query.all()
    categories = Category.query.all()
    if form.validate_on_submit():
        feedback = Feedback(
            name=form.name.data,
            text=form.text.data,
            email=form.email.data,
            rating=form.rating.data)
        db.session.add(feedback)
        db.session.commit()
        return redirect(url_for('chat'))
    return render_template('index.html',
                           chat_messages=chat_messages,
                           form=form, categories=categories)


@app.route('/category/<int:id>')
def news_in_category(id):
    c = Category.query.get(id)
    news = c.news
    name = c.tiltle
    categories = Category.query.all()
    return render_template('category.html',
                           news=news,
                           category_name=name,
                           categories=categories)

@app.route('/total/<int:a>/<int:b>')
def total(a, b):
    return f'Сумма {a + b}'


@app.route("/money")
def money():
    return get_course()


@app.route('/<int:a>/<string:operation>/<int:b>')
def get_date_or_time(a, operation, b):
    if operation == '+':
        return f'<h1>{a + b}</h1>'
    elif operation == '-':
        return f'<h1>{a - b}</h1>'
    elif operation == '*':
        return f'<h1>{a * b}</h1>'
    elif operation == ':':
        return f'<h1>{a / b}</h1>' if b != 0 else '<h1>Ошибка</h1>'
    else:
        return '<h1>Простите, но я вас не понимать.</h1>'


# @app.route('/prime/<int:n>')
# def primes(n):
#     return get_primes(n)
app.add_url_rule('/prime/<int:n>', view_func=get_primes)
app.add_url_rule('/<mode>', 'datetime', get_date_or_time)

if __name__ == '__main__':
    app.run()
