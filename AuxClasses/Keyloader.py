import json
from pprint import pprint

def readKeys():
    with open('../keys.json') as data_file:
        data = json.load(data_file)
    return data

def viewKeyFile():
    contents = readKeys()

    pprint(contents)

def getCredentials(appIndex):
    keys = readKeys()

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
    viewKeyFile()

    desiredKey = 'facebook'
    id,secret = getCredentials(desiredKey)

    print(desiredKey + ' id = ' + id)
    print(desiredKey + ' secret = ' + secret)