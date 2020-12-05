# todo list
# give out the previous two nicely
# write/declare/init stuff only once
# don't upload to git unwanted files
# get fixed values from a file, like the token
# make embed function, for each kind of embed
# tell the user what happens when a report belonging to him is solved or initiated
import asyncio
import sqlite3
import discord
from datetime import datetime, timedelta
from data_catbot import Data_catbot
from modtools import Modtools
import catunits_catbot
import enemyunits_catbot
import stagedata_catbot
import catcomboes

intents = discord.Intents.all()

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print('Ready to go')


@client.event
async def on_message(message):
    if len(str(message.content)) > 300:  # don't bother with stuff too long
        return

    if '\t' in message.content:  # catbot doesn't like tab
        return

    if message.author == client.user:  # bot doesn't want to answer itself
        return

    elif message.content.startswith('!sayhi'):
        level = privilegelevel(message.author)
        if not canSend(1, level, message):
            return
        if isADM(message):
            await message.channel.send('Greetings, user.')
            return
        if level == 5:
            await message.channel.send('Hi dad!')
        elif level == 4:
            await message.channel.send("Hi moderator, how you doin'?")
        elif level == 3:
            await message.channel.send("Wow, you are important, that's cool!")
        elif level == 2:
            await message.channel.send('Well, at least you are here.')
        else:
            await message.channel.send('You can do better than this.')

    elif message.content.startswith('!mytier'):
        if not canSend(1, privilegelevel(message.author), message):
            if not isokayifnotclog(message, isADM(message)):
                return
        await message.channel.send('Your tier is: ' + str(privilegelevel(message.author)))

    elif message.content.startswith('!catstats ') or message.content.startswith('!cs '):
        if not canSend(1, privilegelevel(message.author), message):
            return
        if privilegelevel(message.author) < 3 and message.channel.id not in catbotdata.requireddata[
            'freeforall-channels']:
            if not isokayifnotclog(message, isADM(message)):
                return
        limit = message.content.find(';')
        if limit == -1:
            limit = len(message.content)
        cat = message.content[message.content.find(' ') + 1:limit].lower()
        if cat == '!cs':
            await message.channel.send('You need to input a cat unit name or code.')
            return
        catstats = catculator.getUnitCode(cat, 6)  # second parameter is number of errors allowed
        if catstats == "no result":  # too many errors, maybe they meant an enemy?
            enemystats = enemyculator.getUnitCode(message.content[message.content.find(' ') + 1:limit].lower(), 3)
            if enemystats is None:  # too many errors for an enemy
                await message.channel.send(
                    message.content[message.content.find(' ') + 1:limit] + '; wasn\'t recognized.')
                return
            try:
                lenght = len(enemystats[0])
            except TypeError:
                enemystats[0] = [enemystats[0]]
            if len(enemystats[0]) > 1:  # name wasn't unique
                await message.channel.send(
                    message.content[message.content.find(' ') + 1:limit] + '; wasn\'t recognized.')
                return
            enemy = enemyculator.getrow(enemystats[0][0])
            if enemy is None:
                await message.channel.send(
                    message.content[message.content.find(' ') + 1:limit] + '; wasn\'t recognized.')
                return
            embedsend = enemyculator.getstatsembed(enemy, 1)
            await message.channel.send("Did you mean to search an enemy?", embed=embedsend)
            return
        if catstats == "name not unique":  # name wasn't unique
            await message.channel.send('Couldn\'t discriminate.')
            return
        cat = catculator.getrow(catstats[0])
        if cat is None:
            await message.channel.send('Invalid code for cat unit.')
            return
        try:
            level = int(message.content[message.content.find(';') + 1:])
        except:
            level = 30
        if level < 0 or level > 130:
            level = 30
        try:
            embedsend = catculator.getstatsEmbed(cat, level, catstats[0])
        except TypeError:
            await message.channel.send("That code doesn't provide any result.")
            return
        sent_message = await message.channel.send(embed=embedsend)
        if isADM(message):
            return
        await sent_message.add_reaction('▶')
        await sent_message.add_reaction('◀️')
        await sent_message.add_reaction('⏩')
        await sent_message.add_reaction('⏪')
        await sent_message.add_reaction('\U00002705')
        await sent_message.add_reaction('\U0001F5D1')

        def check(reaction_received, user_that_sent):
            return user_that_sent == message.author and str(reaction_received.emoji) in ['▶', '◀️', '⏩', '⏪',
                                                                                         '\U00002705',
                                                                                         '\U0001F5D1'] and reaction_received.message.id == sent_message.id

        try:
            reaction, user = await client.wait_for('reaction_add', timeout=15.0, check=check)
        except asyncio.TimeoutError:
            pass
        else:
            offset = 0
            txtreaction = str(reaction)
            if txtreaction == '▶':
                offset += 1
            elif txtreaction == '⏩':
                offset += 2
            elif txtreaction == '⏪':
                offset -= 2
            elif txtreaction == '◀️':
                offset -= 1
            elif txtreaction == '\U0001F5D1':
                await message.delete()
                await sent_message.delete()
                return
            else:
                await sent_message.clear_reactions()
                return
            try:
                await sent_message.edit(
                    embed=catculator.getstatsEmbed(catculator.getrow(catstats[0] + offset), level,
                                                   catstats[0] + offset))
            except TypeError:
                await sent_message.edit(content="That form doesn't exists.")
        await sent_message.clear_reactions()
        return

    elif message.content.startswith('!enemystats') or message.content.startswith('!es'):
        if not canSend(1, privilegelevel(message.author), message):
            return
        if privilegelevel(message.author) < 3 and message.channel.id not in catbotdata.requireddata[
            'freeforall-channels']:
            if not isokayifnotclog(message, isADM(message)):
                return
        limit = message.content.find(';')
        if limit == -1:
            limit = len(message.content)
        enemy = message.content[message.content.find(' ') + 1:limit].lower()
        if enemy == '!es':
            await message.channel.send('You need to provide an enemy unit name.')
            return
        enemystats = enemyculator.getUnitCode(enemy, 6)  # second parameter is number of errors allowed
        if enemystats is None:  # too many errors, maybe they meant a cat
            limit = message.content.find(';')
            if limit == -1:
                limit = len(message.content)
            catstats = catculator.getUnitCode(message.content[message.content.find(' ') + 1:limit].lower(), 3)
            enemy = message.content[message.content.find(' ') + 1:limit]
            if enemy == '':
                await message.channel.send('You need to input an enemy name.')
            if catstats == "no result":
                await message.channel.send(enemy + '; wasn\'t recognized.')
            if catstats == "name not unique":  # name wasn't unique
                await message.channel.send(
                    message.content[message.content.find(' ') + 1:limit] + '; wasn\'t recognized.')
                return
            cat = catculator.getrow(catstats[0])
            if cat is None:
                await message.channel.send(
                    message.content[message.content.find(' ') + 1:limit] + '; wasn\'t recognized.')
                return
            embedsend = catculator.getstatsEmbed(cat, 30, catstats[0])
            await message.channel.send("Did you mean to search a cat?", embed=embedsend)
            return
        try:
            lenght = len(enemystats[0])
        except TypeError:
            enemystats[0] = [enemystats[0]]
        if len(enemystats[0]) > 1:  # name wasn't unique
            await message.channel.send('Couldn\'t discriminate.')
            return
        enemy = enemyculator.getrow(enemystats[0][0])
        if enemy is None:
            await message.channel.send('Invalid code for enemy unit.')
            return
        try:
            border = message.content.find('%')
            if border == -1:
                border = find_nth(str(message.content), ';', 2)
                if border == -1:
                    border = len(message.content)
            magnification = float(int(message.content[message.content.find(';') + 1:border]) / 100)
            mag2 = magnification
            if message.content.count(';') == 2:
                mag2 = float(int(message.content[find_nth(str(message.content), ';', 2) + 1:]) / 100)
            elif message.content.count(';') > 2:
                await message.channel.send("Wrong syntax, you passed too many arguments.")
                return
        except:
            magnification = 1
            mag2 = magnification
        if magnification < 0 or magnification > 1000000:
            magnification = 1
        if mag2 < 0 or mag2 > 1000000:
            mag2 = 1
        embedsend = enemyculator.getstatsembed(enemy, magnification, mag2)
        await message.channel.send(embed=embedsend)

    elif message.content.startswith('!renamecat'):
        if not canSend(4, privilegelevel(message.author), message):
            return
        limit = message.content.find(';')
        if limit < 0:
            await message.channel.send('Incorrect format, check command format.')
            return
        realnameunit = message.content[11: limit]
        catcode = catculator.getUnitCode(realnameunit.lower(), 0)
        if catcode == "no result":  # too many errors
            await message.channel.send('That was gibberish.')
            return
        if catcode == "name not unique":  # name wasn't unique
            await message.channel.send('Couldn\'t discriminate.')
            return
        response = catculator.givenewname(catcode[0], message.content[limit + 2:])
        if response:
            await message.channel.send('The name ' + message.content[limit + 2:] + ' is now assigned.')
        else:
            await message.channel.send('Name was already used.')

    elif message.content.startswith('!renameenemy'):
        if not canSend(4, privilegelevel(message.author), message):
            return
        limit = message.content.find(';')
        if limit < 0:
            await message.channel.send('Incorrect format, check command format.')
            return
        realnameunit = message.content[13: limit]
        enemycode = enemyculator.getUnitCode(realnameunit.lower(), 0)
        if enemycode is None:  # too many errors
            await message.channel.send('That was gibberish.')
            return
        if len(enemycode[0]) > 1:  # name wasn't unique
            await message.channel.send('Couldn\'t discriminate.')
            return

        if enemycode[0][0] is None:
            await message.channel.send('Invalid code for cat unit')
            return
        response = enemyculator.givenewname(enemycode[0][0], message.content[limit + 2:])
        if response:
            await message.channel.send('The name ' + message.content[limit + 2:] + ' is now assigned.')
        else:
            await message.channel.send('Name was already used.')

    elif message.content.startswith('!silence'):
        if not canSend(3, privilegelevel(message.author), message):
            return
        timestop = min(60, int(message.content[9:]))
        catbotdata.timelastmessage = datetime.now() + timedelta(minutes=timestop)
        await message.channel.send("I'll be silent for a while")

    elif message.content.startswith('!letfree'):
        if not canSend(3, privilegelevel(message.author), message):
            return
        catbotdata.timelastmessage = datetime.now()
        await message.channel.send("I can speak again")

    elif message.content.startswith('!catnamesof'):
        if not canSend(2, privilegelevel(message.author), message):
            if not isokayifnotclog(message, isADM(message)):
                return
        catstats = catculator.getUnitCode(message.content[12:].lower(),
                                          6)  # second parameter is number of errors allowed
        if catstats == "no result":  # too many errors
            await message.channel.send(message.content[12:] + '; wasn\'t recognized')
            return
        if len(catstats[0]) > 1:  # name wasn't unique
            await message.channel.send('Couldn\'t discriminate.')
            return
        cat = catculator.getrow(catstats[0])
        await message.channel.send(catculator.getnames(cat, catstats[0]))

    elif message.content.startswith('!enemynamesof'):
        if not canSend(2, privilegelevel(message.author), message):
            if not isokayifnotclog(message, isADM(message)):
                return
        enemystats = enemyculator.getUnitCode(message.content[14:].lower(),
                                              6)  # second parameter is number of errors allowed
        if enemystats[0] is None:  # too many errors
            await message.channel.send(message.content[15:] + '; wasn\'t recognized')
            return
        if len(enemystats[0]) > 1:  # name wasn't unique
            await message.channel.send('Couldn\'t discriminate.')
            return
        enemy = enemyculator.getrow(enemystats[0][0])
        await message.channel.send(enemyculator.getnames(enemy, enemystats[0][0]))

    elif message.content.startswith('!deletecatname'):
        if not canSend(4, privilegelevel(message.author), message):
            return
        limit = message.content.find(';')
        if limit < 0:
            await message.channel.send('Incorrect format, check command format')
            return
        realnameunit = message.content[15: limit]
        catcode = catculator.getUnitCode(realnameunit.lower(), 0)
        if catcode == "no result":  # too many errors
            await message.channel.send('That was gibberish.')
            return
        if catcode == "name not unique":  # name wasn't unique
            await message.channel.send('Couldn\'t discriminate.')
            return
        operationsuccess = catculator.removename(catcode[0], message.content[limit + 2:])
        if operationsuccess:
            await message.channel.send('Name was deleted successfully.')
        else:
            await message.channel.send('No such name to delete')

    elif message.content.startswith('!deleteenemyname'):
        if not canSend(4, privilegelevel(message.author), message):
            return
        limit = message.content.find(';')
        if limit < 0:
            await message.channel.send('Incorrect format, check command format')
            return
        realnameunit = message.content[17: limit]
        enemycode = enemyculator.getUnitCode(realnameunit.lower(), 0)
        if enemycode is None:  # too many errors
            await message.channel.send('That was gibberish.')
            return
        if len(enemycode[0]) > 1:  # name wasn't unique
            await message.channel.send('Couldn\'t discriminate.')
            return
        if enemycode[0][0] is None:
            await message.channel.send('Invalid code for cat unit')
            return
        operationsuccess = enemyculator.removename(enemycode[0][0], message.content[limit + 2:])
        if operationsuccess:
            await message.channel.send('Name was deleted successfully.')
        else:
            await message.channel.send('No such name to delete')

    elif message.content.startswith('!stagebeta') or message.content.startswith('!sb'):
        if not canSend(1, privilegelevel(message.author), message):
            return
        if privilegelevel(message.author) < 3 and message.channel.id not in catbotdata.requireddata[
            'freeforall-channels']:
            if not isokayifnotclog(message, isADM(message)):
                return
        limit = message.content.find(';')
        if limit == -1:
            limit = len(message.content)
        s_string = str(message.content)
        if s_string[len(s_string) - 1] != ';':
            s_string += ';'
        stagestring = s_string[s_string.find(' ') + 1:limit]
        stagelevel = s_string[s_string.find(';') + 2:find_nth(s_string, ';', 2)]
        categorystring = s_string[find_nth(s_string, ';', 2) + 2:-1]
        if s_string.count(';') < 2:
            categorystring = ''
        if s_string.count(';') < 1:
            stagelevel = ''
        if s_string.count(';') > 3:
            await message.channel.send("Wrong syntax, check again command usage guide.")
            return
        stageid = stagedata.getstageid(stagestring.lower(), 5, stagelevel.lower(), categorystring.lower())
        if stageid == -1:  # too many errors
            await message.channel.send("That stage doesn't exist.")
            return
        elif stageid == -2:  # could not tell between more than 1 stage
            await message.channel.send("You need to be more specific.")
            return
        elif stageid == -3:  # empty intersection
            await message.channel.send("The combination of the stage, map and category produces no result.")
            return
        elif stageid is None:
            await message.channel.send("Catbot is confused and doesn't know what happened.")
            return
        stageinfo = stagedata.idtostage(stageid)
        stageenemies = stagedata.idtoenemies(stageid)
        stagetimed = stagedata.idtotimed(stageid)
        stagereward = stagedata.idtoreward(stageid)
        stagerestrictions = stagedata.idtorestrictions(stageid)
        embedtosend = stagedata.makeembed(stageinfo, stageenemies, stagetimed, stagereward, stagerestrictions)
        await message.channel.send(embed=embedtosend)

    elif message.content.startswith('!enemysearch'):  # todo look at enemyculator todos
        if not canSend(3, privilegelevel(message.author), message):
            return
        enemystats = enemyculator.getUnitCode(message.content[message.content.find(' ') + 1:].lower(), 6)  # 2nd is errs

        if enemystats[0] is None:  # too many errors
            await message.channel.send(message.content[15:] + '; wasn\'t recognized')
            return
        if len(enemystats[0]) > 1:  # name wasn't unique
            await message.channel.send('Couldn\'t discriminate.')
            return
        nameunit = enemyculator.namefromcode(enemystats[0][0])
        await message.channel.send(stagedata.enemytostages(enemystats[0][0], nameunit))

    elif message.content.startswith('!whereis'):
        if not canSend(1, privilegelevel(message.author), message):
            return
        if privilegelevel(message.author) < 3 and message.channel.id not in catbotdata.requireddata[
                'freeforall-channels']:
            if not isokayifnotclog(message, isADM(message)):
                return
        limit = message.content.find(';')
        if limit == -1:
            limit = len(message.content)
        unit1 = message.content[message.content.find(' ') + 1:limit]
        unit2 = message.content[
                message.content.find(';') + 1:message.content.find(';', message.content.find(';') + 1)]
        unit3 = message.content[message.content.rfind(';') + 2:]
        if message.content.count(';') < 2:
            unit2 = ''
        if message.content.count(';') < 1:
            unit3 = ''
        if message.content.count(';') > 2:
            await message.channel.send("Wrong syntax, check again command usage guide.")
            return
        if unit2 == "" and unit3 != "":
            unit2 = unit3
            unit3 = ""
        enemystats1 = enemyculator.getUnitCode(unit1, 4)
        enemystats2 = None
        enemystats3 = None
        if enemystats1 is None:  # too many errors
            await message.channel.send("The first unit does not exist.")
            return
        try:  # was this a string or a int?
            if len(enemystats1[0]) > 1:  # name wasn't unique
                await message.channel.send('Couldn\'t discriminate.')
                return
        except TypeError:
            await message.channel.send('I need a name, not a number.')
            return
        nameunit1 = enemyculator.namefromcode(enemystats1[0][0])
        nameunit2 = ''
        nameunit3 = ''
        if unit2 != '':
            enemystats2 = enemyculator.getUnitCode(unit2.lower(), 4)
            if enemystats2 is None:  # too many errors
                await message.channel.send("The second unit does not exist.")
                return
            try:  # was this a string or a int?
                if len(enemystats2[0]) > 1:  # name wasn't unique
                    await message.channel.send('Couldn\'t discriminate.')
                    return
            except TypeError:
                await message.channel.send('I need a name, not a number.')
                return
            nameunit2 = enemyculator.namefromcode(enemystats2[0][0])
            if unit3 != '':
                enemystats3 = enemyculator.getUnitCode(unit3.lower(), 4)
                if enemystats3 is None:  # too many errors
                    await message.channel.send("The third unit does not exist.")
                    return
                try:  # was this a string or a int?
                    if len(enemystats3[0]) > 1:  # name wasn't unique
                        await message.channel.send('Couldn\'t discriminate.')
                        return
                except TypeError:
                    await message.channel.send('I need a name, not a number.')
                    return
                nameunit3 = enemyculator.namefromcode(enemystats3[0][0])
        await message.channel.send(
            stagedata.whereistheenemy(enemystats1, nameunit1, nameunit2, nameunit3, enemystats2, enemystats3))

    elif message.content.startswith('!comboname'):
        if not canSend(3, privilegelevel(message.author), message):
            return
        await message.channel.send(
            catcomboes.Comboes.name_to_combo(message.content[message.content.find(' ') + 1:], catculator))

    elif message.content.startswith('!combowith'):
        if not canSend(3, privilegelevel(message.author), message):
            return
        await message.channel.send(
            catcomboes.Comboes.search_by_unit(message.content[message.content.find(' ') + 1:], catculator))

    elif message.content.startswith('!say'):
        if not canSend(5, privilegelevel(message.author), message):
            return
        looking = message.content[message.content.find(' ') + 1: find_nth(message.content, ' ', 2)]
        channel_to_send = client.get_channel(int(looking))
        message_to_send = message.content[find_nth(message.content, ' ', 2):]
        await channel_to_send.send(message_to_send)
        return

    elif message.content.startswith('!rawtalents'):
        if not canSend(3, privilegelevel(message.author), message):
            return
        cat = catculator.getUnitCode(message.content[message.content.find(' ') + 1:].lower(), 6)

        if cat == "no result":
            await message.channel.send("Gibberish.")
            return
        if cat == "name not unique":  # name wasn't unique
            await message.channel.send('Couldn\'t discriminate.')
            return
        ironwallsucks = 0
        if cat[0] > 1017:
            ironwallsucks = 2
        answer = catculator.get_talents_by_id(cat[0] - 2 + ironwallsucks)  # offset by 2 to fix unitcodes
        await message.channel.send(str(answer))
        return

    elif message.content.startswith('!cst'):  # experimental talents assignment
        if not canSend(3, privilegelevel(message.author), message):
            return
        limit = message.content.find(';')
        if limit == -1:
            limit = len(message.content)
        cat = catculator.getUnitCode(message.content[message.content.find(' ') + 1:limit].lower(), 6)
        if cat == "no result":
            await message.channel.send("Gibberish.")
            return
        if cat == "name not unique":  # name wasn't unique
            await message.channel.send('Couldn\'t discriminate.')
            return
        ironwallsucks = 0
        if cat[0] > 1017:
            ironwallsucks = 2
        unit_talents = catculator.get_talents_by_id(cat[0] - 2 + ironwallsucks)  # offset by 2 required
        cat_row = catculator.getrow(cat[0])
        if cat_row is None or unit_talents[:3] == 'nan':
            await message.channel.send("Invalid unitcode.")
            return
        cat_unit = cat_row.tolist()
        if unit_talents[-2:] == 'd.':  # no db found
            await message.channel.send(unit_talents)
            return
        if unit_talents[-2:] == 's.':  # no talents for unit
            await message.channel.send(unit_talents)
            return
        ep = [0, 0, 0, 0, 0, 0, 0, 0]
        unit_talents = [list(ele) for ele in unit_talents]
        for line in unit_talents:
            ret = catculator.apply_talent(cat_unit, line, 10, ep)
            ep = ret[1]
            cat_unit = ret[0]
        try:
            level = int(message.content[message.content.find(';') + 1:])
        except:
            level = 30
        if level < 0 or level > 130:
            level = 30
        emb = catculator.getstatsEmbed(cat_unit, level, int(cat[0]), ep)
        await message.channel.send(embed=emb)
        return

    elif message.content.startswith('!'):  # custom commands
        if not canSend(3, privilegelevel(message.author), message):
            return
        try:
            conn = sqlite3.connect('file:custom_commands.db?mode=rw', uri=True)  # open only if exists
            cursor = conn.cursor()
            search = (message.content,)
            results = cursor.execute("SELECT answer FROM commands WHERE command = ?", search).fetchone()
            if results is None:
                return
            else:
                await message.channel.send(results[0])
                await message.delete()
        except sqlite3.OperationalError:  # database not found
            print("Database for custom commands not found.")
            return

    elif not catbotdata.requireddata['moderation']:
        return

    elif message.content == '!token':
        if canSend(2, privilegelevel(message.author), message):
            if isInServer(message.author) and isADM(message):
                await message.channel.send('Your token is: ' + str(int(message.author.id) % 9999998) + '.')
        return

    elif message.content == '$password manic lion cat':
        if message.channel.id == catbotdata.requireddata['welcome-channel']:
            member = serveruser(message.author)
            await member.add_roles(discord.utils.get(client.get_guild(catbotdata.requireddata['server-id']).roles,
                                                     id=catbotdata.requireddata['tier-2-roles'][0]),
                                   reason='Entering server')
            await message.delete()
            await client.get_channel(catbotdata.requireddata['log-channel-id']).send(
                message.author.mention + ' has used the password.')

    elif message.content.startswith('!solve'):
        if not canSend(4, privilegelevel(message.author), message):
            return
        channel_mod = client.get_channel(catbotdata.requireddata['mod-channel-id'])
        if modqueue.setsolvedbyindex(int(message.content[7:])):  # if true it was solved successfully
            await channel_mod.send('Report has been set as solved')
        else:
            await channel_mod.send('Invalid report code')

    elif message.content.startswith('!assignto'):
        if not canSend(4, privilegelevel(message.author), message):
            return
        if message.content.startswith('!assigntome'):
            modqueue.setassigned(int(message.content[11:]), message.author.mention)
        else:
            modqueue.setassigned(int(message.content[9:message.content.find(
                ',')]), message.content[message.content.find(',') + 2:])
        channel_mod = client.get_channel(catbotdata.requireddata['mod-channel-id'])
        await channel_mod.send('Assignment done')

    elif message.content.startswith('!helpme'):  # todo beautify this
        if not canSend(1, privilegelevel(message.author), message):
            return
        channel_mod = client.get_channel(catbotdata.requireddata['mod-channel-id'])
        reportcode = modqueue.addentry(str(message.author.mention), str(datetime.now()),
                                       str(message.channel), str(message.content[7:]), 'unsolved')
        reportTitle = "New help request: " + str(reportcode)
        embed = discord.Embed(description=reportTitle, color=0x50bdfe)
        embed.set_author(name=client.user)
        embed.add_field(name="Requester", value=message.author.mention, inline=True)
        embed.add_field(name="Date", value=str(datetime.now()), inline=True)
        embed.add_field(name="Location", value=str(message.channel), inline=True)
        embed.add_field(name="Reason", value=str(message.content[7:]), inline=True)
        await channel_mod.send(embed=embed)
        await message.channel.send(
            'Your request has been sent successfully. Your report code is ' + str(reportcode) + '.')

    elif message.content.startswith('!saverequests'):
        if canSend(4, privilegelevel(message.author), message):
            modqueue.savereportsusual()

    elif message.content.startswith('!unsolved'):
        if not canSend(4, privilegelevel(message.author), message):
            return
        channel_mod = client.get_channel(catbotdata.requireddata['mod-channel-id'])
        for i in modqueue.getunsolved():
            reportTitle = "Report id " + str(i[6])
            embed = discord.Embed(description=reportTitle, color=0x50bdfe)
            embed.set_author(name=client.user)
            embed.add_field(name="Requester", value=i[0], inline=True)
            embed.add_field(name="Date", value=i[1], inline=True)
            embed.add_field(name="Location", value=i[2], inline=True)
            embed.add_field(name="Reason", value=i[3], inline=True)
            embed.add_field(name="Status", value=i[4], inline=True)
            embed.add_field(name="Assigned to", value=i[5], inline=True)
            await channel_mod.send(embed=embed)

    elif message.content.startswith('!myreports'):
        if not canSend(4, privilegelevel(message.author), message):
            return
        channel_mod = client.get_channel(catbotdata.requireddata['mod-channel-id'])
        for i in modqueue.getassigned(message.author.mention):  # at this point we know this is a mod
            reportTitle = "Report id " + str(i[6])
            embed = discord.Embed(description=reportTitle, color=0x50bdfe)
            embed.set_author(name=client.user)
            embed.add_field(name="Requester", value=i[0], inline=True)
            embed.add_field(name="Date", value=i[1], inline=True)
            embed.add_field(name="Location", value=i[2], inline=True)
            embed.add_field(name="Reason", value=i[3], inline=True)
            embed.add_field(name="Status", value=i[4], inline=True)
            embed.add_field(name="Assigned to", value=i[5], inline=True)
            await channel_mod.send(embed=embed)

    elif message.content.startswith('!deletereport') or message.content.startswith('!removereport'):
        if not canSend(4, privilegelevel(message.author), message):
            return
        channel_mod = client.get_channel(catbotdata.requireddata['mod-channel-id'])
        report = modqueue.deletereportbyid(int(message.content[14:]))
        await channel_mod.send('Report successfully removed.')
        embed = discord.Embed(description="Report id " + str(report[6]), color=0x123456)
        embed.set_author(name=client.user)
        embed.add_field(name="Requester", value=report[0], inline=True)
        embed.add_field(name="Date", value=report[1], inline=True)
        embed.add_field(name="Location", value=report[2], inline=True)
        embed.add_field(name="Reason", value=report[3], inline=True)
        embed.add_field(name="Status", value=report[4], inline=True)
        embed.add_field(name="Assigned to", value=report[5], inline=True)
        await client.get_channel(catbotdata.requireddata['log-channel-id']).send(embed=embed)
        respondto = int(str(report[0])[3:-1])
        await client.get_user(respondto).send(
            'Your request with the code ' + str(report[6]) + ' has been solved.')


