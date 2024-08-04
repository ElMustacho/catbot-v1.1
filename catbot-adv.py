# todo list
# give out the previous two nicely
# write/declare/init stuff only once
# review all code and check if you can code stuff appearing multiple times only once
import sqlite3
import io
import discord
from datetime import datetime


from data_catbot import Data_catbot
from modtools import Modtools

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print('Ready to go')



@client.event
async def on_message(message):
    if message.author == client.user:  # bot doesn't want to answer itself
        return
    if message.content == '!muted':
        if not canSend(5, privilegelevel(message.author), message):
            return
        msgtosend = '''This channel is ONLY for asking questions about your mute with moderators. All server rules apply.

Reason for your mute is mentioned in DMs with <@204255221017214977>. Do NOT block the bot. 

**You may:** 
- Ask as many questions as you'd like, provided it's about your mute.
- Ping a moderator (ideally the one who muted you, if you know who it is) to get their attention.

**Don'ts:** 
- Do NOT talk to other __muted__ people, spam or ramble about topics unrelated to your mute.
- Do NOT spam/mass ping moderators or uselessly/aggressively argue with them.
- Attempt to bypass the mute by leaving and rejoining, using alternative accounts, etc. **This will result in a permanent and unappealable ban.**

If you misuse the channel, your mute will be **extended**. 
If you continue to misuse the channel after a mute extension, you will be **banned**.'''
        await message.channel.send(msgtosend)
        await message.delete()
        return
    elif message.content.startswith('!say'):
        if not canSend(5, privilegelevel(message.author), message):
            return
        looking = message.content[message.content.find(' ') + 1: find_nth(message.content, ' ', 2)]
        channel_to_send = client.get_channel(int(looking))
        message_to_send = message.content[find_nth(message.content, ' ', 2):]
        await channel_to_send.send(message_to_send)
        return
    elif message.content == '!archive':
        archive_channel = client.get_channel(713964900556341278)
        await archive_channel.send('Beginning logging.')
        if not canSend(5, privilegelevel(message.author), message):
            return
        if message.channel.id != catbotdata.requireddata['mute-channel']:
            await archive_channel.send('You must use this command in the proper channel.')
            return
        messages = [message async for message in client.get_channel(catbotdata.requireddata['mute-channel']).history()]
        users = set()
        for message in reversed(messages[:-1]):
            users.add(message.author)
            color_used = None
            if privilegelevel(message.author) > 4:  # is a mod
                color_used = 0xff0000
            else:  # otherwise they were muted
                color_used = 0x000000
            tobesent=discord.Embed(description=str(message.author) + ' (' + str(message.author.id) + ')', color=color_used)
            tobesent.add_field(name='Message content', value=message.content)  #todo deal with string too long
            #await archive_channel.send(message.author.mention + ' ' + str(message.content), allowed_mentions = discord.AllowedMentions(users = False))
            if len(message.content) > 0:
                await archive_channel.send(embed=tobesent)
            for att in enumerate(message.attachments):
                obtained = await att[1].read()
                arr = io.BytesIO(obtained)
                file = discord.File(arr, filename=att[1].filename)
                await archive_channel.send('There was this attachement:', file=file)
        mentions = ""
        for user in users:
            if privilegelevel(user) < 5:
                mentions += user.mention + ', '
        if len(mentions) > 0:
            mentions=mentions[:-2]
        await archive_channel.send('End of logging.\n' + mentions)
        return
    elif (privilegelevel(message.author) < 4 or privilegelevel(message.author) == 6) and (message.channel.id in [355181142342893568, 355180827589738497, 440680736400343040, 358826700240322573]) and not message.author.bot:
        badwords = ["seed track", "track", "energy glitch", "nrglitch", "nrg", "godfat", "seedling", "railway_track", "macro", "autoclicker", "autotapper", "auto tapper", "auto clicker"]
        # will hardcode here
        msg = message.content.lower()
        #print(msg)
        for word in badwords:
            if word in msg:
                await log_badword(message, word)
                return
        if msg.count("time traveller") + msg.count("time traveler") < msg.count("time travel"):
            await log_badword(message, "time travel")
            return
            
@client.event
async def on_message_delete(message):
    if message.author.bot:
        return
    logchannel = client.get_channel(396154070890577922)
    if privilegelevel(message.author) > 4:
        author_of_message=str(message.author.id) + ', who is a mod'
    else:
        author_of_message=(message.author.mention)
    await logchannel.send("A message from: "+ author_of_message + ", created <t:"+str(round(message.created_at.timestamp()))+":R> was deleted in " + message.channel.mention + " and the text was the following:\n" + message.content)
    for att in enumerate(message.attachments):
        await logchannel.send('There was this attachement:', file=await att[1].to_file())
    return

async def log_badword(message,word):
    logchannel = client.get_channel(702592607703924776)
    await logchannel.send(message.author.mention + " discussed **"+word+"** in " + message.channel.mention + ".\nLink: https://discord.com/channels/647384175208300545/"+str(message.channel.id)+"/"+str(message.id))
    return

def privilegelevel(member):
    level = 1  # by default a user is unworthy
    if member.id in catbotdata.requireddata['tier-6-users']:
        return 6
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
        if i.id in catbotdata.requireddata['tier-4-roles']:  # power_users
            level = max(level, 4)
        if i.id in catbotdata.requireddata['tier-5-roles']:  # mods
            level = max(level, 5)
    return level


def canAnswer(message):
    if not isADM(message) and catbotdata.timelastmessage > datetime.now():  # is silence is active
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


def catch(func, handle=lambda e: e, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        return handle(e)


def log_event(message, user, date, result):
    if not catbotdata.requireddata['logging']:
        return
    try:
        command, parameters = message[:message.find(' ')], message[message.find(' ')+1:]
    except Exception as E:
        command = message
        parameters = None
    try:
        conn = sqlite3.connect('logging.db')
        cursor = conn.cursor()
        cursor.execute('''insert into events (command, parameters, user, time, success) values (?,?,?,?,?);''', (command, parameters, int(user), str(date), result))
        conn.commit()
    except Exception as E:
        print(E)
    finally:
        print('logged '+str((command, parameters, user, date, result)))
        return
modqueue = Modtools('results.tsv', 'archives.tsv')
catbotdata = Data_catbot.defFromFile()
client.run(catbotdata.requireddata['auth-token'])
