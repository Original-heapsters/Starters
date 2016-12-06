from havenondemand.hodclient import *
from havenondemand.hodresponseparser import *

class SentimentAnalysis(object):

    def __init__(self, hodClient=None, parser=None):
        self.hodClient = hodClient
        self.parser = parser

    def sentimentRequestCompleted(self, response, **context):
        resp = ""
        payloadObj = self.parser.parse_payload(response)
        if payloadObj is None:
            errorObj = self.parser.get_last_error()
            for err in errorObj.errors:
                resp += "Error code: %d \nReason: %s \nDetails: %s\n" % (err.error, err.reason, err.detail)
        else:
            app = context["hodapp"]
            if app == HODApps.ANALYZE_SENTIMENT:
                positives = payloadObj["positive"]
                resp += "Positive:\n"
                for pos in positives:
                    resp += "Sentiment: " + pos["sentiment"] + "\n"
                    if pos.get('topic'):
                        resp += "Topic: " + pos["topic"] + "\n"
                    resp += "Score: " + "%f " % (pos["score"]) + "\n"
                    if 'documentIndex' in pos:
                        resp += "Doc: " + str(pos["documentIndex"]) + "\n"
                negatives = payloadObj["negative"]
                resp += "Negative:\n"
                for neg in negatives:
                    resp += "Sentiment: " + neg["sentiment"] + "\n"
                    if neg.get('topic'):
                        resp += "Topic: " + neg["topic"] + "\n"
                    resp += "Score: " + "%f " % (neg["score"]) + "\n"
                    if 'documentIndex' in neg:
                        resp += "Doc: " + str(neg["documentIndex"]) + "\n"
                aggregate = payloadObj["aggregate"]
                resp += "Aggregate:\n"
                resp += "Score: " + "%f " % (aggregate["score"]) + "\n"
                resp += aggregate["sentiment"]
        print(resp)


    def doPost(self, textToAnalyze, language):
        hodApp = HODApps.ANALYZE_SENTIMENT
        paramArr = {}
        #List of sentences
        paramArr["text"] = textToAnalyze
        # ex. 'eng'
        paramArr["lang"] = language

        context = {}
        context["hodapp"] = hodApp

        self.hodClient.post_request(paramArr, hodApp, async=False, callback=self.sentimentRequestCompleted, **context)

if __name__ == '__main__':
    Sent = SentimentAnalysis()
    Sent.doPost(['My feet really hurt.', 'This ice cream is freaking amazeballz!', 'Whats the purpose for life really?'],'eng')