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

    def getstatsEmbed(self, cat, level):  # TODO complete all stats
        catEmbed = emb(description=str('Stats of ' + cat[7]), color=0xff3300)
        catEmbed.set_author(name='Cat Bot')
        catEmbed.add_field(name='Level', value=str(level), inline=True)
        lvmult = int(self.levelMultiplier(cat[2], cat[0], level))
        hpv = str(int(cat[9]) * lvmult) + ' HP - ' + str(cat[10]) + ' KB'
        catEmbed.add_field(name='HP-Knockbacks', value=hpv, inline=True)
        dmg = str(int(cat[12]) * lvmult)
        if int(cat[69]) > 0:
            dmg += '/' + str(int(cat[69]) * lvmult)
        if int(cat[70]) > 0:
            dmg += '/' + str(int(cat[70]) * lvmult)
        dps = ' Damage - ' + str(int(float(cat[-1].replace(',', '.')) * lvmult)) + ' DPS'
        damagekind = ''
        if cat[22] == 1:
            damagekind += 'area'
        else:
            damagekind += 'single'
        if cat[54] > 0:
            if cat[55] > 0:
                damagekind += ', long range'
            elif cat[55] < 0:
                damagekind += ', omnistrike'
        damagetype = 'Damage (' + damagekind + ') - DPS'
        catEmbed.add_field(name=damagetype, value=dmg+dps, inline=True)
        catEmbed.add_field(name='Speed', value=str(cat[11]), inline=True)
        catEmbed.set_thumbnail(url=self.cattotriaitpics(cat))

        return catEmbed

    def closeEnough(self, strToCmp):
        names = self._cats.loc[:, 'searchname'].to_list()
        # edit distance of everything
        dss = list(map(lambda x: nl.edit_distance(x, strToCmp), names))
        if min(dss) > 6:
            return None
        return [i for i, x in enumerate(dss) if x == min(dss)]  # all of the closest

    def levelMultiplier(self, rarity, unitkind, level=0):
        if unitkind in range(261, 287):
            isCrazed = True  # this is a crazed/manic unit
        else:
            isCrazed = False
        if unitkind == 78:
            isBahamut = True  # this is awakened bahamut cat
        else:
            isBahamut = False
        if isBahamut:
            toret = float(min(30, level)*0.25)
            if level > 30:
                toret += float((level-30)*0.125)
            return toret
        if isCrazed:
            toret = float(min(20, level) * 0.25)
            if level > 20:
                toret += float((level-20)*0.125)
            return toret
        toret = float(min(60, level)*0.25)
        if rarity == 'R':
            if level > 60:
                toret += float(min(10, level-60)*0.25)
            if level > 70:
                toret += float(min(20, level-70)*0.125)
            if level > 90:
                toret += float((level-90)*0.0625)
        else:
            if level > 60:
                toret += float(min(20, level-60)*0.125)
            if rarity in ['U', 'S'] and level > 80:
                toret += float((level-80)*0.0625)
            if rarity not in ['U', 'S'] and level > 80:
                toret += float((level-80)*0.125)
        return 2+toret*2
        # return 17

    def cattotriaitpics(self, cat):  # for each trait, add '1' to the string if it has the trait, '0' otherwise
        fstr = ''
        if cat[20] != 0:  # antired
            fstr += '1'
        else:
            fstr += '0'
        if cat[26] != 0:  # antifloating
            fstr += '1'
        else:
            fstr += '0'
        if cat[27] != 0:  # antiblack
            fstr += '1'
        else:
            fstr += '0'
        if cat[28] != 0:  # antimetal
            fstr += '1'
        else:
            fstr += '0'
        if cat[29] != 0:  # antiwhite
            fstr += '1'
        else:
            fstr += '0'
        if cat[30] != 0:  # antiangel
            fstr += '1'
        else:
            fstr += '0'
        if cat[31] != 0:  # antialien
            fstr += '1'
        else:
            fstr += '0'
        if cat[32] != 0:  # antizombie
            fstr += '1'
        else:
            fstr += '0'
        if cat[88] != 0:  # antirelic
            fstr += '1'
        else:
            fstr += '0'
        return 'https://raw.githubusercontent.com/ElMustacho/catbot-v1.1/master/traitpics/' + fstr + '.png'
