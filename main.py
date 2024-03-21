import flask
from flask import render_template
import requests
import datetime

app = flask.Flask(__name__)

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
    title = news[id-1]['title']
    text = news[id-1]['text']
    return render_template('news_details.html', title= title, text=text)


@app.route('/')
def index():
    return render_template("index.html", news=news)


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
