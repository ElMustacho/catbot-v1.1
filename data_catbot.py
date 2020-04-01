from datetime import datetime, timedelta
import json

class Data_catbot:
    def __init__(self, timelastmessage, requireddata):
        self._timelastmessage = timelastmessage
        self._requireddata = requireddata
        self._timerlowtier = 0


    @classmethod
    def defFromFile(cls):
        with open('config.json') as json_file:
            cls.requireddata = json.load(json_file)
        cls.timelastmessage = datetime.now()
        cls.timerlowtier = datetime.now() - timedelta(seconds=60)
        return cls

    @property
    def timelastmessage(self):
        return self._timelastmessage

    @timelastmessage.setter
    def timelastmessage(self, value):
        self._timelastmessage = value


