import pandas as pd


class Modtools:
    def __init__(self, location):
        try:
            loaded = pd.read_csv(str(location), sep='\t')
        except:  # whatever doesn't work it's bad for this
            loaded = None
        self._cols = ['usercode', 'date when happened', 'channel where called',
                      'reason for calling', 'status of this', 'assigned to', 'report-id']
        tempframe = pd.DataFrame(columns=self._cols)
        if loaded is not None:
            self._data = loaded
        else:
            self._data = tempframe
        self._location = location

    def addentry(self, user, date, channel, reason, status):
        assigned = 'no assignee'
        reportcode = max(self._data['report-id'].to_list())+1
        newrow = pd.DataFrame([[user, date, channel, reason, status, assigned, reportcode]],
                              columns=self._cols)
        self._data = pd.concat([self._data, newrow], ignore_index=True, sort=False)
        self.savereportsusual()

    def savereportsusual(self):
        self._data.to_csv(self._location, index=False, sep='\t')

    def getunsolved(self):
        elaborateframe = self._data.loc[self._data['status of this']=='unsolved']
        return elaborateframe.values.tolist()

    def setsolvedbyindex(self, indexloc):
        self._data.at[indexloc, 'status of this'] = 'solved'
        self.savereportsusual()
        return

    def setassigned(self, indexloc, who):
        self._data.at[indexloc, 'assigned to'] = who
        self.savereportsusual()
        return

    def getassigned(self, assignee):
        return self._data.loc[self._data['assigned to'] == assignee].values.tolist()
