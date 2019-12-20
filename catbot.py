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
from datetime import datetime
from data_catbot import Data_catbot
import logging
from modtools import Modtools
import catunits_catbot

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='dsd.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

client = discord.Client()
modchannelid = 652569911113023498  # 647749653495808010 old channel
logchannelid = 396154070890577922


@client.event
async def on_ready():
    print('Ready to go')


@client.event
async def on_message(message):
    if len(str(message.content)) > 200:  # don't bother with stuff too long
        return

    if '\t' in message.content:  # catbot doesn't like tab
        return

    if message.author == client.user:  # bot doesn't want to answer itself
        return

    elif message.content.startswith('!sayhi'):
        if isADM(message):
            await message.channel.send('Greetings, user.')
            return
        list_roles = [str(role) for role in message.author.roles]  # tbd
        if isAMod(message.author):
            await message.channel.send('So cool, you are a mod <3!')
        elif 'Purple Flair' in list_roles:
            await message.channel.send('You have a Purple Flair, nice!')
        else:
            await message.channel.send('You don\'t have a Purple Flair,'
                                       + 'that\'s not cool.')

    elif message.content.startswith('!time'):
        if not isAMod(message.author):  # only mods can do this
            return
        await message.channel.send('Time was: ' + str(data.timelastmessage))
        data.timelastmessage = datetime.now()
        await message.channel.send('Time is now: ' + str(data.timelastmessage))

    elif message.content.startswith('!helpme'):  # todo beautify this
        if not isInServer(message.author):  # to request help, you need to be
            return  # a member, also helps with spam
        channel_mod = client.get_channel(modchannelid)
        message_to_send = str(message.author.mention) + ' has requested help' + \
                          ' regarding: ' + str(message.content[8:])
        reportcode = modqueue.addentry(str(message.author.mention), str(datetime.now()),
                                       str(message.channel), str(message.content[7:]),
                                       'unsolved')
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
        if isAMod(message.author):  # modonly command
            modqueue.savereportsusual()

    elif message.content.startswith('!unsolved'):
        if not isAMod(message.author):  # modonly command
            return
        channel_mod = client.get_channel(modchannelid)
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

    elif message.content.startswith('!solve'):
        if not isAMod(message.author):  # modonly command
            return
        channel_mod = client.get_channel(modchannelid)
        modqueue.setsolvedbyindex(int(message.content[7:]))
        await channel_mod.send('Report has been set as solved')

    elif message.content.startswith('!assignto'):

        if not isAMod(message.author):  # modonly command
            return
        if message.content.startswith('!assigntome'):
            modqueue.setassigned(int(message.content[11:]), message.author.mention)
        else:
            modqueue.setassigned(int(message.content[9:message.content.find(
                ',')]), message.content[message.content.find(',') + 2:])
        channel_mod = client.get_channel(modchannelid)
        await channel_mod.send('Assignment done')

    elif message.content.startswith('!catstats'):
        if not isADM(message):
            if not isWorthy(message.author):  # isWorthy command, for now
                return
        limit = message.content.find(';')
        if limit == -2:
            limit = len(message.content)
        catstats = catculator.getUnitCode(message.content[10:limit].lower(),
                                          6)  # second parameter is number of errors allowed
        if catstats[0] is None:  # too many errors
            await message.channel.send('That was gibberish.')
            return
        if len(catstats[0]) > 1:  # name wasn't unique
            await message.channel.send('Couldn\'t discriminate.')
            return
        cat = catculator.getrow(catstats[0][0])
        if cat is None:
            await message.channel.send('Invalid code for cat unit')
            return
        try:
            level = int(message.content[message.content.find(';') + 2:])
        except:
            level = 30
        if level < 0 or level > 131:
            level = 30
        embedsend = catculator.getstatsEmbed(cat, level, catstats[1])
        await message.channel.send(embed=embedsend)

    elif message.content.startswith('!myreports'):
        if not isAMod(message.author):
            return
        channel_mod = client.get_channel(modchannelid)
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
        if not isAMod(message.author):
            return
        channel_mod = client.get_channel(modchannelid)
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
        await client.get_channel(logchannelid).send(embed=embed)
        await client.get_user(int(str(report[0])[2:-1])).dm_channel.send(
            'Your request with the code ' + str(report[6]) + ' has been solved')

    elif message.content.startswith('!renameunit'):
        # if not isWorthy(message.author):  # isWorthy command, for now
        #    return
        limit = message.content.find(';')
        if limit < 0:
            await message.channel.send('Incorrect format, check command format')
            return
        realnameunit = message.content[12: limit]
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
            await message.channel.send('Should have worked')
        else:
            await message.channel.send('Name was already used')

def isAMod(member):  # is a mod, but only in the battlecats server
    try:
        for i in member.roles:  # 355179088245424128, 355179230889508864 are mods
            if 355179088245424128 == i.id or 355179230889508864 == i.id:
                return isInServer(member)
    except:  # if it breaks, in doubt, the user isn't a mod
        print('something failed, please check')  # tbi
    return False


def isWorthy(member):
    try:
        if 'Muted' in member.roles:
            return False
        if len(member.roles) > 1:
            return True
    except:  # if something goes wrong, they aren't worthy
        return False
    return False


def isADM(message):
    if isinstance(message.channel, discord.DMChannel):
        return True
    return False


def isInServer(member):
    legit_members = client.get_guild(355179033018892289).members  # server id
    if member in legit_members:
        return True
    return False


modqueue = Modtools('results.tsv', 'archives.tsv')
catculator = catunits_catbot.Catunits()
data = Data_catbot.defFromFile()
client.run(data.auth_token)
