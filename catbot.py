# todo list
# give out cat units (to be finished)
# give out enemy units
# give out the previous two nicely
# write/declare/init stuff only once
# don't upload to git unwanted files
# get fixed values from a file, like the token
# make embed function, for each kind of embed
# tell the user what happens when a report belonging to him is solved or initiated
import discord
from datetime import datetime, timedelta
from data_catbot import Data_catbot
import logging
from modtools import Modtools
import catunits_catbot
import enemyunits_catbot

# logger = logging.getLogger('discord')
# logger.setLevel(logging.DEBUG)
# handler = logging.FileHandler(filename='dsd.log', encoding='utf-8', mode='w')
# handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
# logger.addHandler(handler)
client = discord.Client()


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
            return
        await message.channel.send('Your tier is: ' + str(privilegelevel(message.author)))

    elif message.content.startswith('!catstats'):
        if not canSend(1, privilegelevel(message.author), message):
            return
        if privilegelevel(message.author) < 3 and message.channel.id not in data.requireddata['freeforall-channels']:
            return
        limit = message.content.find(';')
        if limit == -1:
            limit = len(message.content)
        catstats = catculator.getUnitCode(message.content[10:limit].lower(),
                                          6)  # second parameter is number of errors allowed
        if catstats is None:  # too many errors
            await message.channel.send(message.content[10:limit] + '; wasn\'t recognized.')
            return
        try:
            lenght = len(catstats[0])
        except TypeError:  # it's a number
            catstats[0] = [catstats[0]]
        if len(catstats[0]) > 1:  # name wasn't unique
            await message.channel.send('Couldn\'t discriminate.')
            return
        cat = catculator.getrow(catstats[0][0])
        if cat is None:
            await message.channel.send('Invalid code for cat unit.')
            return
        try:
            level = int(message.content[message.content.find(';') + 1:])
        except:
            level = 30
        if level < 0 or level > 130:
            level = 30
        embedsend = catculator.getstatsEmbed(cat, level, message.content[10:limit], catstats[0][0])
        await message.channel.send(embed=embedsend)

    elif message.content.startswith('!enemystats'):
        if not canSend(1, privilegelevel(message.author), message):
            return
        if privilegelevel(message.author) < 3 and message.channel.id not in data.requireddata['freeforall-channels']:
            return
        limit = message.content.find(';')
        if limit == -1:
            limit = len(message.content)
        enemystats = enemyculator.getUnitCode(message.content[12:limit].lower(),
                                          6)  # second parameter is number of errors allowed
        if enemystats is None:  # too many errors
            await message.channel.send(message.content[12:limit] + '; wasn\'t recognized.')
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
                border = len(message.content)
            magnification = float(int(message.content[message.content.find(';') + 1:border])/100)
        except:
            magnification = 1
        if magnification < 0 or magnification > 1000000:
            magnification = 1
        embedsend = enemyculator.getstatsembed(enemy, magnification, message.content[12:limit])
        await message.channel.send(embed=embedsend)

    elif message.content.startswith('!renamecat'):
        if not canSend(3, privilegelevel(message.author), message):
            return
        limit = message.content.find(';')
        if limit < 0:
            await message.channel.send('Incorrect format, check command format.')
            return
        realnameunit = message.content[11: limit]
        catcode = catculator.getUnitCode(realnameunit.lower(), 0)
        if catcode is None:  # too many errors
            await message.channel.send('That was gibberish.')
            return
        if len(catcode[0]) > 1:  # name wasn't unique
            await message.channel.send('Couldn\'t discriminate.')
            return

        if catcode[0][0] is None:
            await message.channel.send('Invalid code for cat unit')
            return
        response = catculator.givenewname(catcode[0][0], message.content[limit+2:])
        if response:
            await message.channel.send('The name ' + message.content[limit+2:] + ' is now assigned.')
        else:
            await message.channel.send('Name was already used.')

    elif message.content.startswith('!renameenemy'):
        if not canSend(3, privilegelevel(message.author), message):
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
        response = enemyculator.givenewname(enemycode[0][0], message.content[limit+2:])
        if response:
            await message.channel.send('The name ' + message.content[limit+2:] + ' is now assigned.')
        else:
            await message.channel.send('Name was already used.')

    elif message.content.startswith('!silence'):
        if not canSend(3, privilegelevel(message.author), message):
            return
        timestop = min(60, int(message.content[9:]))
        data.timelastmessage = datetime.now() + timedelta(minutes=timestop)
        await message.channel.send("I'll be silent for a while")

    elif message.content.startswith('!letfree'):
        if not canSend(3, privilegelevel(message.author), message):
            return
        data.timelastmessage = datetime.now()
        await message.channel.send("I can speak again")

    elif message.content.startswith('!catnamesof'):
        if not canSend(2, privilegelevel(message.author), message):
            return
        catstats = catculator.getUnitCode(message.content[12:].lower(),
                                          6)  # second parameter is number of errors allowed
        if catstats[0] is None:  # too many errors
            await message.channel.send(message.content[12:] + '; wasn\'t recognized')
            return
        if len(catstats[0]) > 1:  # name wasn't unique
            await message.channel.send('Couldn\'t discriminate.')
            return
        cat = catculator.getrow(catstats[0][0])
        await message.channel.send(catculator.getnames(cat, catstats[0][0]))

    elif message.content.startswith('!enemynamesof'):
        if not canSend(2, privilegelevel(message.author), message):
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
        if not canSend(3, privilegelevel(message.author), message):
            return
        limit = message.content.find(';')
        if limit < 0:
            await message.channel.send('Incorrect format, check command format')
            return
        realnameunit = message.content[15: limit]
        catcode = catculator.getUnitCode(realnameunit.lower(), 0)
        if catcode is None:  # too many errors
            await message.channel.send('That was gibberish.')
            return
        if len(catcode[0]) > 1:  # name wasn't unique
            await message.channel.send('Couldn\'t discriminate.')
            return
        if catcode[0][0] is None:
            await message.channel.send('Invalid code for cat unit')
            return
        operationsuccess = catculator.removename(catcode[0][0], message.content[limit+2:])
        if operationsuccess:
            await message.channel.send('Name was deleted successfully.')
        else:
            await message.channel.send('No such name to delete')

    elif message.content.startswith('!deleteenemyname'):
        if not canSend(3, privilegelevel(message.author), message):
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

    elif not data.requireddata['moderation']:
        return

    elif message.content == '$password ururun wolf':
        if message.channel.id == data.requireddata['welcome-channel']:
            member = serveruser(message.author)
            await member.add_roles(discord.utils.get(client.get_guild(data.requireddata['server-id']).roles,
                                                      id=data.requireddata['tier-2-roles'][0]), reason='Entering server')
            await message.delete()
            await client.get_channel(data.requireddata['log-channel-id']).send(message.author.mention + ' has used the password.')

    elif message.content.startswith('!solve'):
        if not canSend(4, privilegelevel(message.author), message):
            return
        channel_mod = client.get_channel(data.requireddata['mod-channel-id'])
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
        channel_mod = client.get_channel(data.requireddata['mod-channel-id'])
        await channel_mod.send('Assignment done')

    elif message.content.startswith('!helpme'):  # todo beautify this
        if not canSend(1, privilegelevel(message.author), message):
            return
        channel_mod = client.get_channel(data.requireddata['mod-channel-id'])
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
        channel_mod = client.get_channel(data.requireddata['mod-channel-id'])
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
        channel_mod = client.get_channel(data.requireddata['mod-channel-id'])
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
        channel_mod = client.get_channel(data.requireddata['mod-channel-id'])
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
        await client.get_channel(data.requireddata['log-channel-id']).send(embed=embed)
        respondto = int(str(report[0])[3:-1])
        await client.get_user(respondto).send(
            'Your request with the code ' + str(report[6]) + ' has been solved.')


