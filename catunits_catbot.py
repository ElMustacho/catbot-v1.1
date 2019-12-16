import pandas as pd
import nltk as nl
from discord import Embed as emb
from PIL import Image


class Catunits:
    def __init__(self):
        # data = pd.read_csv(str('unitdata.tsv'), sep='\t')
        # headers = data.iloc[0]
        # print(headers)
        # self._cats  = pd.DataFrame(data.values[1:], columns=headers)
        self._cats = pd.read_csv(str('unitdata.tsv'), sep='\t')

    def getrow(self, row):
        if row < 0:
            return None
        returned = None
        try:
            returned = self._cats.iloc[row].values.tolist()
        except IndexError:
            returned = None
        return returned

    def getcolumn(self, column):
        return None

    def getUnitCode(self, identifier):  # TODO: make this form for real
        locator = None
        try:  # was this a string or a int?
            locator = [int(identifier)]
        except ValueError:
            locator = self.closeEnough(identifier)
        return locator

    def getstats(self, cat):  # TODO: this will need to be an embed
        stats = str(cat[7]) + '; dps lv 30 = ' + str(int(float(cat[-1].replace(',', '.'))
                                                         * self.levelMultiplier()))  # currently locked lv 30
        return stats

    def getstatsEmbed(self, cat):  # TODO level dependant
        catEmbed = emb(description=str('Stats of ' + cat[7]), color=0xff3300)
        catEmbed.set_author(name='Cat Bot')
        catEmbed.add_field(name='Level', value='30 (currently locked)', inline=True)
        hpv = str(int(cat[9]) * self.levelMultiplier()) + ' HP - ' + str(cat[10]) + 'KB'
        catEmbed.add_field(name='HP-Knockbacks', value=hpv, inline=True)
        dmg = str(int(cat[12]) * self.levelMultiplier())
        if int(cat[69]) > 0:
            dmg += '/' + str(int(cat[69])*self.levelMultiplier())
        if int(cat[70]) > 0:
            dmg += '/' + str(int(cat[70]) * self.levelMultiplier())
        dps = ' Damage - ' + str(int(float(cat[-1].replace(',', '.')) * self.levelMultiplier())) + ' DPS'
        catEmbed.add_field(name='Damage - DPS',
                           value=dmg+dps, inline=True)
        catEmbed.add_field(name='Speed', value=str(cat[11]), inline=True)
        catEmbed.set_thumbnail(url='https://i.imgur.com/NjsxXAh.png')

        return catEmbed

    def closeEnough(self, strToCmp):
        names = self._cats.loc[:, 'searchname'].to_list()
        # edit distance of everything
        dss = list(map(lambda x: nl.edit_distance(x, strToCmp), names))
        if min(dss) > 6:
            return None
        return [i for i, x in enumerate(dss) if x == min(dss)]  # all of the closest

    def levelMultiplier(self, data=None, level=None):
        return 17

    def makeimagetraits(self, cat):
        str = ''
        with Image.open('traits-images/base.png', 'r').copy() as base:
            if cat[20] != '0':  # antired
                base.paste(Image.open("traits-images/red.png"), (0, 0))
            if cat[26] != '0':  # antifloating
                base.paste(Image.open("traits-images/floating.png"), (39, 0))
            if cat[27] != '0':  # antiblack
                base.paste(Image.open("traits-images/black.png"), (78, 0))
            if cat[28] != '0':  # antimetal
                base.paste(Image.open("traits-images/metal.png"), (0, 39))
            if cat[29] != '0':  # antiwhite
                base.paste(Image.open("traits-images/white.png"), (39, 39))
            if cat[30] != '0':  # antiangel
                base.paste(Image.open("traits-images/angel.png"), (78, 39))
            if cat[31] != '0':  # antialien
                base.paste(Image.open("traits-images/alien.png"), (0, 78))
            if cat[32] != '0':  # antizombie
                base.paste(Image.open("traits-images/zombie.png"), (39, 78))
            if cat[88] != '0':  # antirelic
                base.paste(Image.open("traits-images/relic.png"), (78, 78))

        return None