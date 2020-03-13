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
                results = 0
                raise Exception('String could not match anything.')
            nearestmatch = [i for i, x in enumerate(dss) if x == min(dss)]
            if len(nearestmatch) > 1:
                results = 1
                raise Exception('Could not discriminate.')
            else:
                nearestmatch = [(stagenames[nearestmatch[0]])]
                cursor.execute('SELECT * from enemylines, stage where stage.stage_id=enemylines.stage_appearance and LOWER(name)=?', nearestmatch)
                results = cursor.fetchall()
        except:
            print('something went wrong')
        finally:
            conn.close()
            return results

    def enemytostages(self, unitcode, name):  # todo differ from all stages and meaningful stages
        with sqlite3.connect('stages.db') as conn:
            cursor = conn.cursor()
            results = cursor.execute(
                'SELECT DISTINCT searchunitstages.name from searchunitstages join stage on searchunitstages.name = '
                'stage.name join enemylines on enemylines.stage_appearance=stage.stage_id where unitcode=?;',
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