def privilegelevel(member):
    level = 1  # by default a user is unworthy
    if member.id in data.requireddata['tier-5-users']:
        return 5
    member = serveruser(member)
    if member is False:  # user not in server
        return 0
    for i in member.roles:
        if i.id in data.requireddata['tier-2-roles']:
            level = max(level, 2)  # this tier is for common users
        if i.id in data.requireddata['tier-1-roles']:
            return 1  # muted
        if i.id in data.requireddata['tier-3-roles']:  # purple/vip/worthy helper/boosters
            level = max(level, 3)
        if i.id in data.requireddata['tier-4-roles']:  # mods
            level = max(level, 4)
    return level


def canAnswer(message):
    if not isADM(message) and data.timelastmessage > datetime.now():  # second condition is asking if silence is active
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
    legit_members = client.get_guild(data.requireddata['server-id']).members  # server id
    if member in legit_members:
        return True
    return False


def serveruser(member):
    legit_members = client.get_guild(data.requireddata['server-id'])  # server id
    if member in legit_members.members:
        return legit_members.get_member(member.id)
    return False


enemyculator = enemyunits_catbot.Enemyunits()
modqueue = Modtools('results.tsv', 'archives.tsv')
catculator = catunits_catbot.Catunits()
data = Data_catbot.defFromFile()
client.run(data.requireddata['auth-token'])
