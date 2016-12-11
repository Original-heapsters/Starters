import boto
from boto.s3.key import Key
from flask import Flask, redirect, url_for, render_template, request
from flask import flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user,\
    current_user
from scripts import KeyLoader
from scripts import Admin_Data
from scripts import userIds
from oauth import OAuthHelpers
from scripts import SentimentAnalysis
from scripts import ConceptExtractor
from scripts import dynamo
from havenondemand.hodclient import *
from havenondemand.hodresponseparser import *
from clarifai.rest import ClarifaiApp
from pprint import pprint
import re, os, json, datetime, time, csv

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

#
# @app.route('/search', methods=['GET', 'POST'])
# def search():
#     if request.method == "POST":
#         hodClient = HODClient(hpeID)
#         parser = HODResponseParser()
#         user_ids = request.form['journal_text']
#
#         return render_template('search.html', user_ids)



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/journal', methods=['GET', 'POST'])
def journal():
    if request.method == "POST":
        print('posting')
        sentiments = None
        concepts = None
        hodClient = HODClient(hpeID)
        parser = HODResponseParser()
        sentiments = SentimentAnalysis.SentimentAnalysis(hodClient, parser)
        concepts = ConceptExtractor.ConceptExtractor(hodClient, parser)
        text_to_analyze = request.form['journal_text']
        if text_to_analyze == "" or len(re.split('[?.,!]', text_to_analyze)) < 4:
            return render_template('journal.html')
        # split text by punctionation
        text = re.split('[?.,!]', text_to_analyze.lower())
        sentiments.doPost(text, 'eng')
        concepts.doPost(text_to_analyze)
        #return render_template('thankyou.html')
        flag_for_review = None
        if 'neutral' in sentiments.results['overall']:
            pos = calc_avg(sentiments.d, "positives")
            neg = calc_avg(sentiments.d, "negatives")
            print(pos, neg)
            if pos > .70 and neg > .70:
                # pass crazy_person = true
                # crazyperson.jpg
                flag_for_review = True
                print('Watch out for this man')

        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d_%H%M%S')

        write_json(request.form['journal_text'], sentiments.d, concepts.results, sentiments.aggregate, timestamp, '1234','dev')
        return render_template('journal.html', sentiments=sentiments, concepts=concepts, flag_for_review=flag_for_review)
    else:
        return render_template('index.html')

def write_sentiments(sent, agg, ts):
    pos_filename = 'possentiments' + ts + '.csv'
    with open(pos_filename, 'w', newline="") as out_file:
        csv_w = csv.writer(out_file)
        csv_w.writerow(
            ["documentIndex", "normalized_length", "normalized_text", "original_length", "original_text", "score",
             "sentiment", "topic"])
        for x in sent['positives']:
            csv_w.writerow([x['documentIndex'],
                            x['normalized_length'],
                            x['normalized_text'],
                            x['original_length'],
                            x['original_text'],
                            x['score'],
                            x['sentiment'],
                            x['topic']])

    neg_filename = 'negsentiments' + ts + '.csv'
    with open(neg_filename, 'w', newline="") as out_file:
        csv_w = csv.writer(out_file)
        csv_w.writerow(
            ["documentIndex", "normalized_length", "normalized_text", "original_length", "original_text", "score",
             "sentiment", "topic"])
        for x in sent['negatives']:
            csv_w.writerow([x['documentIndex'],
                            x['normalized_length'],
                            x['normalized_text'],
                            x['original_length'],
                            x['original_text'],
                            x['score'],
                            x['sentiment'],
                            x['topic']])

    agg_filename = 'aggsentiments' + ts + '.csv'
    with open(agg_filename, 'w', newline="") as out_file:
        csv_w = csv.writer(out_file)
        csv_w.writerow(["sentiment", "score"])
        csv_w.writerow([agg['sentiment'],
                        agg['score']])


    # csv_to_dict(filename)
    send_to_s3(pos_filename)
    send_to_s3(neg_filename)
    send_to_s3(agg_filename)

