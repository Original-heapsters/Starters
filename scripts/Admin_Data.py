
class Admin_Data(object):

    def __init__(self, results={}):
        self.results = results

    def getAdminBreakdown(self, area_to_breakdown=None):
        self.results['errors'] = 'ADMIN ERRORS'

        empHealth = []

        empHealth.append('HEALTH SCORE1')
        empHealth.append('HEALTH SCORE2')
        empHealth.append('HEALTH SCORE3')
        empHealth.append('HEALTH SCORE4')

        empSentiment = []

        empSentiment.append('SENTIMENT SCORE1')
        empSentiment.append('SENTIMENT SCORE2')
        empSentiment.append('SENTIMENT SCORE3')
        empSentiment.append('SENTIMENT SCORE4')

        empOccurrences = []

        empOccurrences.append('OCCURRERENCE DATA1')
        empOccurrences.append('OCCURRERENCE DATA2')
        empOccurrences.append('OCCURRERENCE DATA3')
        empOccurrences.append('OCCURRERENCE DATA4')


        self.results['cumulEmpHealth'] = empHealth
        self.results['cumulSentiment'] = empSentiment
        self.results['cumulOccurances'] = empOccurrences

        for item in self.results:
            print('column ' + item)
            for d in self.results[item]:
                print('row ' + d)




        return self.results

if __name__ == '__main__':
    admin = Admin_Data()
    admin.getAdminBreakdown()