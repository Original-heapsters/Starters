from flask import Flask, redirect, url_for, render_template, request
from flask import flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user,\
    current_user
from Scripts import KeyLoader
from oauth import OAuthHelpers
from Scripts import SentimentAnalysis
from Scripts import ConceptExtractor
from havenondemand.hodclient import *
from havenondemand.hodresponseparser import *
from clarifai.rest import ClarifaiApp
from pprint import pprint
import re, os

keys = KeyLoader.KeyLoader('keys.json')

fbID, fbSecret = keys.getCredentials('facebook')
hpeID, hpeSecret = keys.getCredentials('hpe_haven')
clarifID, clarifSecret = keys.getCredentials('clarifai')
os.environ['CLARIFAI_APP_ID'] = clarifID
os.environ['CLARIFAI_APP_SECRET'] = clarifSecret
clarif = ClarifaiApp()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['OAUTH_CREDENTIALS'] = {
    'facebook': {
        'id': fbID,
        'secret': fbSecret
    },
    'twitter': {
        'id': '3RzWQclolxWZIMq5LJqzRZPTl',
        'secret': 'm9TEd58DSEtRrZHpz2EjrV9AhsBRxKMo8m3kuIZj3zLwzwIimt'
    }
}

db = SQLAlchemy(app)
lm = LoginManager(app)

lm.login_view = 'index'


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), nullable=False, unique=True)
    nickname = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=True)
    name = db.Column(db.String(64), nullable=True)
    role = db.Column(db.String(64), nullable=True)

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/journal', methods=['GET', 'POST'])
def journal():
    if request.method == "POST":
        print('posting')
        journal = None
        hodClient = HODClient(hpeID)
        parser = HODResponseParser()
        journal = SentimentAnalysis.SentimentAnalysis(hodClient, parser)
        text_to_analyze = request.form['journal_text']
        # split text by punctionation
        text = re.split('[?.,!]', text_to_analyze.lower())
        journal.doPost(text, 'eng')

        return render_template('journal.html', journal=journal)
    else:
        return render_template('journal.html')

@app.route('/sentimental', methods=['GET', 'POST'])
def sentimental():
    if request.method == "POST":
        print('posting')
        sentiments = None
        hodClient = HODClient(hpeID)
        parser = HODResponseParser()
        sentiments = SentimentAnalysis.SentimentAnalysis(hodClient, parser)
        text_to_analyze = request.form['sentiment_text']
        # split text by punctionation
        text = re.split('[?.,!]', text_to_analyze)
        sentiments.doPost(text, 'eng')

        return render_template('sentimental.html', sentiments=sentiments)
    else:
        return render_template('sentimental.html')

@app.route('/conceptual', methods=['GET', 'POST'])
def conceptual():
    if request.method == "POST":
        print('posting')
        concepts = None
        hodClient = HODClient(hpeID)
        parser = HODResponseParser()
        concepts = ConceptExtractor.ConceptExtractor(hodClient, parser)
        text_to_analyze = request.form['concept_text']
        # split text by punctionation
        concepts.doPost(text_to_analyze)


        return render_template('conceptual.html', concepts=concepts)
    else:
        return render_template('conceptual.html')

@app.route('/clarifai', methods=['GET','POST'])
def clarifai():
    if request.method == "POST":
        tags = ''
        link_to_tag = request.form['image_url']
        tags = clarif.tag_urls([link_to_tag])
        pprint(tags)
        output = tags['outputs']

        data = output[0]['data']
        print (data)
        concepts = data['concepts']

        tag_list = ''
        for tag in concepts:
            tag_list += tag['name'] + ', '

        return render_template('clarifai.html', original_image=request.form['image_url'],tags=tag_list)
    else:

        return render_template('clarifai.html')

@app.route('/feedback')
def feedback():
    return render_template('feedback.html')

@app.route('/breakdown')
def breakdown():
    return render_template('feedback.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthHelpers.get_provider(provider)
    return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthHelpers.get_provider(provider)
    social_id, username, email, name, role = None, None, None, None, None
    social_id, username, email, name, role = oauth.callback()

    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, nickname=username, email=email, name=name, role=role)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('index'))





if __name__ == '__main__':
    db.create_all()
    app.run(debug=True,host='0.0.0.0')