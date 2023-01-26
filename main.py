from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
import datetime
import random
import string


DATE = datetime.date.today()
LINK_ID_LENGTH = 5


app = Flask(__name__)
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = '4tj5z0v5tuj3uk4y8zr4ezb45'
db = SQLAlchemy(app)
app.app_context().push()


def generate_id():
    letters = string.ascii_lowercase
    shorted_link = ''.join(random.choice(letters) for i in range(LINK_ID_LENGTH))
    if LinkData.query.filter_by(shorted_link=shorted_link).first():
        generate_id()
    return shorted_link


class LinkData(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    link = db.Column(db.String(250), unique=True, nullable=False)
    shorted_link = db.Column(db.String(15), unique=True, nullable=False)
    creation_date = db.Column(db.String(15), nullable=False)
    num_visits = db.Column(db.Integer, nullable=False)


db.create_all()


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        short_link = generate_id()
        link_input = request.form.get('grablink')
        if request.form.get('grablink') == "":
            flash('it seems like you forgot to paste your link')
            return redirect(url_for('home'))
        if LinkData.query.filter_by(link=link_input).first():
            existing_url = LinkData.query.filter_by(link=link_input).first()
            return render_template('index.html', shorted_link=f"{request.url}{existing_url.shorted_link}")
        add_link = LinkData(
            link=link_input,
            shorted_link=short_link,
            creation_date=DATE,
            num_visits=0
        )
        db.session.add(add_link)
        db.session.commit()
        final_link = f"{request.url}{short_link}"
        return render_template('index.html', shorted_link=final_link)
    return render_template('index.html', shorted_link="")


@app.route('/<shortlink>')
def redirecting(shortlink):
    target = LinkData.query.filter_by(shorted_link=shortlink).first()
    if target:
        target.num_visits += 1
        db.session.commit()
        return redirect(f'{target.link}')


@app.route('/stats')
def stats():
    data = LinkData.query.all()
    return render_template('stats.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)
