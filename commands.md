# CatBot Commands
If you see innaccuracies here, feel free to point them out.

## Syntax
`!<command_name> <parameter>; [<optional_parameter>] = <default_value>`

Colour coding of commands will be done as per [privilege levels](privilege_levels.md).

## Unit stats & info

#### catstats / cs
`!cs cat_unit; [level] = 30`

Returns the specified unit’s stats.

All EoC treasures are assumed complete.

__Example:__ `!cs surfer cat; 25`


#### cst
`!cst cat_unit; [level] = 30; [talent_1] = max; [talent_2] = max; [talent_3] = max; [talent_4] = max; [talent_5] = max`

Returns the specified unit’s stats, with support for talents. All EoC treasures are assumed complete.

The order for talents is listed below the stats when the command is used without arguments.

Entering a non-integer level makes it default to the highest level. Entering a negative level makes it default to 0.

__Example:__ `!cst can can cat; 37; 1;0;10;10;10`


#### enemystats / es
`!es enemy_unit; [magnification] = 100; [atk_magnification] = [magnification]`

Returns the specified enemy’s stats.

The third parameter allows you to specify magnifications for attack and health separately (the first parameter being used for health), though split magnifications are only used for baron (gauntlet) bosses in-game. If the third parameter is left blank, the second parameter will be used for both attack and health.

__Example:__ `!es Nimoy Bore; 750`


#### rawtalents
`!rawtalents cat_unit`

Returns raw talents data of the specified unit.

__Example:__ `!rawtalents can can cat`
