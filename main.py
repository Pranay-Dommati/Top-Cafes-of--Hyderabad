from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from flask_bootstrap import Bootstrap5
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('secret_key')
Bootstrap5(app)
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('database_uri')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Cafe(db.Model):
    __tablename__ = 'cafes'
    cafe_name = db.Column(db.String(100), primary_key=True)
    cafe_location = db.Column(db.String(250), nullable=False)
    google_map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f'<Cafe {self.cafe_name}>'


@app.route('/')
def index():
    cafes = Cafe.query.distinct().all()
    return render_template('index.html', cafes=cafes)


if __name__ == '__main__':
    app.run(debug=True)

