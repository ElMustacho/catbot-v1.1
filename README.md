# catbot-v1.1
Welcome to catbot, still in development/prerelease, gonna be short, here is the commands
# Mod only commands

*!helpme [...]* -> the bot creates a requests, and takes the appropriate parameters. [...] is a comment, and supports calling users and channels (inside the same server)

*!saverequests* -> stores to memory the requests, also happens after every new requests

*!unsolved* -> gives the list of currently unresolved requests

*!solve [number]* -> will set the report[number] as solved

*!assignto [number], [...]* -> will set the report [number] assignee to [...], which can be everything (supports usernames)

*!assigntome [number]* -> will set the report [number] to the author of the command

*!myreports* -> will print every report which assignee is the author (needs to be mentioned)

*!deletereport [number]* -> will delete (and store away) a report with an id = [number]

*!removereport [number]* -> same as !deletereport

# Special people commands

*!renameunit* [exact unit name]; [custom name] allows to create an additional name to get an unit instead of using the full name. Short of case sensitiveness the first name doesn't allow errors. Custom names will be searchable immediately after.

*!silence* [number] makes catbot unable to answer tier 2 or lower users in public. DM are not affected. The number means the amount of minutes of silence, capped at 60. Repeated commands reset the time and thus do not stack

*!letfree* removes the silence.

# User commands

*!sayhi* -> the bot greets, distinguishes between flaired users

*!catstats [name]; [number]* -> will give out stats of the given unit, exact name doesn't need to be correct, a few errors are ok and it will be able to tell the differences (if such exists), but too many (5) means it won't try. Name is case insensitive, eventually it will work for custom names too. Optionally, putting a '; ' after the name and a level will permit to get stats for that level, otherwise it defaults to 30

