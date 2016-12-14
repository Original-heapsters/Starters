import csv,datetime, time, os
from boto.s3.key import Key
import boto

class Sentiment(object):

    def __init__(self, positive=[], negative=[], aggregate={}):
        self.positive = positive
        self.negative = negative
        self.aggregate = aggregate

    def understandSentiment(self, jsonResp):
        positiveList = []
        for item in jsonResp['positive']:
            positiveList.append(item)

        self.positive = positiveList

        negativeList = []
        for item in jsonResp['negative']:
            negativeList.append(item)
        self.negative = negativeList

        self.aggregate['sentiment'] = jsonResp['aggregate']['sentiment']
        self.aggregate['score'] = jsonResp['aggregate']['score']

    def pullSentiments(self, type, jsonIn):
        if type.lower() == 'positive':
            pass

        else:
            pass

    def getAggData(self, jsonIn):
        pass

    def writeToCSV(self):
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d_%H%M%S')
        sentiments_filename = 'Sentiments_' + timestamp + '_.csv'
        with open(sentiments_filename, 'w', newline="") as out_file:
            csv_w = csv.writer(out_file)
            csv_w.writerow(
                ["Sentiment", "Topic", "Score", "Original_Text", "Original_Length", "Normalized_Text","Normalized_Length", "Date"])
            for pos in self.positive:
                csv_w.writerow([pos['sentiment'],
                                pos['topic'],
                                str(pos['score']),
                                pos['original_text'],
                                str(pos['original_length']),
                                pos['normalized_text'],
                                str(pos['normalized_length']),
                                timestamp])

            for neg in self.negative:
                csv_w.writerow([neg['sentiment'],
                                neg['topic'],
                                str(neg['score']),
                                neg['original_text'],
                                str(neg['original_length']),
                                neg['normalized_text'],
                                str(neg['normalized_length']),
                                timestamp])

        self.send_to_s3(sentiments_filename,'Pleza_Sentiments')

        agg_filename = 'aggSentiments_' + timestamp + '_.csv'
        with open(agg_filename, 'w', newline="") as out_file:
            csv_w = csv.writer(out_file)
            csv_w.writerow(
                ["Overall_Sentiment", "Overall_Score", "Date"])
            csv_w.writerow(
                [self.aggregate['sentiment'], self.aggregate['score'], timestamp])

        self.send_to_s3(agg_filename, 'Pleza_Aggregate')



    def printObj(self):
        print("Positives__________________________")
        if self.positive:
            for pos in self.positive:
                print("Sentiment: " + pos['sentiment'])
                print("Topic: " + str(pos['topic']))
                print("Score: " + str(pos['score']))
                print("Original Text: " + pos['original_text'])
                print("Original Length: " + str(pos['original_length']))
                print("Normalized Text: " + pos['normalized_text'])
                print("Normalized Length: " + str(pos['normalized_length']))
                #print("Offset: " + str(pos['offset']))

        print("Negatives__________________________")
        if self.negative:
            for neg in self.negative:
                print("Sentiment: " + neg['sentiment'])
                print("Topic: " + str(neg['topic']))
                print("Score: " + str(neg['score']))
                print("Original Text: " + neg['original_text'])
                print("Original Length: " + str(neg['original_length']))
                print("Normalized Text: " + neg['normalized_text'])
                print("Normalized Length: " + str(neg['normalized_length']))
                #print("Offset: " + str(neg['offset']))

        print("Aggegrates__________________________")
        print("Overall Sentiment: " + self.aggregate['sentiment'])
        print("Overall Score: " + str(self.aggregate['score']))

        self.writeToCSV()


    def send_to_s3(self, input_file, location):
        awsID = os.environ['AWS_APP_ID']
        aws_secret = os.environ['AWS_APP_SECRET']
        conn = boto.connect_s3(
            aws_access_key_id=awsID,
            aws_secret_access_key=aws_secret,
        )
        testfile = input_file

        bucket1 = conn.get_bucket("elasticbeanstalk-us-east-1-081891355789")

        k = Key(bucket1)
        k.key = location + '/'+ input_file
        k.set_contents_from_filename(testfile, policy='public-read')

if __name__ == '__main__':
    item = None
    print(item)
    sent = Sentiment()

    sent.understandSentiment('s')

    for pos in sent.positive:
        print(pos['sentiment'])
        print(pos['topic'])
        print(pos['score'])
        print(pos['original_text'])
        print(pos['original_length'])
        print(pos['normalized_text'])
        print(pos['normalized_length'])
        print(pos['offset'])

    for neg in sent.negative:
        print(neg['sentiment'])
        print(neg['topic'])
        print(neg['score'])
        print(neg['original_text'])
        print(neg['original_length'])
        print(neg['normalized_text'])
        print(neg['normalized_length'])
        print(neg['offset'])

    print(sent.aggregate['sentiment'])
    print(sent.aggregate['score'])




