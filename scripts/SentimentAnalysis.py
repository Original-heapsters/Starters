from scripts import Sentiment
from scripts import KeyLoader
from pprint import pprint
from havenondemand.hodclient import *
from havenondemand.hodresponseparser import *

class SentimentAnalysis(object):

    def __init__(self, hodClient=None, parser=None, results={}, orig_text='Text'):
        self.hodClient = hodClient
        self.parser = parser
        self.results = results
        self.d = {}
        self.aggregate = {}
        self.orig_text = orig_text

    def sentimentRequestCompleted(self, response, **context):
        sentiment_dict = {}
        sentiment_result = {}
        resp = "<br>"
        payloadObj = self.parser.parse_payload(response)

        pprint(payloadObj)

        if payloadObj is None:
            errorObj = self.parser.get_last_error()
            sentiment_dict['errors'] = ''
            for err in errorObj.errors:
                sentiment_dict['errors'] += "Error code: %d Reason: %s Details: %s" % (err.error, err.reason, err.detail)
                resp += "Error code: %d Reason: %s Details: %s" % (err.error, err.reason, err.detail)
        else:

            sentObj = Sentiment.Sentiment(orig_text=self.orig_text)

            sentObj.understandSentiment(payloadObj)
            sentObj.printObj()



            app = context["hodapp"]
            if app == HODApps.ANALYZE_SENTIMENT:
                positives = payloadObj["positive"]
                resp += "Positive:<br>"
                sentiment_dict['positives'] = ''
                sentiment_result['positives'] = []
                for pos in positives:
                    pos['score'] = round(pos['score'], 3)
                    sentiment_result['positives'].append(pos)
                    pos_text = ''
                    pos_text += "Sentiment: " + pos["sentiment"] + "<br>"
                    resp += "Sentiment: " + pos["sentiment"] + "<br>"
                    if pos.get('topic'):
                        pos_text += "Topic: " + pos["topic"] + "<br>"
                        resp += "Topic: " + pos["topic"] + "<br>"
                    pos_text += "Score: " + "%f " % (pos["score"]) + "<br>"
                    resp += "Score: " + "%f " % (pos["score"]) + "<br>"
                    if 'documentIndex' in pos:
                        pos_text += "Doc: " + str(pos["documentIndex"]) + "<br>"
                        resp += "Doc: " + str(pos["documentIndex"]) + "<br>"
                    sentiment_dict['positives'] += pos_text
                negatives = payloadObj["negative"]
                resp += "Negative:<br>"
                sentiment_dict['negatives'] = ''
                sentiment_result['negatives'] = []
                for neg in negatives:
                    neg['score'] = round(neg['score'], 3)
                    sentiment_result['negatives'].append(neg)
                    neg_text = ''
                    neg_text += "Sentiment: " + neg["sentiment"] + "<br>"
                    resp += "Sentiment: " + neg["sentiment"] + "<br>"
                    if neg.get('topic'):
                        neg_text += "Topic: " + neg["topic"] + "<br>"
                        resp += "Topic: " + neg["topic"] + "<br>"
                    neg_text += "Score: " + "%f " % (neg["score"]) + "<br>"
                    resp += "Score: " + "%f " % (neg["score"]) + "<br>"
                    if 'documentIndex' in neg:
                        neg_text += "Doc: " + str(neg["documentIndex"]) + "<br>"
                        resp += "Doc: " + str(neg["documentIndex"]) + "<br>"
                    sentiment_dict['negatives'] += neg_text
                aggregate = payloadObj["aggregate"]
                sentiment_dict['overall'] = "Aggregate:<br>"
                resp += "Aggregate:<br>"
                sentiment_dict['overall'] += "Score: " + "%f " % (aggregate["score"]) + "<br>"
                resp += "Score: " + "%f " % (aggregate["score"]) + "<br>"
                sentiment_dict['overall'] += aggregate["sentiment"] + "<br>"
                if aggregate["sentiment"] == 'neutral':
                    sentiment_dict['overall'] += ':|'
                elif aggregate["sentiment"] == 'positive':
                        sentiment_dict['overall'] += ':)'
                elif aggregate["sentiment"] == 'negative':
                    sentiment_dict['overall'] += '>:('
                self.aggregate = {'score': round(aggregate["score"],3), 'sentiment': aggregate["sentiment"]}
                resp += aggregate["sentiment"]
        self.results = sentiment_dict
        self.d = sentiment_result
        print(resp)

    def doPost(self, textToAnalyze, language):
        hodApp = HODApps.ANALYZE_SENTIMENT
        paramArr = {}
        #List of sentences
        paramArr["text"] = textToAnalyze
        #self.orig_text = textToAnalyze
        # ex. 'eng'
        paramArr["lang"] = language

        context = {}
        context["hodapp"] = hodApp

        self.hodClient.post_request(paramArr, hodApp, async=False, callback=self.sentimentRequestCompleted, **context)

if __name__ == '__main__':
    keys = KeyLoader.KeyLoader('../keys.json')

    fbID, fbSecret = keys.getCredentials('facebook')
    hpeID, hpeSecret = keys.getCredentials('hpe_haven')

    hodClient = HODClient(hpeID)
    parser = HODResponseParser()
    Sent = SentimentAnalysis(hodClient,parser)
    Sent.doPost(['My feet really hurt.', 'This ice cream is amazing!', 'Whats the purpose for life really?', 'I am unhappy with my job.'],'eng')