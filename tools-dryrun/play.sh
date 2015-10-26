#!/usr/bin/env sh
DEFAULTMAP=maps/maze/maze_04p_01.map
MAP=$DEFAULTMAP

# numbers N from 01 to 56
# MAP=maps/maze/maze_p04_N.map
#MAP=maps/maze/maze_p04_37.map

# numbers N from 04 to 26
# MAP=maps/cell_maze/cell_maze_p04_N.map
#MAP=maps/cell_maze/cell_maze_p04_17.map

# numbers from 01 to 10
# MAP=maps/random_walk/random_walk_p04_N.map
#MAP=maps/random_walk/random_walk_p04_05.map

MAP=maps/maze/maze_p04_27.map


# replace mybots/BBot.py with your own bot.
./playgame.py --cutoff_turn 1000 --verbose -SoEeR --player_seed 42 --end_wait=0.25 --verbose --log_dir game_logs --turns 1000 --map_file $MAP "$@" \
    "python sample_bots/python/HunterBot.py" \
    "python sample_bots/python/GreedyBot.py" \
    "python sample_bots/python/LeftyBot.py" \
    "python mybots/BBot.py" |
java -jar visualizer.jar

