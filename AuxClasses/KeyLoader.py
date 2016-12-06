import json
from pprint import pprint

class KeyLoader(object):

    def __init__(self, filepath=''):
        self.filepath = filepath

    def readKeys(self):
        with open(self.filepath) as data_file:
            data = json.load(data_file)
        return data

    def viewKeyFile(self):
        contents = self.readKeys()

        pprint(contents)

    def getCredentials(self, appIndex):
        keys = self.readKeys()

        if type(appIndex) is not int:
            for app in keys['Apps']['app']:
                if app['name'].lower() == appIndex:
                    keyObj = app
        else:
            keyObj = keys['Apps']['app'][appIndex]

        keyID = keyObj['app_id']
        keySecret = keyObj['app_secret']

        return keyID, keySecret

if __name__ == '__main__':
    keys = KeyLoader('../keys.json')
    keys.viewKeyFile()

    desiredKey = 'facebook'
    id,secret = keys.getCredentials(desiredKey)

    print(desiredKey + ' id = ' + id)
    print(desiredKey + ' secret = ' + secret)