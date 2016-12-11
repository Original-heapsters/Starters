
class Admin_Data(object):

    def __init__(self, results={}):
        self.results = results

    def getAdminBreakdown(self, area_to_breakdown=None):
        self.results['errors'] = 'ADMIN ERRORS'
        self.results['cumulative_totals'] = {}

        empHealth = []

        empHealth.append('HEALTH SCORE')

        empSentiment = []

        empSentiment.append('SENTIMENT SCORE')

        empOccurrences = []

        empOccurrences.append('OCCURRERENCE DATA')


        self.results['cumulative_totals']['cumulEmpHealth'] = empHealth
        self.results['cumulative_totals']['cumulSentiment'] = empSentiment
        self.results['cumulative_totals']['cumulOccurances'] = empOccurrences




        return self.results

if __name__ == '__main__':
    admin = Admin_Data()
    admin.getAdminBreakdown()