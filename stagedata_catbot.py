from discord import Embed as emb
import sqlite3
import nltk as nl


class Stagedata:
    def __init__(self, enemydata):
        self._stagedata = ''
        self._enemydata = enemydata

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
            conn = sqlite3.connect('stagedatanew.db')
            cursor = conn.cursor()
            query = '''select stages.stage, stages.level, stages.category, stages.stageid from stages;'''
            stage = cursor.execute(query).fetchall()
            stagenames = [x[0].lower() for x in stage]
            dss = list(map(lambda x: nl.edit_distance(x, stagename), stagenames))
            if min(dss) > errors:
                results = -1
                raise Exception('String could not match anything.')
            nearestmatch = [i for i, x in enumerate(dss) if x == min(dss)]
            if len(nearestmatch) > 1:
                if stagelevel == '':
                    results = -2
                    raise Exception('Could not discriminate.')
                else:
                    stagelevels = [x[1].lower() for x in stage]
                    leveldss = list(map(lambda x: nl.edit_distance(x, stagelevel), stagelevels))
                    if min(leveldss) > errors:
                        results = -1
                        raise Exception('Level could not match anything.')
                    nearestlevelmatch = [i for i, x in enumerate(leveldss) if x == min(leveldss)]
                    intersection1 = [value for value in nearestlevelmatch if value in nearestmatch]
                    if len(intersection1) > 1:  # same level and stage name eg sweet xp
                        if stagecategory == '':
                            results = -2
                            raise Exception('Could not discriminate.')
                        else:
                            stagecategories = [x[2].lower() for x in stage]
                            categorydss = list(map(lambda x: nl.edit_distance(x, stagecategory), stagecategories))
                            if min(categorydss) > errors:
                                results = -1
                                raise Exception('Category could not match anything.')
                            nearestcategorymatch = [i for i, x in enumerate(categorydss) if x == min(categorydss)]
                            intersection2 = [value for value in intersection1 if value in nearestcategorymatch]
                            if len(intersection2) > 1:
                                results = -2
                                raise Exception('Could not discriminate.')
                            else:
                                results = stage[intersection2[0]][3]
                    else:
                        results = stage[intersection1[0]][3]
            else:
                results = stage[nearestmatch[0]][3]
        except:
            print('something went wrong')
        finally:
            conn.close()
            return results
        return

    def makeembed(self, stageinfo, stageenemies, stagetimed, stagereward, stagerestrictions):
        decsstring='Base hp = ' + str(stageinfo[0][4]) +', stage length = ' + str(stageinfo[0][7]) + ', max enemies = ' + str(stageinfo[0][8]) +'\n'
        for reward in stagereward:
            decsstring += str(reward[0])+'% of getting ' + str(reward[1]) + ' ' + reward[2] + ', '
        if len(stagereward) > 0:
            decsstring = decsstring[:-2]
        stageEmbed = emb(title=stageinfo[0][3] + ', ' + stageinfo[0][2] + ', ' + stageinfo[0][1], description=decsstring,
                         color=0x009B77)
        stageEmbed.set_author(name='Cat Bot')
        enemystring = ''
        stageenemies = stageenemies[::-1]  # reverses enemies as order matters
        for enemyline in stageenemies:
            title = ''
            if enemyline[9] == 1:
                title = '**'
            title += self._enemydata.namefromcode(enemyline[1]) + ', ' + str(round(enemyline[10])) + '%'
            if enemyline[9] == 1:
                title += '**'
            if enemyline[2] < 1:
                enemystring += '∞'
            else:
                enemystring += str(enemyline[2])
            enemystring += ' | ' + str(enemyline[3]) + 'f'
            if enemyline[2] != 1:
                if enemyline[4] == enemyline[5]:
                    enemystring += ' *(' + str(enemyline[4]) + 'f)*'
                else:
                    enemystring += ' *(' + str(enemyline[4]) + '~' + str(enemyline[5]) + 'f)*'
            enemystring += ' | ' + str(enemyline[6]) + '%'
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
            dss = list(map(lambda x: nl.edit_distance(x, stringtosearch), stagenames))
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

    def whereistheenemy(self, enemycode, name):
        with sqlite3.connect('stagedatanew.db') as conn:
            cursor = conn.cursor()
            results = cursor.execute(
                'SELECT DISTINCT stages.stage from units join stages on units.stageid = stages.stageid where unitcode=?',
                [str(enemycode)]).fetchall()
            if len(results) == 0:
                return name + " wasn't found in current stages."
            answer = name + ' is found in the following stages: '
            for stage in results:
                answer += stage[0] + ' - '
                if len(answer) > 1950:
                    answer += '*and other stages*   '
                    break
            answer = answer[:-3]
            answer += '.'
            return answer

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

    def idtoenemies(self, id):
        with sqlite3.connect('stagedatanew.db') as conn:
            cursor = conn.cursor()
            results = cursor.execute('select units.* from units JOIN stages on units.stageid=stages.stageid where '
                                     'units.stageid = ?', [id]).fetchall()
            return results

    def idtostage(self, id):
        with sqlite3.connect('stagedatanew.db') as conn:
            cursor = conn.cursor()
            results = cursor.execute('select * from stages where stageid = ?', [id]).fetchall()
            return results

    def idtotimed(self, id):
        with sqlite3.connect('stagedatanew.db') as conn:
            cursor = conn.cursor()
            results = cursor.execute(
                'select timed.* from timed JOIN stages on timed.stage_id=stages.stageid where stages.stageid = ?',
                [id]).fetchall()
            return results

    def idtoreward(self, id):
        with sqlite3.connect('stagedatanew.db') as conn:
            cursor = conn.cursor()
            results = cursor.execute(
                "SELECT chance, amount, 'reward-translation'.item from rewards join 'reward-translation' where code = rewards.item and stage_id=?;",
                [id]).fetchall()
            return results

    def idtorestrictions(self, id):
        with sqlite3.connect('stagedatanew.db') as conn:
            cursor = conn.cursor()
            results = cursor.execute(
                'select "restrict".* from "restrict" JOIN stages on "restrict".stageid=stages.stageid where stages.stageid = ?',
                [id]).fetchall()
            return results




# select units.* from units JOIN stages on units.stageid=stages.stageid where stages.stage = "No Return Flights";

# select rewards.* from rewards JOIN stages on rewards.stage_id=stages.stageid where stages.stage = "No Return Flights";

# select "restrict".* from "restrict" JOIN stages on "restrict".stageid=stages.stageid where stages.stage = "Aguham";

# select timed.* from timed JOIN stages on timed.stage_id=stages.stageid where stages.stage = "Mallow March";

