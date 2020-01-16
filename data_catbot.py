from datetime import datetime

class Data_catbot:
    def __init__(self, auth_token, timelastmessage):
        self._auth_token = auth_token
        self._timelastmessage = timelastmessage
        self._purr = 0  # probably going to remove this

    @classmethod
    def defFromFile(cls):
        try:
            f = open("auth.token", "r")
            cls.auth_token = f.read(59)
        except OSError:
            print('oh shit')
        finally:
            f.close()
        cls.timelastmessage = datetime.now()
        return cls

    @property
    def timelastmessage(self):
        return self._timelastmessage

    @property
    def auth_token(self):
        return self._auth_token

    @timelastmessage.setter
    def timelastmessage(self, value):
        self._timelastmessage = value

    def purrcatbot(self):
        self._purr += 1

    @property
    def purr(self):
        return self._purr