def write_concepts(conc,ts):
    filename = 'concepts' + ts + '.csv'
    with open(filename, 'w', newline="") as out_file:
        csv_w = csv.writer(out_file)
        csv_w.writerow(["concept", "occurrence"])
        for x,y in conc.items():
            csv_w.writerow([x, y])

    # csv_to_dict(filename)
    send_to_s3(filename)

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
    pprint(user)


    write_sentiments(sentiment, score, user['TimeStamp'])


    #filename = 'sentiments' + user['TimeStamp'] + '.csv'
    #with open(filename, 'w', newline="") as out_file:
    #    csv_w = csv.writer(out_file)
    #    csv_w.writerow(
    #        ["text","positives", "negatives", "aggregate", "User_ID"])
    #    csv_w.writerow([text,
    #                    sentiment['positives'],
    #                    sentiment['negatives'],
    ##                    score,
    #                   id])

    # csv_to_dict(filename)
    #send_to_s3(filename)
    write_concepts(concepts, user['TimeStamp'])
    # filename = 'concepts' + user['TimeStamp'] + '.csv'
    # with open(filename, 'w', newline="") as out_file:
    #     csv_w = csv.writer(out_file)
    #     csv_w.writerow(["text", "concept", "count", "User_ID"])
    #     for entry in concepts:
    #         csv_w.writerow([text,
    #                         entry,
    #                         concepts[entry],
    #                         id])

    # csv_to_dict(filename)
    # send_to_s3(filename)

    filename = user['TimeStamp'] + '.csv'
    with open(filename, 'w', newline="") as out_file:
        csv_w = csv.writer(out_file)
        csv_w.writerow(["Text", "Sentiment", "Score", "ConceptsWords", "ConceptsCounts","TimeStamp", "User_ID", "Role"])
        csv_w.writerow([user['Text'],
                        user['Sentiment'],
                        user['Score'],
                        user['ConceptsWords'],
                        user['ConceptsCounts'],
                        user['TimeStamp'],
                        user['User_ID'],
                        user['Role']])

    #csv_to_dict(filename)
    send_to_s3(filename)


def csv_to_dict(input_file):
    user = {}
    user['Text'] = None
    user['Sentiment'] = None
    user['Score'] = None
    user['Concepts'] = None
    user['TimeStamp'] = None
    user['User_ID'] = None
    user['Role'] = None

    rows = csv.DictReader(open(input_file))

    for row in rows:
        user['Text'] = row['Text']
        user['Sentiment'] = row['Sentiment']
        user['Score'] = row['Score']
        user['Concepts'] = row['Concepts']
        user['TimeStamp'] = row['TimeStamp']
        user['User_ID'] = row['User_ID']
        user['Role'] = row['Role']
    pprint(user)
    entry = {
    'TimeStamp': user['TimeStamp'],
    'Concept': user['Concepts'],
    'Role': user['Role'],
    'Score': user['Score'],
    'Sentiment': user['Sentiment'],
    'Text': user['Text'],
    'User_ID': '1234'
    }

    dym = dynamo.dynamoOps()

    dym.addEntry(entry)

    send_to_s3(input_file)

def send_to_s3(input_file):
    conn = boto.connect_s3(
        aws_access_key_id=awsID,
        aws_secret_access_key=aws_secret,
    )
    testfile = input_file

    bucket1 = conn.get_bucket("elasticbeanstalk-us-east-1-081891355789")

    k = Key(bucket1)
    k.key = 'PlezaDump/'+ input_file + '.csv'

    k.set_contents_from_filename(testfile, policy='public-read')


def calc_avg(dict, type):
    print(dict)
    avg = 0
    for score in dict[type]:
        avg += score['score']
    avg = avg / len(dict[type])
    return abs(avg)

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

@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')

@app.route('/feedback')
def feedback():
    return render_template('feedback.html')

@app.route('/breakdown')
def breakdown():

    admin = Admin_Data.Admin_Data()

    admin_data = admin.getAdminBreakdown()
    # Get dynamo info
    return render_template('breakdown.html', admin_data=admin, area='JANITORIAL')

@app.route('/search/')
def search():
    ids = userIds.userIds()
    user_ids= ids.getuserIds()
    return render_template('search.html', user_ids=ids)

@app.route("/search/<useridstr>/")
def userpage(useridstr):
    # show the user profile for that user
    return render_template('index.html')

@app.route('/finduser', methods=['GET','POST'])
def finduser():
    dyn = dynamo.dynamoOps()

    if request.method == 'POST':
        userdata = dyn.getUserByID(request.form['finduserid'])
    else:
        userdata = None

    return render_template('finduser.html', userdata=userdata)


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