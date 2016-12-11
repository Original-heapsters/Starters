
class userIds(object):
    def __init__(self, results={}):
        self.results = results

    def getuserIds(self):
        self.results['errors'] = 'ADMIN ERRORS'

        uID = []

        uID.append('1234')
        uID.append('1235')
        uID.append('1236')
        uID.append('1237')

        uNAME = []

        uNAME.append('Henry')
        uNAME.append('Sam')
        uNAME.append('Bill Jones')
        uNAME.append('Red Bull')

        uSCORE = []

        uSCORE.append('40')
        uSCORE.append('50')
        uSCORE.append('60')
        uSCORE.append('70')

        self.results['ID'] = uID
        self.results['NAME'] = uNAME
        self.results['SCORE'] = uSCORE

        # for item in self.results:
        #     print('column ' + item)
        #     for d in self.results[item]:
        #         print('row ' + d)
        #
        return self.results

if __name__ == '__main__':
    ids = userIds()
    ids.getuserIds()