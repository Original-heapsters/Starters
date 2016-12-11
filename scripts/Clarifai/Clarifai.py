import os
from scripts import KeyLoader
from clarifai.rest import ClarifaiApp
from pprint import pprint

keys = KeyLoader.KeyLoader('../../keys.json')
clarifID, clarifSecret = keys.getCredentials('clarifai')


os.environ['CLARIFAI_APP_ID'] = clarifID
os.environ['CLARIFAI_APP_SECRET'] = clarifSecret

app = ClarifaiApp()

pprint(app.tag_urls(['https://samples.clarifai.com/metro-north.jpg']))