# CatBot Commands
If you see innaccuracies here, feel free to point them out.



## Syntax
`!<command_name> <parameter>; [<optional_parameter>] = <default_value>`

Colour coding of commands will be done as per [privilege levels](privilege_levels.md).



## Unit stats & info

### catstats / cs
`!cs cat_unit; [level] = 30`

Returns the specified unit’s stats.

All EoC treasures are assumed complete.

__Example:__ `!cs surfer cat; 25`


### cst
`!cst cat_unit; [level] = 30; [talent_1] = max; [talent_2] = max; [talent_3] = max; [talent_4] = max; [talent_5] = max`

Returns the specified unit’s stats, with support for talents. All EoC treasures are assumed complete.

The order for talents is listed below the stats when the command is used without arguments.

Entering a non-integer level makes it default to the highest level. Entering a negative level makes it default to 0.

__Example:__ `!cst can can cat; 37; 1;0;10;10;10`


### enemystats / es
`!es enemy_unit; [magnification] = 100; [atk_magnification] = [magnification]`

Returns the specified enemy’s stats.

The third parameter allows you to specify magnifications for attack and health separately (the first parameter being used for health), though split magnifications are only used for baron (gauntlet) bosses in-game. If the third parameter is left blank, the second parameter will be used for both attack and health.

__Example:__ `!es Nimoy Bore; 750`


### rawtalents
`!rawtalents cat_unit`

Returns raw talents data of the specified unit.

__Example:__ `!rawtalents can can cat`



## Stages

### stagebeta / sb
`!sb stage_name; [map_name]; [category]`

Returns the schematics of the specified stage.

The second and third parameters are optional, though they may be necessary to use if multiple stages have similar names, which is the case for certain enigma stages. You can skip the difficulty of the stage in its title, as seen in the last example.

__Examples:__
- `!sb No Plan A (Deadly)`
- `!sb The Big Bang; CotC Ch.2; CH`
- `!sb Cradle Shrine; Necro Cradle; Enigma`


### sbid
`!sbid stage_ID`

Returns the schematics of the stage with the given ID.

Stage IDs appear when you use !sb. This is mostly meant for debugging purposes, but feel free to use it if you wish to.

__Example:__ `!sbid 1007`


### whereis
`!whereis enemy; [enemy_2]; [enemy_3]`

Returns all stages where the specified enemy appears. Specify multiple enemies to return every stage where __all__ of them appear.

__Example:__ `!whereis JK Bun Bun; Capy; Those Guys`


### whereisb
`!whereisb enemy; [enemy_2]; [enemy_3]`

Returns all stages where the specified enemy appears, but as an embed. Specify multiple enemies to return every stage where __all__ of them appear.

__Example:__ `!whereis JK Bun Bun; Capy; Those Guys`


### whereismonthly
`!whereismonthly enemy; [enemy_2]; [enemy_3]`

Returns all stages where the specified enemy appears (sorted in ascending order of energy cost). Specify multiple enemies to return every stage where __all__ of them appear.

__Example:__ `!whereismonthly JK Bun Bun; Capy`



## Combos

### comboname
`!comboname name_of_combo`

Returns the specified CatCombo’s full name, the units needed to activate it, and its effect.

__Example:__ `!comboname Part-Time Coworkers`


### combowith
`!combowith cat_unit`

Returns all combos the specified unit is a part of.

This command is form-sensitive, meaning that if you specify a unit’s first form, combos that require its 2nd or 3rd form will not be shown.

__Example:__ `!combowith Riceball Cat`



## Aliases

### renamecat
`!renamecat existing_name; new_alias`

Creates an alias (custom name) to use instead of the real name when using a command for a unit.

__Example:__ `!renamecat Manic Macho Legs; MML`


### catnamesof
`!catnamesof cat_unit`

Returns all custom names for the specified cat unit.

__Example:__ `!catnamesof Diabolic Gao`


### deletecatname
`!deletecatname actual_name; custom_name`

Deletes the specified custom name.

__Example:__ `!deletecatname Manic Macho Legs; MML`


#### !renameenemy enemy_unit; new_alias | !enemynamesof enemy_unit | !deleteenemyname actual_name; custom_name 
See the three previous commands: they work the same.



## Miscellaneous

### sayhi
`!sayhi`

Responds to you based on your privilege level.


### say
`!say channel_id message_content`

Send a message in a specified channel.



## Custom commands
(WIP)