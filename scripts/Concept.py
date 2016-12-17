import csv,datetime, time, os
from boto.s3.key import Key
import boto


class Concept(object):

    def __init__(self, concept=[]):
        self.concept = concept

    def understandConcept(self, jsonResp):
        conceptList = []
        for item in jsonResp['concepts']:
            conceptList.append(item)

        self.concept = conceptList

    def writeToCSV(self):
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d_%H%M%S')
        concepts_filename = 'Concepts_' + timestamp + '_.csv'
        with open(concepts_filename, 'w', newline="") as out_file:
            csv_w = csv.writer(out_file)
            csv_w.writerow(
                ["Concept", "Occurrence", "Date"])
            for con in self.concept:
                csv_w.writerow([con['concept'],
                                str(con['occurrences']),
                                timestamp])
        self.send_to_s3(concepts_filename,'Pleza_Concepts')
        os.remove(concepts_filename)

    def printObj(self):
        print("Concepts__________________________")
        if self.concept:
            for con in self.concept:
                print("Concept: " + con['concept'])
                print("Occurrence: " + str(con['occurrences']))

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
    con = Concept()

    con.understandConcept('s')





