from AuxClasses import KeyLoader
from AuxClasses import SentimentAnalysis
from havenondemand.hodclient import *
from havenondemand.hodresponseparser import *


keys = KeyLoader.KeyLoader('../../keys.json')

app_id, app_secret = keys.getCredentials('hpe_haven')

print(app_id)
print(app_secret)

hodClient = HODClient(app_id)
parser = HODResponseParser()

sentiments = SentimentAnalysis.SentimentAnalysis(hodClient,parser)
listOfSentences = ["My feet really hurt", "This ice cream is amazing", "I feel really fat today"] # ["I like tropical fruits","Public parking service in Palo Alto is really awesome","A mountain lion was killed by a local resident in Los Gatos"]
sentiments.doPost(listOfSentences,'eng')