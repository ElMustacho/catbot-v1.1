import pandas as pd


class Modtools:
    def __init__(self, location, storelocation):
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

        try:
            loaded = pd.read_csv(str(storelocation), sep='\t')
        except:  # whatever doesn't work it's bad for this
            loaded = None
        tempframe = pd.DataFrame(columns=self._cols)
        if loaded is not None:
            self._storedata = loaded
        else:
            self._storedata = tempframe

        self._storelocation = storelocation
        self._location = location

    def addentry(self, user, date, channel, reason, status):
        assigned = 'no assignee'
        try:
            reportcode = max(self._data['report-id'].to_list())+1
        except ValueError:
            reportcode = 1
        newrow = pd.DataFrame([[user, date, channel, reason, status, assigned, reportcode]],
                              columns=self._cols)
        self._data = pd.concat([self._data, newrow], ignore_index=True, sort=False)
        self.savereportsusual()
        return reportcode

    def savereportsusual(self):
        self._data.to_csv(self._location, index=False, sep='\t')

    def getunsolved(self):
        elaborateframe = self._data.loc[self._data['status of this'] == 'unsolved']
        return elaborateframe.values.tolist()

    def setsolvedbyindex(self, indexloc):
        looking = self._data['report-id'].to_list()
        if indexloc in looking:
            self._data.loc[self._data['report-id'] == indexloc, 'status of this'] = 'solved'
            self.savereportsusual()
            return True
        else:
            return False


    def setassigned(self, indexloc, who):
        self._data.at[indexloc, 'assigned to'] = who
        self._data.at[indexloc, 'status of this'] = 'assigned'
        self.savereportsusual()
        return

    def getassigned(self, assignee):
        return self._data.loc[self._data['assigned to'] == assignee].values.tolist()

    def deletereportbyid(self, value):
        tostore = self._data.loc[self._data['report-id'] == value]
        self._data = self._data[self._data['report-id'] != value]
        self.savereportsusual()
        self.storereport(tostore)
        return tostore.values.tolist()[0]

    def storereport(self, report):
        self._storedata = pd.concat([self._storedata, report], ignore_index=True, sort=False)
        self._storedata.to_csv(self._storelocation, index=False, sep='\t')
        return None