import sqlite3

import pandas as pd
import nltk as nl
from discord import Embed as emb
import math
import pickle
from collections import defaultdict


class Catunits:
    def __init__(self):
        self._cats = pd.read_csv('unitdata10.1.tsv', sep='\t')
        self._customnames = None
        try:
            self._customnames = pickle.load(open('catCustomUnits.pkl', 'rb'))  # this is a dictionary
        except FileNotFoundError:
            self._customnames = {}

    def getrow(self, row):
        if row < 0:
            return None
        returned = None
        try:
            returned = self._cats.iloc[row]
        except IndexError:
            returned = None
        return returned

    def getnamebycode(self, id):
        returned = None
        try:
            returned = self._cats.iloc[id][98]
        except IndexError:
            pass
        return returned


    def getUnitCode(self, identifier, errors):
        try:  # was this a string or a int?
            locator = [int(identifier), 0]
        except ValueError:
            locator = self.closeEnough(identifier, errors)
            if locator == None:
                return "no result"
            if len(locator[0]) > 1:
                return "name not unique"
            locator[0] = locator[0][0]
        return locator

    def getstatsEmbed(self, cat, level, unitcode, extraparam = []):
        isinline = True
        title = 'Stats of ' + cat[96]
        if len(cat[98]) > 1:
            title = 'Stats of ' + cat[98]
        whichform = unitcode - 1 if unitcode > 1019 else unitcode
        if whichform % 3 == 0:
            title += ' - First form'
        elif whichform % 3 == 1:
            title += ' - Evolved form'
        else:
            title += ' - True form'
        title += ' - Unitcode: ' + str(unitcode)
        catEmbed = emb(description=title, color=0xff3300)
        catEmbed.set_author(name='Cat Bot')
        rarity = ''
        if cat[97] == 0:
            rarity = 'Normal Rare'
        elif cat[97] == 1:
            rarity = 'Special Rare'
        elif cat[97] == 2:
            rarity = 'Rare'
        elif cat[97] == 3:
            rarity = 'Super Rare'
        elif cat[97] == 4:
            rarity = 'Uber Super Rare'
        elif cat[97] == 5:
            rarity = 'Legend Rare'
        catEmbed.add_field(name='Level - Rarity', value=str(level) + ' - ' + rarity, inline=isinline)
        lvmult = float(self.levelMultiplier(cat[97], unitcode, level))
        hpv = str(math.ceil(int(cat[0]) * lvmult)) + ' HP - ' + str(round(int(cat[1]), 0)) + ' KB'
        catEmbed.add_field(name='HP - Knockbacks', value=hpv, inline=isinline)
        dmg = str(math.ceil(int(cat[3]) * lvmult))
        tba = round(int(cat[100]) / 30, 2)
        if int(cat[59]) > 0:
            dmg += '/' + str(math.ceil(int(cat[59]) * lvmult))
        if int(cat[60]) > 0:
            dmg += '/' + str(math.ceil(int(cat[60]) * lvmult))
        dps = ' Damage - ' + str(round((cat[3] + cat[59] + cat[60])*lvmult/tba)) + ' DPS'
        damagekind = ''
        if cat[12] == 1:
            damagekind += 'area'
        else:
            damagekind += 'single'
        if cat[44] > 0:
            if cat[45] > 0:
                damagekind += ', long range'
            elif cat[45] < 0:
                damagekind += ', omnistrike'
        damagetype = 'Damage (' + damagekind + ') - DPS'
        catEmbed.add_field(name=damagetype, value=dmg + dps, inline=isinline)
        catEmbed.add_field(name='Speed - Attack Frequency', value=str(round(int(cat[2]), 0)) + ' - ' + str(tba) + 's',
                           inline=isinline)
        catEmbed.add_field(name='Cost - Respawn', value=str(round(int(cat[6] * 1.5), 0)) + ' - ' + str(
            round(max(((cat[7] * 2 - 254) / 30), 2), 2)) + 's', inline=isinline)
        rangestr = ''
        if ',' in damagekind:  # it's long range or omni
            leftrange = str(max(round(int(cat[44]), 0), round(int(cat[44] + cat[45]))))
            rightrange = str(min(round(int(cat[44]), 0), round(int(cat[44] + cat[45]))))
            rangestr += leftrange + ' to ' + rightrange + '; stands at ' + str(round(int(cat[5])))
        else:  # otherwise only range is needed
            rangestr += str(round(int(cat[5])))
        catEmbed.add_field(name='Range', value=rangestr, inline=isinline)
        catEmbed.set_thumbnail(url=self.cattotriaitpics(cat))
        offensivestr = ''
        if cat[23] > 0:  # strong
            offensivestr += 'Strong, '
        if cat[24] > 0:  # knockback
            offensivestr += 'Knockback ' + str(round(int(cat[24]))) + '%, '
        if cat[25] > 0:  # freezes
            offensivestr += 'Freeze ' + str(round(int(cat[25]))) + '% (' + str(round(int(cat[26]) / 30, 2)) + 's), '
        if cat[27] > 0:  # slow
            offensivestr += 'Slow ' + str(round(int(cat[27]))) + '% (' + str(round(int(cat[28]) / 30, 2)) + 's), '
        if cat[30] > 0:  # massive damage
            offensivestr += 'Massive Damage, '
        if cat[31] > 0:  # critical
            offensivestr += 'Critical ' + str(round(int(cat[31]))) + '%, '
        if cat[32] > 0:  # targets only
            offensivestr += 'Targets only, '
        if cat[33] > 0:  # cash
            offensivestr += 'Double money, '
        if cat[34] > 0:  # base destroyer
            offensivestr += 'Base destroyer, '
        if cat[35] > 0:  # wave attack
            if cat[94] > 0:  # alternative wave
                offensivestr += "Smallwave"
            else:  # regular
                offensivestr += "Wave"
            offensivestr += ' attack ' + str(round(int(cat[35]))) + '% (' + str(
                333 + round(int(cat[36]) - 1) * 200) + ' range), '
        if cat[37] > 0:  # weaken
            offensivestr += 'Weaken ' + str(round(int(cat[37]))) + '% (' + str(round(int(cat[39]))) + '% power, ' + str(
                round(int(cat[38]) / 30, 2)) + 's), '
        if cat[40] > 0:  # strengthen
            offensivestr += 'Strengthen +' + str(round(int(cat[41]))) + '% (at ' + str(round(int(cat[40]))) + '% hp), '
        if cat[52] > 0:  # zombie killer
            offensivestr += 'Zombie killer, '
        if cat[53] > 0:  # witch killer (collab)
            offensivestr += 'Witch killer, '
        if cat[70] > 0:  # barrier breaks
            offensivestr += 'Barrier breaks ' + str(round(int(cat[70]))) + '%, '
        if cat[71] > 0:  # warp, currently unused
            offensivestr += 'Warp ' + str(round(int(cat[71]))) + '% (' + str(round(int(cat[73]))) + '-' + str(
                round(int(cat[74]))) + ', ' + str(round(int(cat[72] / 30, 2))) + 's), '
        if cat[81] > 0:  # insane damage
            offensivestr += 'Insane damage, '
        if cat[82] > 0:  # savage blow
            offensivestr += 'Savage Blow ' + str(round(int(cat[82]))) + '% (' + str(
                round(int(cat[83]))) + '% extra power), '
        if cat[86] > 0:  # surge attack
            offensivestr += 'Surge Attack ' + str(round(int(cat[86]))) + '% (' + str(
                round(int(cat[87] / 4))) + '-' + str(round(int(cat[87] / 4) + int(cat[88] / 4))) + ', level ' + str(
                round(int(cat[89]))) + '), '
        if cat[92] > 0:  # curse attack
            offensivestr += 'Curses ' + str(round(int(cat[92]))) + '% for ' + str(round(cat[93] / 30, 2)) + 's, '
        offensivestr = offensivestr[:-2]
        if len(offensivestr) > 3:
            catEmbed.add_field(name='Offensive abilities', value=offensivestr, inline=isinline)
        defensivestr = ''
        if cat[29] > 0:  # strong
            defensivestr += 'Resistant, '
        if cat[42] > 0:  # survive
            defensivestr += 'Survive ' + str(round(int(cat[42]))) + '%, '
        if cat[43] > 0:  # metal
            defensivestr += 'Metal, '
        if cat[46] > 0:  # wave immune
            defensivestr += 'Wave immune, '
        if cat[47] > 0:  # wave block
            defensivestr += 'Wave block, '
        if cat[48] > 0:  # knockback immune
            defensivestr += 'Knockback immune, '
        if cat[49] > 0:  # freeze immune
            defensivestr += 'Freeze immune, '
        if cat[50] > 0:  # slow immune
            defensivestr += 'Slow immune, '
        if cat[51] > 0:  # weaken immune
            defensivestr += 'Weaken immune, '
        if cat[75] > 0:  # warp immune
            defensivestr += 'Warp immune, '
        if cat[79] > 0:  # curse immune
            defensivestr += 'Curse immune, '
        if cat[80] > 0:  # insane resist
            defensivestr += 'Insanely resists, '
        if cat[84] > 0:  # dodge
            defensivestr += 'Dodge ' + str(round(int(cat[84]))) + '% (' + str(round(int(cat[85]) / 30, 2)) + 's), '
        if cat[90] > 0:  # toxic immune
            defensivestr += 'Toxic immune, '
        if cat[91] > 0:  # surge immune
            defensivestr += 'Surge immune, '
        if len(extraparam)>0:
            if extraparam[0] > 0:
                defensivestr += 'Resist weaken ' + str(int(extraparam[0])) + '%, '
            if extraparam[1] > 0:
                defensivestr += 'Resist freeze ' + str(int(extraparam[1])) + '%, '
            if extraparam[2] > 0:
                defensivestr += 'Resist slow ' + str(int(extraparam[2])) + '%, '
            if extraparam[3] > 0:
                defensivestr += 'Resist knockback ' + str(int(extraparam[3])) + '%, '
            if extraparam[4] > 0:
                defensivestr += 'Resist waves ' + str(int(extraparam[4])) + '%, '
            if extraparam[5] > 0:
                defensivestr += 'Resist curse ' + str(int(extraparam[5])) + '%, '
            if extraparam[6] > 0:
                defensivestr += 'Resist toxic ' + str(int(extraparam[6])) + '%, '
            if extraparam[7] > 0:
                defensivestr += 'Resist surge ' + str(int(extraparam[7])) + '%, '
        defensivestr = defensivestr[:-2]
        if len(defensivestr) > 3:
            catEmbed.add_field(name='Defensive abilities', value=defensivestr, inline=isinline)
        atkroutine = str(round(int(cat[13])))
        if cat[63] > 0:  # first attack applies effects
            atkroutine = '**' + atkroutine + '**'
        if int(cat[61]) > 0:  # has a second attack
            if cat[64] > 0:  # second attack applies effect
                atkroutine += 'f / **' + str(round(int(cat[61]))) + '**'
            else:
                atkroutine += 'f / ' + str(round(int(cat[61])))
        if int(cat[62]) > 0:
            if cat[65] > 0:  # third attack has effect
                atkroutine += 'f / **' + str(round(int(cat[62]))) + '**'
            else:
                atkroutine += 'f / ' + str(round(int(cat[62])))
        atkroutine += 'f / ' + str(round(int(cat[99]))) + 'f'  # backswing
        catEmbed.add_field(name='Attack timings', value=atkroutine, inline=isinline)
        return catEmbed

    def closeEnough(self, strToCmp, errors):
        names = self._cats.loc[:, 'enname'].to_list()
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
            customnames.append(errors + 1)
        if min(dss) > errors and customnames[0] > errors:  # both were too bad
            return None
        if min(dss) < customnames[0]:  # normal names were better
            return [closest, min(dss)]  # all of the closest and the distance of the closests
        else:  # custom names were better
            return [customnames[1], customnames[0]]  # the best matches of all custom names

    def levelMultiplier(self, rarity, unitkind, level=0):
        if unitkind in range(273, 300):
            isCrazed = True  # this is a crazed/manic unit
        else:
            isCrazed = False
        if unitkind in [75, 76, 77]:
            isBahamut = True  # this is bahamut cat
        else:
            isBahamut = False
        if unitkind in [1672, 1673, 1674]:
            isgatyacat = True
        else:
            isgatyacat = False
        if isgatyacat:
            toret = float(min(20, level) * 0.25)
            if level > 20:
                toret += float(min(10, level - 20) * 0.75)
                if level > 30:
                    toret += float(min(10, level - 30) * 1.5)
                    if level > 40:
                        toret += float(min(10, level - 40) * 2.25)
            return 2 + toret * 2
        if isBahamut:
            toret = float(min(30, level) * 0.25)
            if level > 30:
                toret += float((level - 30) * 0.125)
            return 2 + toret * 2
        if isCrazed:
            toret = float(min(20, level) * 0.25)
            if level > 20:
                toret += float((level - 20) * 0.125)
            return 2 + toret * 2
        toret = float(min(60, level) * 0.25)
        if rarity == 2:
            if level > 60:
                toret += float(min(10, level - 60) * 0.25)
            if level > 70:
                toret += float(min(20, level - 70) * 0.125)
            if level > 90:
                toret += float((level - 90) * 0.0625)
        else:
            if level > 60:
                toret += float(min(20, level - 60) * 0.125)
            if rarity in [5, 4, 3] and level > 80:
                toret += float((level - 80) * 0.0625)
            if rarity not in [5, 4, 3] and level > 80:
                toret += float((level - 80) * 0.125)
        return 2 + toret * 2

    def cattotriaitpics(self, cat):  # for each trait, add '1' to the string if it has the trait, '0' otherwise
        fstr = ''
        if cat[10] != 0:  # antired
            fstr += '1'
        else:
            fstr += '0'
        if cat[16] != 0:  # antifloating
            fstr += '1'
        else:
            fstr += '0'
        if cat[17] != 0:  # antiblack
            fstr += '1'
        else:
            fstr += '0'
        if cat[18] != 0:  # antimetal
            fstr += '1'
        else:
            fstr += '0'
        if cat[19] != 0:  # antiwhite
            fstr += '1'
        else:
            fstr += '0'
        if cat[20] != 0:  # antiangel
            fstr += '1'
        else:
            fstr += '0'
        if cat[21] != 0:  # antialien
            fstr += '1'
        else:
            fstr += '0'
        if cat[22] != 0:  # antizombie
            fstr += '1'
        else:
            fstr += '0'
        if cat[78] != 0:  # antirelic
            fstr += '1'
        else:
            fstr += '0'
        return 'https://raw.githubusercontent.com/ElMustacho/catbot-v1.1/master/traitpics/' + fstr + '.png'

    def getnames(self, cat, catcode):
        name = cat[97]
        allnames = 'The custom names of ' + name + ' are: '
        for key, value in self._customnames.items():
            if value == catcode:
                allnames += key + '; '
        if allnames[-2:] == ': ':
            allnames = name + ' has no custom name.'
        return allnames

    def removename(self, catcode, nametoremove):
        for key, value in self._customnames.items():
            if value == catcode and nametoremove == key:
                del self._customnames[nametoremove]
                self.storedict()
                return True
        return False

    def givenewname(self, unitcode, newname):
        lowernames = {k.lower(): v for k, v in self._customnames.items()}
        if newname.lower() in lowernames:  # can't have a name refer to 2 different units
            return False
        self._customnames[newname] = unitcode
        self.storedict()
        return True

    def storedict(self):
        with open('catCustomUnits.pkl', 'wb') as f:
            pickle.dump(self._customnames, f, pickle.DEFAULT_PROTOCOL)

    @staticmethod  # TODO fix the warning, try to use .loc, also fix last talents
    def apply_talent(unit, talent, level, extra_param):
        if level < 1 or level > talent[3]:  # invalid level for talent
            if talent[3] == 0:  # ponos sometimes sets to 0 the max level, when it really meant 1
                level = 1
            else:
                level = talent[3]
        first_param = talent[4] + (level - 1) * ((talent[5] - talent[4]) / max(talent[3] - 1, 1))
        second_param = talent[6] + (level - 1) * ((talent[7] - talent[6]) / max(talent[3] - 1, 1))
        third_param = talent[8] + (level - 1) * ((talent[9] - talent[8]) / max(talent[3] - 1, 1))
        fourth_param = talent[10] + (level - 1) * ((talent[11] - talent[10]) / max(talent[3] - 1, 1))
        if talent[2] == 1:  # weaken
            unit[37] += first_param
            unit[38] += second_param
            unit[39] += third_param
        elif talent[2] == 2:  # freeze
            unit[25] += first_param
            unit[26] += second_param
        elif talent[2] == 3:  # slow
            unit[27] += first_param
            unit[28] += second_param
        elif talent[2] == 4:  # target only
            unit[32] |= 1
        elif talent[2] == 5:  # strong
            unit[23] |= 1
        elif talent[2] == 6:  # resist
            unit[29] |= 1
        elif talent[2] == 7:  # massive damage
            unit[30] |= 1
        elif talent[2] == 8:  # knockback
            unit[24] += first_param
        elif talent[2] == 9:  # warp (unused)
            pass
        elif talent[2] == 10:  # strengthen
            unit[40] += 100 - first_param
            unit[41] += second_param
        elif talent[2] == 11:  # survive
            unit[42] += first_param
        elif talent[2] == 12:  # base destroyer
            unit[34] |= 1
        elif talent[2] == 13:  # critical (unused)
            pass
        elif talent[2] == 14:  # zombie killer
            unit[52] |= 1
        elif talent[2] == 15:  # barrier breaker
            unit[70] += first_param
        elif talent[2] == 16:  # double cash
            unit[33] |= 1
        elif talent[2] == 17:  # wave attack
            unit[35] += first_param
            unit[36] += second_param
        elif talent[2] == 18:  # resists weaken
            extra_param[0] = first_param
        elif talent[2] == 19:  # resists freeze
            extra_param[1] = first_param
        elif talent[2] == 20:  # resists slow
            extra_param[2] = first_param
        elif talent[2] == 21:  # resists knockback
            extra_param[3] = first_param
        elif talent[2] == 22:  # resists waves
            extra_param[4] = first_param
        elif talent[2] == 23:  # wave immune (unused)
            pass
        elif talent[2] == 24:  # warp block (unused)
            pass
        elif talent[2] == 25:  # curse immunity
            unit[79] |= 1
        elif talent[2] == 26:  # resist curse
            extra_param[5] = first_param
        elif talent[2] == 27:  # hp up
            unit[0] *= (1+first_param/100)
        elif talent[2] == 28:  # atk up
            unit[3] *= (1 + first_param / 100)
            unit[59] *= (1 + first_param / 100)
            unit[60] *= (1 + first_param / 100)
        elif talent[2] == 29:  # speed up
            unit[2] += first_param
        elif talent[2] == 30:  # knockback chance up (unused)
            pass
        elif talent[2] == 31:  # cost down
            unit[6] = unit[6] - first_param
        elif talent[2] == 32:  # recharge down
            unit[7] = unit[7] - first_param
        elif talent[2] == 33:  # target red
            unit[10] |= 1
        elif talent[2] == 34:  # target floating
            unit[16] |= 1
        elif talent[2] == 35:  # target black
            unit[17] |= 1
        elif talent[2] == 36:  # target metal
            unit[18] |= 1
        elif talent[2] == 37:  # target angel
            unit[20] |= 1
        elif talent[2] == 38:  # target alien
            unit[21] |= 1
        elif talent[2] == 39:  # target zombies
            unit[22] |= 1
        elif talent[2] == 40:  # target relic
            unit[78] |= 1
        elif talent[2] == 41:  # target traitless
            unit[19] |= 1
        elif talent[2] == 42:  # weaken duration up
            unit[38] += first_param
        elif talent[2] == 43:  # freeze duration up
            unit[26] += second_param
        elif talent[2] == 44:  # slow duration up
            unit[28] += second_param
        elif talent[2] == 45:  # knockback chance up
            unit[24] += first_param
        elif talent[2] == 46:  # strengthen power up
            unit[41] += second_param
        elif talent[2] == 47:  # survive chance
            unit[42] += first_param
        elif talent[2] == 48:  # critical chance
            unit[31] += first_param
        elif talent[2] == 49:  # barrier breaker chance
            unit[70] += first_param
        elif talent[2] == 50:  # wave chance
            pass
        elif talent[2] == 51:  # warp duration (unused)
            pass
        elif talent[2] == 52:  # critical
            unit[31] += first_param
        elif talent[2] == 53:  # weaken immune
            unit[51] |= 1
        elif talent[2] == 54:  # freeze immune
            unit[49] |= 1
        elif talent[2] == 55:  # slow immune
            unit[50] |= 1
        elif talent[2] == 56:  # knockback immune
            unit[48] |= 1
        elif talent[2] == 57:  # wave immune
            unit[46] |= 1
        elif talent[2] == 58:  # warp block
            unit[75] |= 1
        elif talent[2] == 59:  # savage blow
            unit[82] += first_param
            unit[83] += second_param
        elif talent[2] == 60:  # dodge
            unit[84] += first_param
            unit[85] += second_param
        elif talent[2] == 61:  # savage blow chance
            pass
        elif talent[2] == 62:  # dodge duration
            pass
        elif talent[2] == 63:  # slow chance
            unit[27] += first_param
        elif talent[2] == 64:  # resist toxic
            extra_param[6] = first_param
        elif talent[2] == 65:  # toxic immune
            unit[90] |= 1
        elif talent[2] == 66:  # resist surge
            extra_param[7] = first_param
        elif talent[2] == 67:  # surge immune
            unit[91] |= 1
        elif talent[2] == 68:  # surge attack
            unit[86] += first_param
            unit[87] += third_param
            unit[88] += fourth_param
            unit[89] += second_param
        elif talent[2] == 69:  # slow relic
            unit[27] += first_param
            unit[28] += second_param
            unit[78] |= 1
        elif talent[2] == 70:  # weaken relic
            unit[37] += first_param
            unit[38] += second_param
            unit[39] += second_param
            unit[78] |= 1
        elif talent[2] == 71:  # weaken alien
            unit[37] += first_param
            unit[38] += second_param
            unit[39] += second_param
            unit[21] |= 1
        elif talent[2] == 72:  # slow metal
            unit[27] += first_param
            unit[28] += second_param
            unit[18] |= 1
        elif talent[2] == 73:  # knockback zombies
            unit[24] += first_param
            unit[22] |= 1
        return [unit, extra_param]

    def get_talents_by_id(self, unit_id):
        try:
            conn = sqlite3.connect('file:talents.db?mode=rw', uri=True)  # open only if exists
            cursor = conn.cursor()
            results = cursor.execute("select * from talents where unit_id = ?/3.0", (unit_id,)).fetchall()
        except sqlite3.OperationalError:  # database not found
            return "Database for cat comboes not found."
        if len(results) == 0:
            if unit_id>1017:
                return str(self.getnamebycode(unit_id)) + " doesn't have talents."
            else:
                return str(self.getnamebycode(unit_id+2)) + " doesn't have talents."
        return results

    def get_talent_explanation(self, unit_id):
        try:
            conn = sqlite3.connect('file:talents.db?mode=rw', uri=True)  # open only if exists
            cursor = conn.cursor()
            results = cursor.execute("select talents_explanation.description_text from talents join talents_explanation on talents.description=talents_explanation.description_id where unit_id = ?/3.0", (unit_id,)).fetchall()
        except sqlite3.OperationalError:  # database not found
            return "Database for cat comboes not found."
        if len(results) == 0:
            if unit_id > 1017:
                return str(self.getnamebycode(unit_id)) + " doesn't have talents."
            else:
                return str(self.getnamebycode(unit_id+2)) + " doesn't have talents."
        return results
