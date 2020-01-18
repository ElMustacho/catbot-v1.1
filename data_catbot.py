from datetime import datetime
import json

class Data_catbot:
    def __init__(self, auth_token, timelastmessage, requireddata):
        self._timelastmessage = timelastmessage
        self._requireddata = requireddata


    @classmethod
    def defFromFile(cls):
        with open('config.json') as json_file:
            cls.requireddata = json.load(json_file)
        cls.timelastmessage = datetime.now()
        return cls

    @property
    def timelastmessage(self):
        return self._timelastmessage

    @timelastmessage.setter
    def timelastmessage(self, value):
        self._timelastmessage = value

