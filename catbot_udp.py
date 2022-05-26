import json
from discord import Embed
class Catbot_udp(object):
    def __init__(self,fileName):
        with open(fileName) as file:
            self.data = json.loads(file.read())

    def unitExists(self, id):
        try:
            assert self.data[id]  # todo write this in another way
            return True
        except KeyError:
            return False

    def makeEmbedFromUnit(self, id):  # if we are here we expect the unit to exist
        emb = Embed(description='UDP of '+self.data[id]['Name'], color=0xffffff)
        emb.set_author(name='Cat Bot')
        emb.add_field(name='Brief description', value=self.data[id]['Description'][0]+' [Click here for more](https://thanksfeanor.pythonanywhere.com/UDP/' + id.zfill(3)+')', inline=False)
        # uncomment to make feanor angry
        #emb.set_image(url='https://thanksfeanor.pythonanywhere.com/static/UDPCards/UDPCARD'+id+'.png')
        return emb

