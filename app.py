from flask import Flask, render_template, request, url_for, flash, redirect
import string
import requests
import secrets
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
ENV = "dev"
URL = ""
# create db with name shortner_db and password postgres
if ENV == "dev":
    app.debug = True
    app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://postgres:postgres@localhost/shortner_db'
    URL = "http://127.0.0.1:5000/"
else:
    app.debug = False
    app.config["SQLALCHEMY_DATABASE_URI"] = ''
    URL = "https://short.nr/"

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Shorten(db.Model):
    __tablename__ = 'shortner_tb'

    id = db.Column(db.Integer(), primary_key=True)
    original_url = db.Column(db.String(), nullable=False)
    generated_url = db.Column(db.String(), unique=True, nullable=False)
    date_generated = db.Column(db.DateTime, default=datetime.utcnow())

    def __init__(self, original_url, generated_url):
        self.original_url = original_url
        self.generated_url = generated_url

    def __repr__(self):
        return f"<generated url {self.generated_url}>"

    def serialize(self):
        return {
            "OriginalUrl": self.original_url,
            "GeneratedUrl": self.generated_url
        }


LENGTH = 5

my_dict = {}


def generateUniqueId():
    uid = ''.join(secrets.choice(string.ascii_letters + string.digits)
                  for x in range(LENGTH))
    return uid


# def transformUrl(mainUrl):
#     generatedId = generateUniqueId()
#     my_dict[generatedId] = mainUrl
#     return my_dict[generatedId], generatedId


@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        mainUrl = str(request.form.get('mainUrl'))

        # check if entered url is a valid url
        # if requests.get(mainUrl).status_code != 200 or mainUrl == '':
        #     return render_template("index.html", message="Invalid URL")

        generatedId = generateUniqueId()

        data = Shorten(mainUrl, generatedId)
        db.session.add(data)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("index.html", message="Please Enter URL")


# get params for url and check from db to get the original url and redirect
@app.route('/<string:uniqueId>', methods=['GET', 'POST'])
def getOriginalUrl(uniqueId):
    if request.method == 'GET':
        data = Shorten.query.filter_by(generated_url=uniqueId).first()
        original_url = str(data.original_url) + "/"
        # TODO :make redirect work
        return requests.get(original_url)


if __name__ == '__main__':
    app.run()
