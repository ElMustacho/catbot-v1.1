from discord import Embed as emb
import sqlite3
import nltk as nl


class Stagedata:
    def __init__(self, enemydata):
        self._stagedata = ''
        self._enemydata = enemydata

    def dataToEmbed(self, enemylines, stagedata, magnification):  # TODO refine the enemylines
        stageEmbed = emb(description='Unit | Amount | Magnification | First Spawn Frame *(Respawn F)* | Base Health',
                         color=0x98ff33)
        stageEmbed.set_author(name='Cat Bot')
        stageEmbed.add_field(name='Stage data', value=enemylines[0][14])
        enemystring = ''
        unitnumber = 1
        for enemyline in enemylines:
            if enemyline[10] == 1:
                enemystring = '**'
            enemystring += self._enemydata.namefromcode(enemyline[2]) + ' | '
            if enemyline[3] < 1:
                enemystring += '∞'
            else:
                enemystring += str(enemyline[3])
            enemystring += ' | ' + str(enemyline[4] * magnification) + '% | ' + str(enemyline[11] * 2) + 'f'
            if enemyline[3] != 1:
                if enemyline[5] == enemyline[6]:
                    enemystring += ' *(' + str(enemyline[5] * 2) + 'f)*'
                else:
                    enemystring += ' *(' + str(enemyline[5] * 2) + '-' + str(enemyline[6] * 2) + 'f)*'
            enemystring += ' | ' + str(enemyline[7]) + '%'
            if enemyline[10] == 1:
                enemystring += '**'
            stageEmbed.add_field(name='Unit ' + str(unitnumber), value=enemystring, inline=False)
            enemystring = ''
            unitnumber += 1
        return stageEmbed

    def nametoenemies(self, stringtosearch, errors):  # TODO refine failing to get data for whatever reason
        results = None
        try:
            conn = sqlite3.connect('stages.db')
            cursor = conn.cursor()
            query = '''select * from searchunitstages'''
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
                nearestmatch = [(stagenames[0])]
                cursor.execute('SELECT * from enemylines, stage where stage.stage_id=enemylines.stage_appearance and LOWER(name)=?', nearestmatch)
                results = cursor.fetchall()
        except:
            print('something went wrong')
        finally:
            conn.close()
            return results
