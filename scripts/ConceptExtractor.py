from Scripts import KeyLoader
from havenondemand.hodclient import *
from havenondemand.hodresponseparser import *

class ConceptExtractor(object):

    def __init__(self, hodClient=None, parser=None, results={}):
        self.hodClient = hodClient
        self.parser = parser
        self.results = results

    def conceptRequestCompleted(self, response, **context):
        concept_dict = {}
        resp = "<br>"
        payloadObj = self.parser.parse_payload(response)
        print('Parseing')
        if payloadObj is None:
            errorObj = self.parser.get_last_error()
            for err in errorObj.errors:
                resp += "Error code: %d Reason: %s Details: %s" % (err.error, err.reason, err.detail)
                print(resp)
        else:
            app = context["hodapp"]
            if app == HODApps.EXTRACT_CONCEPTS:
                print("In apppppp")
                concepts = payloadObj["concepts"]

                for concept in concepts:
                    print(concept)
                    concept_dict[concept['concept']] = concept['occurrences']
        self.results = concept_dict

    def doPost(self, textToAnalyze):
        hodApp = HODApps.EXTRACT_CONCEPTS
        paramArr = {}
        #List of sentences
        paramArr["text"] = textToAnalyze

        context = {}
        context["hodapp"] = hodApp

        self.hodClient.post_request(paramArr, hodApp, async=False, callback=self.conceptRequestCompleted, **context)

if __name__ == '__main__':
    keys = KeyLoader.KeyLoader('../keys.json')

    hpeID, hpeSecret = keys.getCredentials('hpe_haven')

    hodClient = HODClient(hpeID)
    parser = HODResponseParser()
    concept = ConceptExtractor(hodClient=hodClient, parser=parser)
    concept.doPost('My feet really hurt. This ice cream is freaking amazeballz! Whats the purpose for life really?')
    diction = concept.results

    for k,v in diction.items():
        print(k)
        print(v)