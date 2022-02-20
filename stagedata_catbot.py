import math
import custom_stages
from discord import Embed as emb
import sqlite3


class Stagedata:
    def __init__(self, enemydata):
        self._enemydata = enemydata
        custom_stages.Custom_stages.setup_table()  # sets up table, does nothing if already done once in the past

    def dataToEmbed(self, enemylines, stagedata, magnification):  # TODO refine the enemylines
        stageEmbed = emb(description='Amount | First Spawn Frame *(Respawn F)* | Base Health',
                         color=0x009B77)
        stageEmbed.set_author(name='Cat Bot')
        stageEmbed.add_field(name='Stage data', value=enemylines[0][14])
        enemystring = ''
        for enemyline in enemylines:
            title = ''
            if enemyline[10] == 1:
                title = '**'
            title += self._enemydata.namefromcode(enemyline[2]) + ', ' + str(round(enemyline[4] * magnification)) + '%'
            if enemyline[10] == 1:
                title += '**'
            if enemyline[3] < 1:
                enemystring += '∞'
            else:
                enemystring += str(enemyline[3])
            enemystring += ' | ' + str(enemyline[11] * 2) + 'f'
            if enemyline[3] != 1:
                if enemyline[5] == enemyline[6]:
                    enemystring += ' *(' + str(enemyline[5] * 2) + 'f)*'
                else:
                    enemystring += ' *(' + str(enemyline[5] * 2) + '~' + str(enemyline[6] * 2) + 'f)*'
            enemystring += ' | ' + str(enemyline[7]) + '%'
            stageEmbed.add_field(name=title, value=enemystring, inline=True)
            enemystring = ''
        return stageEmbed

    def getstageid(self, stagename, errors, stagelevel = '', stagecategory = ''):
        results = None
        try:
            conn = sqlite3.connect('stages.db')
            cursor = conn.cursor()
            query = '''select stages.stage, stages.level, stages.category, stages.stageid from stages;'''
            stage = cursor.execute(query).fetchall()
            custom_stages_for_reference = custom_stages.Custom_stages.get_all_names()
            stagenames_nodiff = [x[0].lower() for x in stage]
            stagenames_nodiff = [x[:x.find('(') if x.find('(')>0 else len(x)] for x in stagenames_nodiff]
            dss = list(map(lambda x: edit_distance_fast(x, stagename, errors), stagenames_nodiff))
            custom_stagenames_nodiff = [x[0].lower() for x in custom_stages.Custom_stages.get_all_names()]
            dss_custom = list(map(lambda x: edit_distance_fast(x, stagename, errors), custom_stagenames_nodiff))
            # 1) an actual name is the best one
            # 2) a custom name is the best one
            # 3) both names sucks, in which case we check if
            # 3b) there's a good match as an actual name without the difficulty spelled in
            # 4) more than 2 any names could fit equally good, in which case
            # 4b) there's a good match if we also take in account the map for actual names
            # 4c) there's a good match if we also take in account the map and the category for actual names
            # actual names are given priority

            if min(dss) > errors and min(dss_custom) > errors:  # case 3
                stagenames = [x[0].lower() for x in stage]
                dss = list(map(lambda x: edit_distance_fast(x, stagename, errors), stagenames))
                if min(dss) > errors:  # case 3b
                    return -1
            #FIXME throws exception if empty
            best_minimum = min(min(dss),min(dss_custom))
            nearestmatch = [i for i, x in enumerate(dss) if x == best_minimum]
            nearestmatch_custom = [i for i, x in enumerate(dss_custom) if x == best_minimum]
            all_best_matches = nearestmatch + nearestmatch_custom
            if len(all_best_matches) > 1:  # this means we have more than 2 best shots
                if stagelevel == '':
                    closest = []
                    closest_custom = []
                    for near in nearestmatch:
                        closest.append(stage[near])
                    for near in nearestmatch_custom:
                        closest_custom.append(custom_stages_for_reference[near])
                    return [closest, closest_custom]
                else:
                    stagelevels = [x[1].lower() for x in stage]
                    leveldss = list(map(lambda x: edit_distance_fast(x, stagelevel, errors), stagelevels))
                    if min(leveldss) > errors:
                        results = -1
                        raise Exception('Level could not match anything.')
                    nearestlevelmatch = [i for i, x in enumerate(leveldss) if x == min(leveldss)]
                    intersection1 = [value for value in nearestlevelmatch if value in nearestmatch]
                    if len(intersection1) == 0:
                        results = -3
                        raise Exception('Empty intersection.')
                    if len(intersection1) > 1:  # same level and stage name eg sweet xp
                        if stagecategory == '':
                            results = -2
                            raise Exception('Could not discriminate.')
                        else:
                            stagecategories = [x[2].lower() for x in stage]
                            categorydss = list(map(lambda x: edit_distance_fast(x, stagecategory, errors), stagecategories))
                            if min(categorydss) > errors:
                                results = -1
                                raise Exception('Category could not match anything.')
                            nearestcategorymatch = [i for i, x in enumerate(categorydss) if x == min(categorydss)]
                            intersection2 = [value for value in intersection1 if value in nearestcategorymatch]
                            if len(intersection2) == 0:
                                results = -3
                                raise Exception('Empty secondary intersection.')
                            if len(intersection2) > 1:
                                results = -2
                                raise Exception('Could not discriminate.')
                            else:
                                results = stage[intersection2[0]][3]
                    else:
                        results = stage[intersection1[0]][3]
            else:  # we have exactly 1 best match
                if len(nearestmatch_custom) > 0:  # case 2
                    results = custom_stages.Custom_stages.custom_name_to_id(custom_stagenames_nodiff[nearestmatch_custom[0]])[0]
                else:  # case 1
                    results = stage[nearestmatch[0]][3]
        except Exception as e:
            print(e)
        finally:
            conn.close()
        return results

    def makeembed(self, stageinfo, stageenemies, stagetimed, stagereward, stagerestrictions, stageid):
        decsstring='Base hp = ' + str(stageinfo[0][4]) +', stage length = ' + str(stageinfo[0][7]) + ', max enemies = ' + str(stageinfo[0][8]) +'\n'
        for reward in stagereward:
            decsstring += str(reward[0])+'% of getting ' + str(reward[1]) + ' ' + reward[2] + ', '
        if len(stagereward) > 0:
            decsstring = decsstring[:-2] + '\n'
        for timed in stagetimed:
            decsstring += "Time score " + str(timed[0]) + " = " + str(timed[1]) + ' ' + str(timed[2]) + ', '
        if len(stagetimed) > 0:
            decsstring = decsstring[:-2] + '\n'
        decsstring += 'Difficulties ' + stageinfo[0][14]
        stageEmbed = emb(title=stageinfo[0][3] + '; ' + stageinfo[0][2] + '; ' + stageinfo[0][1] + '; '+str(stageid), description=decsstring,
                         color=0x009B77)
        stageEmbed.set_author(name='Cat Bot')
        enemystring = ''
        for enemyline in stageenemies:
            title = ''
            if enemyline[1] == 1:
                title = '__**'
            magstring = enemyline[3]
            if magstring.count(magstring[1:magstring.find(',')]) > 1:
                magstring = magstring[1:magstring.find(',')] + '%'
            else:
                magstring = magstring + '%'
            title += self._enemydata.namefromcode(enemyline[2]) + ', ' + magstring
            if enemyline[1] == 1:
                title += '**__'
            if enemyline[4] < 1:
                enemystring += '∞'
            else:
                enemystring += str(enemyline[4])
            enemystring += ' | ' + str(enemyline[6]) + 'f'
            if enemyline[4] != 1:
                enemystring += ' *(' + str(enemyline[7]) + 'f)*'
            enemystring += ' | ' + str(enemyline[5])
            stageEmbed.add_field(name=title, value=enemystring, inline=True)
            enemystring = ''
        try:
            elaborate = stagerestrictions[0][1]
            stageEmbed.set_footer(text=elaborate)
        except:
            stageEmbed.set_footer(text='No restrictions')
        return stageEmbed

    def nametoenemies(self, stringtosearch, errors):  # TODO refine failing to get data for whatever reason
        results = None
        try:
            conn = sqlite3.connect('stages.db')
            cursor = conn.cursor()
            query = '''select * from searchunitstages'''  # TODO this is going to change later
            stagenames = cursor.execute(query).fetchall()
            stagenames = [x[0].lower() for x in stagenames]
            dss = list(map(lambda x: edit_distance_fast(x, stringtosearch, errors), stagenames))
            if min(dss) > errors:
                results = -1
                raise Exception('String could not match anything.')
            nearestmatch = [i for i, x in enumerate(dss) if x == min(dss)]
            if len(nearestmatch) > 1:
                results = -2
                raise Exception('Could not discriminate.')
            else:
                nearestmatch = [(stagenames[nearestmatch[0]])]
                cursor.execute('SELECT * from enemylines, stage where stage.stage_id=enemylines.stage_appearance and '
                               'LOWER(name)=?', nearestmatch)
                results = cursor.fetchall()
        except:
            print('something went wrong')
        finally:
            conn.close()
            return results

    def whereistheenemy(self, enemycode, enemycode1=None, enemycode2=None):
        with sqlite3.connect('stages.db') as conn:
            cursor = conn.cursor()
            if enemycode1 is not None:
                if enemycode2 is not None:
                    tuple = (str(enemycode[0][0]), str(enemycode1[0][0]), str(enemycode2[0][0]))
                    results = cursor.execute(
                        '''SELECT DISTINCT stages.stage, stages.category, stages.level, stages.stageid from units join stages on units.stageid = stages.stageid where enemycode=? 
INTERSECT
SELECT DISTINCT stages.stage, stages.category, stages.level, stages.stageid from units join stages on units.stageid = stages.stageid where enemycode=? 
INTERSECT
SELECT DISTINCT stages.stage, stages.category, stages.level, stages.stageid from units join stages on units.stageid = stages.stageid where enemycode=? order by stages.category''',
                        tuple).fetchall()
                else:
                    tuple=(str(enemycode[0][0]), str(enemycode1[0][0]))
                    results = cursor.execute(
                        '''SELECT DISTINCT stages.stage, stages.category, stages.level, stages.stageid from units join stages on units.stageid = stages.stageid where enemycode=? 
INTERSECT
SELECT DISTINCT stages.stage, stages.category, stages.level, stages.stageid from units join stages on units.stageid = stages.stageid where enemycode=? order by stages.category''',
                        tuple).fetchall()
            else:
                results = cursor.execute(
                    'SELECT DISTINCT stages.stage, stages.category, stages.level, stages.stageid from units join stages on units.stageid = stages.stageid where enemycode=? order by stages.category',
                    [str(enemycode[0][0])]).fetchall()

            if len(results) == 0:
                return "No stages found."
            elif len(results) == 1:  # teleport to best result by using sbid function
                return results[0]
            answer = "Stages found: "  #todo make this nicer, text wise, in respect to the number of units
            category = ''
            post_processed_stages = []
            last_stage = [-1,-1,-1,-1]
            first_good_stage = -1
            consecutive_stages = 0
            # collapse barons into less stages
            for stage in results:
                if last_stage[3] == int(stage[3]) - 1:  # can compress this stage
                    if stage[3] // 100000==24 or stage[3] // 100000==27:  # barons and collab barons only
                        if first_good_stage == -1:
                            consecutive_stages+=1
                        else:
                            first_good_stage = stage
                    else:  # we shouldn't compress anymore
                        if consecutive_stages > 0:  # we might end up here in case of consecutive stages that really have nothing to do with the neighboor
                            first_good_stage = -1
                            post_processed_stages[-1][0] += ' __and the next '+str(consecutive_stages)+' stages__'
                            consecutive_stages = 0
                        post_processed_stages.append(list(stage))
                else:
                    if consecutive_stages > 0:  # stop compressing
                        first_good_stage = -1
                        post_processed_stages[-1][0] += ' __and the next ' + str(consecutive_stages) + ' stages__'
                        consecutive_stages = 0
                    post_processed_stages.append(list(stage))
                last_stage = stage
            if consecutive_stages > 0:  # stop compressing, might happen if last stage could have been compressed
                post_processed_stages[-1][0] += ' __and the next ' + str(consecutive_stages) + ' stages__'
            for stage in post_processed_stages:
                if stage[1] != category:
                    if answer.endswith(' - '):
                        answer = answer[0:-3]
                    answer += '\n**' + stage[1] + '**; '
                category = stage[1]
                answer += stage[0] + ' - '
                if len(answer) > 1950:
                    answer += '*and other stages*   '
                    break
            answer = answer[:-3]
            answer += '.'
            return answer

    def whereisthenemymonthly(self, enemycode, name, name2="", name3="", enemycode1="", enemycode2=""): # todo refactor to ignore name
        with sqlite3.connect('stages.db') as conn:
            cursor = conn.cursor()
            results = None
            if name2 != '':
                if name3 != '':
                    tuple = (str(enemycode[0][0]), str(enemycode1[0][0]), str(enemycode2[0][0]))
                    results = cursor.execute(
                        '''SELECT DISTINCT stages.stage, stages.category, stages.level, stages.energy from units join stages on units.stageid = stages.stageid where level not like '%Zombie%' and enemycode=? and category in ('SoL', 'Story Mode') 
INTERSECT
SELECT DISTINCT stages.stage, stages.category, stages.level, stages.energy from units join stages on units.stageid = stages.stageid where level not like '%Zombie%' and enemycode=? and category in ('SoL', 'Story Mode') 
INTERSECT
SELECT DISTINCT stages.stage, stages.category, stages.level, stages.energy from units join stages on units.stageid = stages.stageid where level not like '%Zombie%' and enemycode=? and category in ('SoL', 'Story Mode') order by stages.energy''',
                        tuple).fetchall()
                else:
                    tuple = (str(enemycode[0][0]), str(enemycode1[0][0]))
                    results = cursor.execute(
                        '''SELECT DISTINCT stages.stage, stages.category, stages.level, stages.energy from units join stages on units.stageid = stages.stageid where level not like '%Zombie%' and enemycode=? and category in ('SoL', 'Story Mode') 
INTERSECT
SELECT DISTINCT stages.stage, stages.category, stages.level, stages.energy from units join stages on units.stageid = stages.stageid where level not like '%Zombie%' and enemycode=? and category in ('SoL', 'Story Mode') order by stages.energy''',
                        tuple).fetchall()
            else:
                results = cursor.execute(
                    '''SELECT DISTINCT stages.stage, stages.category, stages.level, stages.energy from units join stages on units.stageid = stages.stageid where level not like '%Zombie%' and enemycode=? and category in ('SoL', 'Story Mode') order by stages.energy''',
                    [str(enemycode[0][0])]).fetchall()

            if len(results) == 0:
                return "No stages found."
            answer = "(Beta) Stages found (sorted by energy price): "  # todo make this nicer, text wise, in respect with the number of units
            category = ''
            for stage in results:
                if stage[1] != category:
                    if answer.endswith(' - '):
                        answer = answer[0:-3]
                    answer += '\n**' + stage[1] + '**; '
                category = stage[1]
                answer += stage[0] + ' - '
                if len(answer) > 1950:
                    answer += '*and other stages*   '
                    break
            answer = answer[:-3]
            answer += '.'
            return answer

    def listofstagesfromenemies(self, enemycode, name2="", name3="", enemycode1="", enemycode2=""):
        with sqlite3.connect('stages.db') as conn:
            cursor = conn.cursor()
            results = None
            if name2 != '':
                if name3 != '':
                    tuple = (str(enemycode[0][0]), str(enemycode1[0][0]), str(enemycode2[0][0]))
                    results = cursor.execute(
                        '''SELECT DISTINCT stages.stage, stages.category, stages.level from units join stages on units.stageid = stages.stageid where enemycode=? 
INTERSECT
SELECT DISTINCT stages.stage, stages.category, stages.level from units join stages on units.stageid = stages.stageid where enemycode=? 
INTERSECT
SELECT DISTINCT stages.stage, stages.category, stages.level from units join stages on units.stageid = stages.stageid where enemycode=? order by stages.category''',
                        tuple).fetchall()
                else:
                    tuple = (str(enemycode[0][0]), str(enemycode1[0][0]))
                    results = cursor.execute(
                        '''SELECT DISTINCT stages.stage, stages.category, stages.level from units join stages on units.stageid = stages.stageid where enemycode=? 
INTERSECT
SELECT DISTINCT stages.stage, stages.category, stages.level from units join stages on units.stageid = stages.stageid where enemycode=? order by stages.category''',
                        tuple).fetchall()
            else:
                results = cursor.execute(
                    'SELECT DISTINCT stages.stage, stages.category from units join stages on units.stageid = stages.stageid where enemycode=? order by stages.category',
                    [str(enemycode[0][0])]).fetchall()

            if len(results) == 0:
                return "No stages found."
            return results

    def showstagesinembed(self, stages, index=0, showcost=False):  # todo implement showcost
        embedtoret = emb(description='test', color=0xf43967)
        embedtoret.set_author(name='Cat Bot')
        embedtoret.set_footer(text='Beta feature; showing page ' + str(math.ceil((index+1)/25)) + ' out of ' + str(math.ceil(len(stages)/25)))
        for stage in stages[index:index+24]:
            embedtoret.add_field(name=stage[1] + ' - ' + stage[2], value=stage[3], inline=True)
        return embedtoret

    def enemytostages(self, unitcode, name):  # todo differ from all stages and meaningful stages
        with sqlite3.connect('stages.db') as conn:
            cursor = conn.cursor()
            results = cursor.execute(
                'SELECT DISTINCT stage.name from searchunitstages join stage on searchunitstages.name = stage.name '
                'join enemylines on enemylines.stage_appearance=stage.stage_id where unitcode=? order by '
                'enemylines.id;',
                [str(unitcode)]).fetchall()
            if len(results) == 0:
                return name + " wasn't found in current stages."
            answer = name + ' is found in the following stages: '
            for stage in results:
                answer += stage[0] + ' - '
            answer = answer[:-2]
            if len(answer) > 2000:
                return 'too long'  # todo make this work for any length
            return answer

    def does_name_exist(self, name):
        with sqlite3.connect('stages.db') as conn:
            cursor = conn.cursor()
            results = cursor.execute('select count(*) from stages where name = ?', (name,)).fetchone()
            return results

    def idtoenemies(self, id_f):
        with sqlite3.connect('stages.db') as conn:
            cursor = conn.cursor()
            results = cursor.execute('select units.* from units JOIN stages on units.stageid=stages.stageid where '
                                     'units.stageid = ?', [id_f]).fetchall()
            return results

    def idtostage(self, id_f):
        with sqlite3.connect('stages.db') as conn:
            cursor = conn.cursor()
            results = cursor.execute('select * from stages where stageid = ?', [id_f]).fetchall()
            return results

    def idtotimed(self, id_f):
        with sqlite3.connect('stages.db') as conn:
            cursor = conn.cursor()
            results = cursor.execute(
                "select time, 'reward-translation'.item, amount from timed JOIN stages on "
                "timed.stage_id=stages.stageid join 'reward-translation' on timed.item='reward-translation'.code "
                "where stages.stageid = ?",
                [id_f]).fetchall()
            return results

    def idtoreward(self, id_f):
        with sqlite3.connect('stages.db') as conn:
            cursor = conn.cursor()
            results = cursor.execute(
                "SELECT chance, amount, 'reward-translation'.item from rewards join 'reward-translation' where code = rewards.item and stage_id=?;",
                [id_f]).fetchall()
            return results

    def idtorestrictions(self, id_f):
        with sqlite3.connect('stages.db') as conn:
            cursor = conn.cursor()
            results = cursor.execute(
                'select "restrict".* from "restrict" JOIN stages on "restrict".stageid=stages.stageid where stages.stageid = ?',
                [id_f]).fetchall()
            return results




# select units.* from units JOIN stages on units.stageid=stages.stageid where stages.stage = "No Return Flights";

# select rewards.* from rewards JOIN stages on rewards.stage_id=stages.stageid where stages.stage = "No Return Flights";

# select "restrict".* from "restrict" JOIN stages on "restrict".stageid=stages.stageid where stages.stage = "Aguham";

# select timed.* from timed JOIN stages on timed.stage_id=stages.stageid where stages.stage = "Mallow March";

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
