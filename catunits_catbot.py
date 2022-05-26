import sqlite3

import pandas as pd
import nltk as nl
from discord import Embed as emb
import math
import pickle
from collections import defaultdict


class Catunits:
    def __init__(self):
        self._cats = pd.read_csv('auto_units.tsv', sep='\t')
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
            returned = self._cats.iloc[id][-4]
        except IndexError:
            pass
        return returned

    def getUnitCode(self, identifier, errors):
        try:  # was this a string or a int?
            locator = [int(identifier), 0]
        except (ValueError, TypeError):
            locator = self.closeEnough(identifier, errors)
            if locator is None:
                return ["no result"]
            if len(locator[0]) > 1:
                return ["name not unique", locator[0]]
            locator[0] = locator[0][0]
        return locator

    def getstatsEmbed(self, cat, level, unitcode, extraparam = []):  #todo made up stats should be accessed from right
        isinline = True
        title = 'Stats of ' + cat[-6]
        if len(cat[-6]) > 1:
            title = 'Stats of ' + cat[-4]
        whichform = unitcode
        if whichform % 3 == 0:
            title += ' - First form'
        elif whichform % 3 == 1:
            title += ' - Evolved form'
        else:
            title += ' - True form'
        title += ' - Unitcode: ' + str(whichform) + ' (' + str(int(whichform/3)) + '-' + str(int(whichform%3)) + ')'
        catEmbed = emb(description=title, color=0xff3300)
        catEmbed.set_author(name='Cat Bot')
        rarity = ''
        if cat[-5] == 0:
            rarity = 'Normal Rare'
        elif cat[-5] == 1:
            rarity = 'Special Rare'
        elif cat[-5] == 2:
            rarity = 'Rare'
        elif cat[-5] == 3:
            rarity = 'Super Rare'
        elif cat[-5] == 4:
            rarity = 'Uber Super Rare'
        elif cat[-5] == 5:
            rarity = 'Legend Rare'
        catEmbed.add_field(name='Level - Rarity', value=str(level) + ' - ' + rarity, inline=isinline)
        lvmult = float(self.levelMultiplier(cat[-5], unitcode, level))
        lives_once = ''
        if cat[58] > 0:
            lives_once = ' (hits once before dying)'
        hpv = str(math.ceil(int(cat[0]) * lvmult)) + ' HP' + lives_once + ' - ' + str(round(int(cat[1]), 0)) + ' KB'
        catEmbed.add_field(name='HP - Knockbacks', value=hpv, inline=isinline)
        if len(extraparam) > 0:
            talent_atk = extraparam[8]
        else:
            talent_atk = 1
        dmg = str(round(math.floor(math.floor(cat[3] * lvmult) * max(1, talent_atk))))
        tba = round(int(cat[-2]) / 30, 2)
        if int(cat[59]) > 0:
            dmg += '/' + str(round(math.floor(math.floor(cat[59] * lvmult) * max(1, talent_atk))))
        if int(cat[60]) > 0:
            dmg += '/' + str(round(math.floor(math.floor(cat[60] * lvmult) * max(1, talent_atk))))
        dps = ' Damage - ' + str(round(math.floor(math.floor((cat[3]+cat[59]+cat[60]) * lvmult) *
                                                  max(1, talent_atk))/tba)) + ' DPS'
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
        if cat[99] > 0 or cat[102] > 0:  # multiarea attack
            damagekind += ', multiarea'
        damagetype = 'Damage (' + damagekind + ') - DPS'
        catEmbed.add_field(name=damagetype, value=dmg + dps, inline=isinline)
        catEmbed.add_field(name='Speed - Attack Frequency', value=str(round(int(cat[2]), 0)) + ' - ' + str(tba) + 's',
                           inline=isinline)
        catEmbed.add_field(name='Cost - Respawn', value=str(round(int(cat[6] * 1.5), 0)) + ' - ' + str(
            round(max(((cat[7] * 2 - 264) / 30), 2), 2)) + 's', inline=isinline)
        rangestr = ''
        if ',' in damagekind:  # it's long range or omni
            if cat[99] > 0 and cat[102] == 0:  # multiarea 1, gods this stuff is a mess
                second_range_begin = str(int(cat[100]))
                second_range_end = str(int(cat[100] + cat[101]))

                leftrange = str(min(round(int(cat[44]), 0), round(int(cat[44] + cat[45]))))
                rightrange = str(max(round(int(cat[44]), 0), round(int(cat[44] + cat[45]))))
                rangestr += leftrange + ' to ' + rightrange + ' | ' + second_range_begin + ' to ' + second_range_end + '; stands at ' + str(
                    round(int(cat[5])))

            elif cat[99] > 0 and cat[102] > 0:  # multiarea 2
                second_range_begin = str(int(cat[100]))
                second_range_end = str(int(cat[100] + cat[101]))

                third_range_begin = str(int(cat[103]))
                third_range_end = str(int(cat[103] + cat[104]))

                leftrange = str(min(round(int(cat[44]), 0), round(int(cat[44] + cat[45]))))
                rightrange =  str(max(round(int(cat[44]), 0), round(int(cat[44] + cat[45]))))
                rangestr += leftrange + ' to ' + rightrange + ' | ' + second_range_begin + ' to ' + second_range_end + ' | ' + third_range_begin + ' to ' + third_range_end + '; stands at ' + str(
                    round(int(cat[5])))

            else:

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
                offensivestr += "Mini-wave"
            else:  # regular
                offensivestr += "Wave"
            offensivestr += ' attack ' + str(round(int(cat[35]))) + '% (' + str(
                333 + round(int(cat[36]) - 1) * 200) + ' range, level '+str(cat[36])+'), '
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
        if cat[95] > 0:  # shield breaks
            offensivestr += 'Shield Piercing '+str(int(cat[95]))+'%, '
        if cat[98] > 0:  # corpse killer
            offensivestr += 'Soulstrike, '
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
        misc_abilities = ''
        if cat[97] > 0:  # colossus killer
            misc_abilities += 'Colossus Killer, '
        if cat[77] > 0:  # eva killer
            misc_abilities += 'Eva Killer, '
        if cat[54] > 0:  # witch killer
            misc_abilities += 'Witch Killer, '
        if cat[105] > 0:  # target Behemoth
            misc_abilities += 'Behemoth Slayer, '
        if cat[106] > 0:  # Behemoth dodge
            misc_abilities += 'Behemoth dodge ' + str(round(int(cat[106]))) + '% (' + str(round(int(cat[107]) / 30, 2)) + 's), '

        misc_abilities = misc_abilities[:-2]
        atkroutine = str(round(int(cat[13])))
        if cat[63] > 0:  # first attack applies effects
            atkroutine = '__**' + atkroutine + '**__'
        if int(cat[61]) > 0:  # has a second attack
            if cat[64] > 0:  # second attack applies effect
                atkroutine += 'f / __**' + str(round(int(cat[61]))) + '**__'
            else:
                atkroutine += 'f / ' + str(round(int(cat[61])))
        if int(cat[62]) > 0:
            if cat[65] > 0:  # third attack has effect
                atkroutine += 'f / __**' + str(round(int(cat[62]))) + '**__'
            else:
                atkroutine += 'f / ' + str(round(int(cat[62])))
        atkroutine += 'f / ' + str(round(int(cat[-3]))) + 'f'  # backswing
        catEmbed.add_field(name='Attack timings', value=atkroutine, inline=isinline)
        if len(misc_abilities) > 3:
            catEmbed.add_field(name='Miscellaneous abilities', value=misc_abilities, inline=isinline)
        return catEmbed

    def closeEnough(self, strToCmp, errors):
        strToCmp = strToCmp.lower()
        names = self._cats.loc[:, 'enname'].to_list()
        names = [str(x).lower() for x in names]
        # edit distance of everything in the tsv
        dss = list(map(lambda x: edit_distance_fast(x, strToCmp, errors), names))

        closest = [i for i, x in enumerate(dss) if x == min(dss)]

        # from dictionary
        distancedict = defaultdict(list)
        for i in self._customnames:
            distancedict[edit_distance_fast(strToCmp, i.lower(),errors)].append(self._customnames[i])
        customnames = []
        try:
            customnames = min(distancedict.items())
        except ValueError:  # empty custom names
            customnames.append(errors + 1)
        if min(dss) > errors and customnames[0] > errors:  # both were too bad
            return None
        if min(dss) < customnames[0]:  # normal names were better
            return [closest, min(dss), 'original']  # all of the closest and the distance of the closest
        elif min(dss) == customnames[0]:  # equally good names
            return [list(set(closest+customnames[1])), min(dss), 'mixed']
        else:  # custom names were better
            return [customnames[1], customnames[0], 'custom']  # the best matches of all custom names

    def levelMultiplier(self, rarity, unitkind, level=0):
        if unitkind in range(273, 300):
            isCrazed = True  # this is a crazed/manic unit
        else:
            isCrazed = False
        if unitkind in [75, 76, 77]:
            isBahamut = True  # this is bahamut cat
        else:
            isBahamut = False
        if unitkind in [1674, 1675, 1676]:
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
        if cat[96] != 0:  # antidevil
            fstr += '1'
        else:
            fstr += '0'
        return 'https://raw.githubusercontent.com/ElMustacho/catbot-v1.1/master/new_pics/' + fstr + '.png'

    def getnames(self, cat, catcode):
        name = cat[-3]
        allnames = 'The custom names of ' + name + ' are: '
        for key, value in self._customnames.items():
            if value == catcode:
                allnames += key + '; '
        if allnames[-2:] == ': ':
            allnames = name + ' has no custom name. '
        return allnames[:-1]

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

    @staticmethod
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
        talent_to_apply = talent[-2]
        if talent_to_apply == 1:  # weaken
            unit[37] += first_param
            unit[38] += second_param
            unit[39] += 100 - third_param
        elif talent_to_apply == 2:  # freeze
            unit[25] += first_param
            unit[26] += second_param
        elif talent_to_apply == 3:  # slow
            unit[27] += first_param
            unit[28] += second_param
        elif talent_to_apply == 4:  # target only
            unit[32] |= 1
        elif talent_to_apply == 5:  # strong
            unit[23] |= 1
        elif talent_to_apply == 6:  # resist
            unit[29] |= 1
        elif talent_to_apply == 7:  # massive damage
            unit[30] |= 1
        elif talent_to_apply == 8:  # knockback
            unit[24] += first_param
        elif talent_to_apply == 9:  # warp (unused)
            pass
        elif talent_to_apply == 10:  # strengthen
            unit[40] += 100 - first_param
            unit[41] += second_param
        elif talent_to_apply == 11:  # survive
            unit[42] += first_param
        elif talent_to_apply == 12:  # base destroyer
            unit[34] |= 1
        elif talent_to_apply == 13:  # critical (unused)
            pass
        elif talent_to_apply == 14:  # zombie killer
            unit[52] |= 1
        elif talent_to_apply == 15:  # barrier breaker
            unit[70] += first_param
        elif talent_to_apply == 16:  # double cash
            unit[33] |= 1
        elif talent_to_apply == 17:  # wave attack
            unit[35] += first_param
            unit[36] += second_param
        elif talent_to_apply == 18:  # resists weaken
            extra_param[0] = first_param
        elif talent_to_apply == 19:  # resists freeze
            extra_param[1] = first_param
        elif talent_to_apply == 20:  # resists slow
            extra_param[2] = first_param
        elif talent_to_apply == 21:  # resists knockback
            extra_param[3] = first_param
        elif talent_to_apply == 22:  # resists waves
            extra_param[4] = first_param
        elif talent_to_apply == 23:  # wave immune (unused)
            pass
        elif talent_to_apply == 24:  # warp block (unused)
            pass
        elif talent_to_apply == 25:  # curse immunity
            unit[79] |= 1
        elif talent_to_apply == 26:  # resist curse
            extra_param[5] = first_param
        elif talent_to_apply == 27:  # hp up
            unit[0] *= (1+first_param/100)
        elif talent_to_apply == 28:  # atk up
            extra_param[8] = (1 + first_param / 100)
        elif talent_to_apply == 29:  # speed up
            unit[2] += first_param
        elif talent_to_apply == 30:  # knockback chance up (unused)
            pass
        elif talent_to_apply == 31:  # cost down
            unit[6] = unit[6] - first_param
        elif talent_to_apply == 32:  # recharge down
            unit[7] = unit[7] - first_param
        elif talent_to_apply == 33:  # target red
            unit[10] |= 1
        elif talent_to_apply == 34:  # target floating
            unit[16] |= 1
        elif talent_to_apply == 35:  # target black
            unit[17] |= 1
        elif talent_to_apply == 36:  # target metal
            unit[18] |= 1
        elif talent_to_apply == 37:  # target angel
            unit[20] |= 1
        elif talent_to_apply == 38:  # target alien
            unit[21] |= 1
        elif talent_to_apply == 39:  # target zombies
            unit[22] |= 1
        elif talent_to_apply == 40:  # target relic
            unit[78] |= 1
        elif talent_to_apply == 41:  # target traitless
            unit[19] |= 1
        elif talent_to_apply == 42:  # weaken duration up
            unit[38] += second_param
        elif talent_to_apply == 43:  # freeze duration up
            unit[26] += second_param
        elif talent_to_apply == 44:  # slow duration up
            unit[28] += second_param
        elif talent_to_apply == 45:  # knockback chance up
            unit[24] += first_param
        elif talent_to_apply == 46:  # strengthen power up
            unit[41] += second_param
        elif talent_to_apply == 47:  # survive chance
            unit[42] += first_param
        elif talent_to_apply == 48:  # critical chance
            unit[31] += first_param
        elif talent_to_apply == 49:  # barrier breaker chance
            unit[70] += first_param
        elif talent_to_apply == 50:  # wave chance
            pass
        elif talent_to_apply == 51:  # warp duration (unused)
            pass
        elif talent_to_apply == 52:  # critical
            unit[31] += first_param
        elif talent_to_apply == 53:  # weaken immune
            unit[51] |= 1
        elif talent_to_apply == 54:  # freeze immune
            unit[49] |= 1
        elif talent_to_apply == 55:  # slow immune
            unit[50] |= 1
        elif talent_to_apply == 56:  # knockback immune
            unit[48] |= 1
        elif talent_to_apply == 57:  # wave immune
            unit[46] |= 1
        elif talent_to_apply == 58:  # warp block
            unit[75] |= 1
        elif talent_to_apply == 59:  # savage blow
            unit[82] += first_param
            unit[83] += second_param
        elif talent_to_apply == 60:  # dodge
            unit[84] += first_param
            unit[85] += second_param
        elif talent_to_apply == 61:  # savage blow chance
            pass
        elif talent_to_apply == 62:  # dodge duration
            pass
        elif talent_to_apply == 63:  # slow chance
            unit[27] += first_param
        elif talent_to_apply == 64:  # resist toxic
            extra_param[6] = first_param
        elif talent_to_apply == 65:  # toxic immune
            unit[90] |= 1
        elif talent_to_apply == 66:  # resist surge
            extra_param[7] = first_param
        elif talent_to_apply == 67:  # surge immune
            unit[91] |= 1
        elif talent_to_apply == 68:  # surge attack
            unit[86] += first_param
            unit[87] += third_param
            unit[88] += fourth_param
            unit[89] += second_param
        elif talent_to_apply == 69:  # slow relic
            unit[27] += first_param
            unit[28] += second_param
            unit[78] |= 1
        elif talent_to_apply == 70:  # weaken relic
            unit[37] += first_param
            unit[38] += second_param
            unit[39] += 100 - third_param
            unit[78] |= 1
        elif talent_to_apply == 71:  # weaken alien
            unit[37] += first_param
            unit[38] += second_param
            unit[39] += 100 - third_param
            unit[21] |= 1
        elif talent_to_apply == 72:  # slow metal
            unit[27] += first_param
            unit[28] += second_param
            unit[18] |= 1
        elif talent_to_apply == 73:  # knockback zombies
            unit[24] += first_param
            unit[22] |= 1
        elif talent_to_apply == 74:  # freeze chance up
            unit[25] += first_param
        elif talent_to_apply == 75:  # knockback alien
            unit[24] += first_param
            unit[21] |= 1
        elif talent_to_apply == 76:  # freeze metal
            unit[25] += first_param
            unit[26] += second_param
            unit[18] |= 1
        elif talent_to_apply == 77:  # target aku
            unit[96] |= 1
        elif talent_to_apply == 78:  # shield pierce
            unit[95] += first_param
        elif talent_to_apply == 79:  # maybe soul killer
            unit[98] |= 1
        elif talent_to_apply == 80:  # curse
            unit[92] += first_param
            unit[93] += second_param
        return [unit, extra_param]

    def get_talents_by_id(self, unit_id):
        try:
            conn = sqlite3.connect('file:talents.db?mode=rw', uri=True)  # open only if exists
            cursor = conn.cursor()
            results = cursor.execute("select * from talents where unit_id = ?/3.0", (unit_id,)).fetchall()
        except sqlite3.OperationalError:  # database not found
            return "Database for cat comboes not found."
        if len(results) == 0:
            return "The given unit doesn't have talents."
            
        return results

    def get_talent_explanation(self, unit_id):
        try:
            conn = sqlite3.connect('file:talents.db?mode=rw', uri=True)  # open only if exists
            cursor = conn.cursor()
            results = cursor.execute("select talents_explanation.description_text from talents join talents_explanation on talents.description=talents_explanation.description_id where unit_id = ?/3.0", (unit_id,)).fetchall()
        except sqlite3.OperationalError:  # database not found
            return "Database for cat comboes not found."
        if len(results) == 0:
            return str(self.getnamebycode(unit_id)) + " doesn't have talents."
            
        return results

def edit_distance_fast(s1, s2, errors):
    '''
    Returns the edit distance between s1 and s2,
    unless distance > errors, in which case it will
    return some number greater than errors. Uses
    Ukkonen's improvement on the Wagner-Fisher algorithm.

    Credits to clam
    '''
    # ensure that len(s1) <= len(s2)
    len1, len2 = len(s1), len(s2)
    if len(s1) > len(s2):
        s1, s2 = s2, s1
        len1, len2 = len2, len1
    # distance is at least len2 - len1
    if len2 - len1 > errors:
        return errors + 1
    prev_row = [*range(len2 + 1)]
    for i, c1 in enumerate(s1):
        cur_row = [i + 1, *([errors + 1] * len2)]
        # only need to check the interval [i-errors,i+errors]
        for j in range(max(0, i - errors), min(len2, i + errors + 1)):
            cur_row[j + 1] = min(
                prev_row[j + 1] + 1,  # skip char in s1
                cur_row[j] + 1,  # skip char in s2
                prev_row[j] + (c1 != s2[j])  # substitution
            )
        prev_row = cur_row
    return cur_row[len2]