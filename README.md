# CatBot v1.1

## How to use
Run catbot.py, but be sure to get config.json sorted out first.
Given that you need an auth token for it to work, and that's not something meant to shared, you can't skip that, hence 
why there is no preconfigured file, but just a sample.
Catbot will gladly tell you whatever isn't working in the console output. Most of the times, it's missing perms discord
wise.
Feel free to run it in background, anyway.

## Documentation
See [here](commands.md) for a list of commands, [here](custom_commands.md) for a list of custom commands, and
[here](privilege_levels.md) for a list of privilege levels.

## Some Q&A

### Why are there 3 data formats?
Because refactoring code that works is time I'd like to spend on more functionalities.

### Where do you get the data from?
Game files after some post processing. Icons are procedurally generated (me) or hand made (not me), and stored here 
instead of being sent
because it's better to have a pointer than to send the whole thing. Custom names come from discord users.

### This is a discord bot and slash commands are not implemented, why?
This can summarily be shortened with "Discord Bad". The longer version of this is that I use the bot for moderation too,
and that implies slash commands not being enough with, let's say, identifying a certain kind of messages. The library
also stopped development, and while slash commands are not exactly done, everything else works good. Lastly, discord bad, 
which is also the reason of why the library stopped its development.

### What's catbot-adv.py?

That's catbot, with all the cool things I add as progress goes ahead.
I make no promises, but run this instead of catbot.py if you feel like using new features.

### Why do you show the password of the discord server in the files?

If you are smart enough to be here and understand what's going on, you don't need 10 minutes and 5 attempts to read the 
rule channels.

