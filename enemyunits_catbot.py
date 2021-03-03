import pandas as pd
import nltk as nl
from discord import Embed as emb
import math
import pickle
from collections import defaultdict

class Enemyunits:
    def __init__(self):
        self._enemies = pd.read_csv('enemyunits.tsv', sep='\t')
        self._customnames = None
        try:
            self._customnames = pickle.load(open('enemyCustomUnits.pkl', 'rb'))  # this is a dictionary
        except FileNotFoundError:
            self._customnames = {}

    def namefromcode(self, enemycode):
        returnthis = self._enemies.iloc[enemycode]
        returnthis = returnthis.iat[88]
        return returnthis

    def getrow(self, row):
        if row < 0:
            return None
        returned = None
        try:
            returned = self._enemies.iloc[row]
        except IndexError:
            returned = None
        return returned

    def closeEnough(self, strToCmp, errors):
        strToCmp = strToCmp.lower()
        names = self._enemies.loc[:, 'en names'].to_list()
        names = [str(x).lower() for x in names]
        # edit distance of everything in the tsv
        dss = list(map(lambda x: nl.edit_distance(x, strToCmp), names))

        closest = [i for i, x in enumerate(dss) if x == min(dss)]

        # from dictionary
        distancedict = defaultdict(list)
        for i in self._customnames:
            distancedict[nl.edit_distance(strToCmp, i.lower())].append(self._customnames[i])
        customnames = []
        try:
            customnames = min(distancedict.items())
        except ValueError:  # empty custom names
            customnames.append(errors+1)
        if min(dss) > errors and customnames[0] > errors:  # both were too bad
            return None
        if min(dss) < customnames[0]:  # normal names were better
            return [closest, min(dss)]  # all of the closest and the distance of the closests
        else:  # custom names were better
            return [customnames[1], customnames[0]]  # the best matches of all custom names

    def enemytraitstopic(self, enemy):  # for each trait, add '1' to the string if it has the trait, '0' otherwise
        fstr = ''
        if enemy[10] != 0:  # red
            fstr += '1'
        else:
            fstr += '0'
        if enemy[13] != 0:  # floating
            fstr += '1'
        else:
            fstr += '0'
        if enemy[14] != 0:  # black
            fstr += '1'
        else:
            fstr += '0'
        if enemy[15] != 0:  # metal
            fstr += '1'
        else:
            fstr += '0'
        if enemy[16] != 0:  # white
            fstr += '1'
        else:
            fstr += '0'
        if enemy[17] != 0:  # angel
            fstr += '1'
        else:
            fstr += '0'
        if enemy[18] != 0:  # alien
            if enemy[69] == 1:  # star alien
                fstr += '2'
            else:
                fstr += '1'
        else:
            fstr += '0'
        if enemy[19] != 0:  # zombie
            fstr += '1'
        else:
            fstr += '0'
        if enemy[72] != 0:  # relic
            fstr += '1'
        else:
            fstr += '0'
        if enemy[48] > 0:  # witch trait
            fstr = "witchtrait"
        if enemy[71] > 0:  # is eva
            fstr = "evatrait"
        return 'https://raw.githubusercontent.com/ElMustacho/catbot-v1.1/master/traitpics/' + fstr + '.png'

    def getUnitCode(self, identifier, errors):
        locator = None
        try:  # was this a string or a int?
            locator = [int(identifier), 0]
        except ValueError:
            locator = self.closeEnough(identifier, errors)
        return locator

    def getstatsembed(self, enemy, magnification, mag2=None):
        if mag2 == None:
            mag2 = magnification
        title = 'Stats of ' + str(enemy[88])
        enemyEmbed = emb(description=title, color=0x00ff00)
        enemyEmbed.set_author(name='Cat Bot')
        magstring = str(int(magnification*100)) + '%'
        if mag2 != magnification:
            magstring = magstring + ' HP, ' + str(int(round(mag2*100,0))) + '% Damage'
        enemyEmbed.add_field(name='Magnification', value=magstring, inline=True)
        hpv = str(math.ceil(int(enemy[0]) * magnification)) + ' HP - ' + str(round(int(enemy[1]), 0)) + ' KB'
        enemyEmbed.add_field(name='HP - Knockbacks', value=hpv, inline=True)
        dmg = str(math.ceil(int(enemy[3]) * mag2))
        if int(enemy[55]) > 0:
            dmg += '/' + str(math.ceil(int(enemy[55]) * mag2))
        if int(enemy[56]) > 0:
            dmg += '/' + str(math.ceil(int(enemy[56]) * mag2))
        dps = ' Damage - ' + str(math.ceil(int(enemy[3]+enemy[55]+enemy[56])*mag2*30/enemy[92])) + ' DPS'
        damagekind = ''
        if enemy[11] == 1:
            damagekind += 'area'
        else:
            damagekind += 'single'
        if enemy[35] > 0:
            if enemy[36] > 0:
                damagekind += ', long range'
            elif enemy[36] < 0:
                damagekind += ', omnistrike'
        damagetype = 'Damage (' + damagekind + ') - DPS'
        enemyEmbed.add_field(name=damagetype, value=dmg + dps, inline=True)
        tba = str(round(int(enemy[92]) / 30, 2))
        enemyEmbed.add_field(name='Speed - Attack Frequency', value=str(round(int(enemy[2]), 0)) + ' - ' + tba + 's',
                           inline=True)
        enemyEmbed.add_field(name='Cash Awarded', value=str(round(int(enemy[6]*3.95), 0)), inline=True)
        rangestr = ''
        if ',' in damagekind:  # it's long range or omni
            leftrange = str(max(round(int(enemy[35]), 0), round(int(enemy[35] + enemy[36]))))
            rightrange = str(min(round(int(enemy[35]), 0), round(int(enemy[35] + enemy[36]))))
            rangestr += leftrange + ' to ' + rightrange + '; stands at ' + str(round(int(enemy[5])))
        else:  # otherwise only range is needed
            rangestr += str(round(int(enemy[5])))
        enemyEmbed.add_field(name='Range', value=rangestr, inline=True)
        enemyEmbed.set_thumbnail(url=self.enemytraitstopic(enemy))
        offensive = ''
        if enemy[20] > 0:  # knockback
            offensive += 'Knockback ' + str(round(int(enemy[20]))) + '%, '
        if enemy[21] > 0:  # freezes
            offensive += 'Freeze ' + str(round(int(enemy[21]))) + '% (' + str(round(int(enemy[22]) / 30, 2)) + 's), '
        if enemy[23] > 0:  # slow
            offensive += 'Slow ' + str(round(int(enemy[23]))) + '% (' + str(round(int(enemy[24]) / 30, 2)) + 's), '
        if enemy[25] > 0:  # crits
            offensive += 'Critical ' + str(round(int(enemy[25]))) + '%, '
        if enemy[26] > 0:  # base destroyer
            offensive += 'Base Destroyer, '
        if enemy[27] > 0:  # wave attack
            typewave = "Wave attack "
            if enemy[86] > 0:  # it's a small wave
                typewave = "Mini-Wave "
            offensive += typewave + str(round(int(enemy[27]))) + '% (' + str(467 + round(int(enemy[28]) - 1) * 200) + ' range), '
        if enemy[29] > 0:  # weaken
            offensive += 'Weaken ' + str(round(int(enemy[29]))) + '% (' + str(round(int(enemy[31]))) + '% power, ' + str(
                round(int(enemy[30]) / 30, 2)) + 's), '
        if enemy[32] > 0:  # strengthen
            offensive += 'Strengthen ' + str(round(int(enemy[33]))) + '% (at ' + str(round(int(enemy[32]))) + '% hp), '
        if enemy[43] != 0:  # burrow
            if enemy[43] == 1:
                offensive += 'Burrows once'
            elif enemy[43] > 1:
                offensive += 'Burrows ' + str(enemy[43]) + ' times'
            else:
                offensive += 'Burrows infinite times'
            offensive += ' (for ' + str(int(enemy[44]/4)) + ' range), '
        if enemy[65] > 0:  # warp
            warp1 = str(round(int(enemy[65])))
            warp2 = str(round(int(enemy[67]/4)))
            warp3 = str(round(int(enemy[68]/4)))
            warp4 = str(round(float(enemy[66] / 30), 2))
            offensive += 'Warp ' + warp1 + '% (' + warp2 + ' / ' + warp3 + ' range, ' + warp4 + 's), '
        if enemy[73] > 0:  # curses
            offensive += 'Curses ' + str(round(int(enemy[73]))) + '% (' + str(round(int(enemy[74]) / 30, 2)) + 's), '
        if enemy[79] > 0:  # poison
            offensive += 'Poisons ' + str(round(int(enemy[79]))) + '% (' + str(int(enemy[80])) + '% hp), '
        if enemy[81] > 0:  # surge attack
            offensive += 'Surge Attack ' + str(round(int(enemy[81]))) + '% (' + str(round(int(enemy[82]/4))) + '-' + str(round(int(enemy[82]/4)+int(enemy[83]/4))) + ', level ' + str(round(int(enemy[84]))) + '), '
        offensive = offensive[:-2]
        if len(offensive) > 3:
            enemyEmbed.add_field(name='Offensive abilities', value=offensive, inline=True)
        defensive = ''
        if enemy[34] > 0:  # survive
            defensive += 'Survive ' + str(round(int(enemy[34]))) + '%, '
        if enemy[37] > 0:  # wave immune
            defensive += 'Wave immune, '
        if enemy[39] > 0:  # knockback immune
            defensive += 'Knockback immune, '
        if enemy[40] > 0:  # freeze immune
            defensive += 'Freeze immune, '
        if enemy[41] > 0:  # slow immune
            defensive += 'Slow immune, '
        if enemy[42] > 0:  # weaken immune
            defensive += 'Weaken immune, '
        if enemy[45] != 0:  # resurrects
            if enemy[45] == 1:
                defensive += 'Revives once'
            elif enemy[45] > 1:
                defensive += 'Revives ' + str(enemy[45]) + ' times'
            else:
                defensive += 'Revives until z-killed'
            defensive += ' (in ' + str(round(enemy[46]/30, 2)) + 's, at ' + str(enemy[47]) + '% hp), '
        if enemy[49] > 0:  # it's a base
            defensive += "It's a base, "
        if enemy[64] > 0:  # has a barrier
            defensive += 'Has a ' + str(int(enemy[64])) + 'hp barrier, '
        if enemy[70] > 0:  # resists warp (never used)
            defensive += 'Immune to warp, '
        if enemy[77] > 0:  # dodge
            defensive += 'Dodge ' + str(round(int(enemy[77]))) + '% (' + str(round(int(enemy[78]) / 30, 2)) + 's), '
        defensive = defensive[:-2]
        if len(defensive) > 3:
            enemyEmbed.add_field(name='Defensive abilities', value=defensive, inline=True)
        if int(enemy[59]) > 0:
            atkroutine = '**' + str(round(int(enemy[12]))) + '**'
        else:
            atkroutine = str(round(int(enemy[12])))
        if int(enemy[57]) > 0:
            if int(enemy[60]) > 0:
                atkroutine += 'f / **' + str(round(int(enemy[57]))) + '**'
            else:
                atkroutine += 'f / ' + str(round(int(enemy[57])))
        if int(enemy[58]) > 0:
            if int(enemy[61]) > 0:
                atkroutine += 'f / **' + str(round(int(enemy[58]))) + '**'
            else:
                atkroutine += 'f / ' + str(round(int(enemy[58])))
        atkroutine += 'f / ' + str(round(int(enemy[91]))) + 'f'
        enemyEmbed.add_field(name='Attack timings', value=atkroutine, inline=True)
        return enemyEmbed

    def givenewname(self, enemycode, newname):
        lowernames = {k.lower(): v for k, v in self._customnames.items()}
        if newname.lower() in lowernames:  # can't have a name refer to 2 different units
            return False
        self._customnames[newname] = enemycode
        self.storedict()
        return True

    def storedict(self):
        with open('enemyCustomUnits.pkl', 'wb') as f:
            pickle.dump(self._customnames, f, pickle.DEFAULT_PROTOCOL)

    def getnames(self, enemy, enemycode):
        name = enemy[86]
        allnames = 'The custom names of ' + name + ' are: '
        for key, value in self._customnames.items():
            if value == enemycode:
                allnames += key + '; '
        if allnames[-2:] == ': ':
            allnames = name + ' has no custom name.'
        return allnames

    def removename(self, enemy, nametoremove):
        for key, value in self._customnames.items():
            if value == enemy and nametoremove == key:
                del self._customnames[nametoremove]
                self.storedict()
                return True
        return False