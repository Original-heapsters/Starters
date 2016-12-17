from flask import Flask, redirect, url_for, render_template, request
from flask import flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from scripts import KeyLoader
from oauth import OAuthHelpers
from scripts import SentimentAnalysis
from scripts import ConceptExtractor
from scripts import dynamo
from havenondemand.hodclient import *
from havenondemand.hodresponseparser import *
from clarifai.rest import ClarifaiApp
import re, os, datetime, time


##################  Setup api keys  ##################
keys = KeyLoader.KeyLoader('keys.json')

fbID, fbSecret = keys.getCredentials('facebook')
hpeID, hpeSecret = keys.getCredentials('hpe_haven')
clarifID, clarifSecret = keys.getCredentials('clarifai')
awsID, aws_secret = keys.getCredentials('aws')
os.environ['AWS_APP_ID'] = awsID
os.environ['AWS_APP_SECRET'] = aws_secret
os.environ['CLARIFAI_APP_ID'] = clarifID
os.environ['CLARIFAI_APP_SECRET'] = clarifSecret
clarif = ClarifaiApp()


##################  Setup application & Oauth  ##################
app = Flask(__name__)
application = app
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

##################  Connect db with app  ##################
db = SQLAlchemy(app)
lm = LoginManager(app)
lm.login_view = 'index'

##################  Internal User Definition  ##################
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), nullable=False, unique=True)
    nickname = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=True)
    name = db.Column(db.String(64), nullable=True)
    role = db.Column(db.String(64), nullable=True)

##################  Load user  ##################
@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

##################  INDEX  ##################
@app.route('/')
def index():

    dyn = dynamo.dynamoOps()
    positivePosts = dyn.getPositivePosts()

    return render_template('index.html', positives=positivePosts)

##################  Journal  ##################
@app.route('/journal', methods=['GET', 'POST'])
def journal():

    #Received data
    if request.method == "POST":

        sentiments = None
        concepts = None
        hodClient = HODClient(hpeID)
        parser = HODResponseParser()

        sentiments = SentimentAnalysis.SentimentAnalysis(hodClient, parser,orig_text=request.form['journal_text'])
        concepts = ConceptExtractor.ConceptExtractor(hodClient, parser)

        text_to_analyze = request.form['journal_text']

        # split text by punctionation
        text = re.split('[?.,!]', text_to_analyze.lower())

        # No text was provided or only wrote <3 sentences
        # This encourages people to write more just to get more of that sweet sweet data
        if text_to_analyze == "" or len(text) < 4:
            return render_template('journal.html')

        # Send the hpe sentiment & concept request
        sentiments.doPost(text, 'eng')
        concepts.doPost(text_to_analyze)

        flag_for_review = True

        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y_%H-%M-%S')

        dyn = dynamo.dynamoOps()
        positivePosts = dyn.getPositivePosts()

        write_json(request.form['journal_text'], sentiments.d, concepts.results, sentiments.aggregate, timestamp, '1234','dev')
        return render_template('journal.html', sentiments=sentiments, concepts=concepts, flag_for_review=flag_for_review, positives=positivePosts)

    # No data received
    else:
        return render_template('index.html')

##################  FIND USER  ##################
@app.route('/findphrase', methods=['GET', 'POST'])
def findphrase():

    # Received a search phrase
    if request.method == 'POST':
        dyn = dynamo.dynamoOps()
        userdata = dyn.getUserByID(request.form['findphrase'])

        return render_template('findphrase.html', userdata=userdata)

    # No search received
    else:
        return render_template('findphrase.html')

##################  LOGOUT  ##################
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

################## OAUTH  ##################
@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthHelpers.get_provider(provider)
    return oauth.authorize()

##################  Callback from OAuth  ##################
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

##################  AUX  ##################
def write_json(text, sentiment, concepts, score, timestamp, id, role):
    user = {}
    user['Text'] = text.replace("\""," ").replace("{", " ").replace("}"," ")
    user['Sentiment'] = sentiment
    user['Score'] = score['score']
    user['ConceptsWords'] = ''.join(concepts.keys())
    user['ConceptsCounts'] = ''.join(str(concepts.values()))
    user['TimeStamp'] = timestamp
    user['User_ID'] = id
    user['Role'] = role

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True,host='0.0.0.0')