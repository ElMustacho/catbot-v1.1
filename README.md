# catbot-v1.1
Welcome to catbot, still in development/prerelease, gonna be short, here is the commands.
# Mod only commands

*!saverequests* -> stores to memory the requests, also happens after every new requests.

*!unsolved* -> gives the list of currently unresolved requests.

*!solve [number]* -> will set the report[number] as solved.

*!assignto [number], [...]* -> will set the report [number] assignee to [...], which can be everything (supports usernames).

*!assigntome [number]* -> will set the report [number] to the author of the command.

*!myreports* -> will print every report which assignee is the author (needs to be mentioned).

*!deletereport [number]* -> will delete (and store away) a report with an id = [number].

*!removereport [number]* -> same as !deletereport.

# Special people commands

*!renameunit* [exact unit name]; [custom name] allows to create an additional name to get an unit instead of using the full name. Short of case sensitiveness the first name doesn't allow errors. Custom names will be searchable immediately after.

*!silence* [number] makes catbot unable to answer tier 2 or lower users in public. DM are not affected. The number means the amount of minutes of silence, capped at 60. Repeated commands reset the time and thus do not stack.

*!letfree* removes the silence.

# User commands

*!sayhi* -> the bot greets, distinguishes between flaired users.

*!catstats [name]; [number]* -> will give out stats of the given unit, exact name doesn't need to be correct, a few errors are ok and it will be able to tell the differences (if such exists), but too many (5) means it won't try. Name is case insensitive. Optionally, putting a '; ' after the name and a level will permit to get stats for that level, otherwise it defaults to 30.

*!helpme [...]* -> the bot creates a requests, and takes the appropriate parameters. [...] is a comment, and supports calling users and channels (inside the same server).

# Tier Explanations

0 -> catbotbanned; people not registered in this server, catbot won't answer to anything

1 -> not worthy; can only send private messages, such as helpme and catstats. muted and people without the cat role are here, being muted overrides your higher tier

2 -> generic users; has the cat role, can use catbot on the server with limited usage

3 -> worthy (purple flair, pink role, fandom vip); can give custom names to units and can issue silence lv 2 (tier 2 and lower can't use commands in public up to an hour)

4 -> moderator; all commands and can issue silence lv 3 (tier 3 and lower can't use commands in public, until revoked) or lower

5 -> daddy/mommy (me); all commands and can issue lv 4 silence (I shutdown catbot), ignores being muted