def privilegelevel(member):
    level = 1  # by default a user is unworthy
    if member.id in catbotdata.requireddata['tier-5-users']:
        return 5
    member = serveruser(member)
    if member is False:  # user not in server
        return 0
    for i in member.roles:
        if i.id in catbotdata.requireddata['tier-2-roles']:
            level = max(level, 2)  # this tier is for common users
        if i.id in catbotdata.requireddata['tier-1-roles']:
            return 1  # muted
        if i.id in catbotdata.requireddata['tier-3-roles']:  # purple/vip/worthy helper/boosters
            level = max(level, 3)
        if i.id in catbotdata.requireddata['tier-4-roles']:  # mods
            level = max(level, 4)
    return level


def canAnswer(message):
    if not isADM(
            message) and catbotdata.timelastmessage > datetime.now():  # second condition is asking if silence is active
        if privilegelevel(serveruser(message.author)) < 3:  # if you are important you can skip the silence
            return False
    return True


def canSend(tier_req, tier, message):
    if tier_req <= tier:
        if isInServer(message.author):
            return canAnswer(message)
    return False


def isADM(message):
    if isinstance(message.channel, discord.DMChannel):
        return True
    return False


def isInServer(member):
    legit_members = client.get_guild(catbotdata.requireddata['server-id']).members  # server id
    if member in legit_members:
        return True
    return False


def serveruser(member):
    legit_members = client.get_guild(catbotdata.requireddata['server-id'])  # server id
    if member in legit_members.members:
        return legit_members.get_member(member.id)
    return False


def isokayifnotclog(message, message_dm):  # if we are here, we know it's not tier 3
    if message.channel.id in catbotdata.requireddata['partial-permit-channels']:  # maybe if nobody is clogging
        rightnow = datetime.now()
        time_elapsed = rightnow - catbotdata.timerlowtier
        toret = False
        if time_elapsed.seconds > 60:  # wait for a minute
            toret = True
        catbotdata.timerlowtier = rightnow
        return toret
    if message_dm:
        return True


def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start + len(needle))
        n -= 1
    return start


enemyculator = enemyunits_catbot.Enemyunits()
modqueue = Modtools('results.tsv', 'archives.tsv')
catculator = catunits_catbot.Catunits()
catbotdata = Data_catbot.defFromFile()
stagedata = stagedata_catbot.Stagedata(enemyculator)
client.run(catbotdata.requireddata['auth-token'])
