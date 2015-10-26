#!/usr/bin/env python
from random import choice, randrange
from ants import *
import sys
import logging
import time
from optparse import OptionParser

from logutils import initLogging, getLogger
logging.basicConfig(level=logging.DEBUG)

class SimpleBot:
    def __init__(self):
        # Tuple of coordinates to direction ('n', 'e', 's', 'w')
        self.ants_straight = {}
        self.ants_lefty = {}
        self.food_ants = {}
        self.killer_ants = {}
        self.razer_ants = {}

        self.has_food = {}

    def count_unpassable(self, ants, a_row, a_col, dest_row, dest_col):
        if a_row < dest_row:
            start_row = a_row
            stop_row = dest_row
        else:
            start_row = dest_row
            stop_row = a_row

        if a_col < dest_col:
            start_col = a_col
            stop_col = dest_col
        else:
            start_col = dest_col
            stop_col = a_col

        unpassable = 0
        for i in range(start_row + 1, stop_row):
            for j in range(start_col + 1, stop_col):
                if ants.passable(i, j):
                    unpassable += 1
        return unpassable

    def time_remaining(self, ants):
       return ants.turntime - int(1000 * (time.clock() - ants.turn_start_time))

    def do_turn(self, ants):
        destinations = []
        new_straight = {}
        new_lefty = {}
        new_food = {}
        new_hunter = {}
        new_hill = {}
        new_unseen = {}
        for a_row, a_col in ants.my_ants():
            if self.time_remaining(ants) < 50:
                break
            # send new ants toward closest goal
            cur_ant = (a_row, a_col)
            if (not cur_ant in self.ants_straight and not cur_ant in self.ants_lefty and not cur_ant in self.food_ants):

                closest_home = ants.closest_home(cur_ant[0], cur_ant[1])

                if cur_ant in self.has_food and closest_home:
                    # If ant has food, and there's a closest home, just go there
                    direction = ants.direction(cur_ant[0], cur_ant[1],
                                               closest_home[0], closest_home[1])
                    ants.issue_order((a_row, a_col, direction[0]))

                closest_food = ants.closest_food(cur_ant[0], cur_ant[1])
                closest_enemy_hill = ants.closest_enemy_hill(cur_ant[0], cur_ant[1])
                closest_unseen = ants.closest_unseen(cur_ant[0], cur_ant[1])

                distance_food = 9999999
                if closest_food:
                    distance_food = ants.distance(cur_ant[0], cur_ant[1], closest_food[0], closest_food[1])
                    getLogger().debug("Found food at distance %s" % distance_food)

                distance_hill = 9999999
                if closest_enemy_hill:
                    distance_hill = ants.distance(cur_ant[0], cur_ant[1], closest_enemy_hill[0], closest_enemy_hill[1])
                    getLogger().debug("Found hill at distance %s" % distance_food)

                distance_unseen = 9999999
                if closest_unseen:
                    distance_unseen = ants.distance(cur_ant[0], cur_ant[1], closest_unseen[0], closest_unseen[1])
                    getLogger().debug("Found unseen at distance %s" % closest_unseen)

                if closest_food or closest_enemy_hill or closest_unseen:
                    minimum = min(distance_food, distance_hill, distance_unseen)

                    if minimum == distance_food:
                        getLogger().debug("Going toward food")
                        direction = ants.direction(cur_ant[0], cur_ant[1], closest_food[0], closest_food[1])
                        new_food[cur_ant] = direction[0]

                    elif minimum == distance_hill:
                        getLogger().debug("Going toward hill")
                        direction = ants.direction(cur_ant[0], cur_ant[1], closest_enemy_hill[0], closest_enemy_hill[1])
                        new_hill[cur_ant] = direction[0]

                    elif minimum == distance_unseen:
                        getLogger().debug("Going toward unseen")
                        direction = ants.direction(cur_ant[0], cur_ant[1], closest_unseen[0], closest_unseen[1])
                        new_unseen[cur_ant] = direction[0]
                    ants.issue_order((a_row, a_col, direction[0]))

                else:
                    if a_row % 2 == 0:
                        if a_col % 2 == 0:
                            direction = 'n'
                        else:
                            direction = 's'
                    else:
                        if a_col % 2 == 0:
                            direction = 'e'
                        else:
                            direction = 'w'
                    self.ants_straight[(a_row, a_col)] = direction

            # send ants going in a straight line in the same direction
            if (cur_ant in self.ants_straight) or (cur_ant in self.food_ants):
                direction = self.ants_straight.get((a_row, a_col))
                if not direction:
                    direction = self.food_ants.get((a_row, a_col))
                getLogger().debug("Direction is %s" % direction)
                n_row, n_col = ants.destination(a_row, a_col, direction)
                if ants.passable(n_row, n_col):
                    if (ants.unoccupied(n_row, n_col) and
                            not (n_row, n_col) in destinations):
                        ants.issue_order((a_row, a_col, direction))
                        new_straight[(n_row, n_col)] = direction
                        destinations.append((n_row, n_col))
                    else:
                        # pause ant, turn and try again next turn
                        new_straight[(a_row, a_col)] = LEFT[direction]
                        destinations.append((a_row, a_col))
                else:
                    # hit a wall, start following it
                    self.ants_lefty[(a_row, a_col)] = RIGHT[direction]

            # send ants following a wall, keeping it on their left
            if (a_row, a_col) in self.ants_lefty:
                direction = self.ants_lefty[(a_row, a_col)]
                directions = [LEFT[direction], direction, RIGHT[direction], BEHIND[direction]]
                # try 4 directions in order, attempting to turn left at corners
                for new_direction in directions:
                    n_row, n_col = ants.destination(a_row, a_col, new_direction)
                    if ants.passable(n_row, n_col):
                        if (ants.unoccupied(n_row, n_col) and
                                not (n_row, n_col) in destinations):
                            ants.issue_order((a_row, a_col, new_direction))
                            new_lefty[(n_row, n_col)] = new_direction
                            destinations.append((n_row, n_col))
                            break
                        else:
                            # have ant wait until it is clear
                            new_straight[(a_row, a_col)] = RIGHT[direction]
                            destinations.append((a_row, a_col))
                            break

        # reset lists
        self.ants_straight = new_straight
        self.ants_lefty = new_lefty
        self.food_ants = new_food
        self.razer_ants = new_hunter

if __name__ == '__main__':
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    try:
        Ants.run(SimpleBot())
    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
