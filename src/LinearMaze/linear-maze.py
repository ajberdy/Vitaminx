#!/usr/bin/env python
"""
##########################
     #      #         #
  #    *        #
         #     #       #
#########################
"""
import time

import numpy as np
import curses

EMPTY = 0
BLOCK = 1
RACER = 2
GOAL = 3

RIGHT = 4
LEFT = 5
FORWARD = 6
BACKWARD = 7

COIN = 8
BOMB = 9
SPIKE = 10
DIAMOND = 11


class Track:

    def __init__(self, length=100, width=3):
        self.track = np.zeros([length + 1, width+2], dtype=int)
        self.track[:, 0] = self.track[:, -1] = BLOCK
        self.track[-1, :] = GOAL
        self.width = width + 2
        self.length = length + 1
        self.racer_pos = width // 2, 0
        self.goodies = np.zeros([length, width])
        self.initialize_goodies()

    def show(self):
        # print(self.track)
        # return "TRACK"
        return str(self.track)

    def __getitem__(self, item):
        return self.track[item]

    def __setitem__(self, key, value):
        return self.track.__setitem__(key, value)

    def move(self, direction):
        x, y = self.racer_pos
        if direction == RIGHT:
            next_pos = x + 1, y
        elif direction == LEFT:
            next_pos = x - 1, y
        elif direction == FORWARD:
            next_pos = x, y + 1
        elif direction == BACKWARD:
            next_pos = x, y - 1
        else:
            raise TypeError("Bad direction")

        next_x, next_y = next_pos
        if not (0 <= next_y < self.length and 0 <= next_x < self.width):
            return False

        if self.track[next_y][next_x] not in (EMPTY, GOAL):
            return False

        self.racer_pos = next_x, next_y

        return True

    def initialize_goodies(self):
        goodies = [COIN, BOMB, SPIKE, DIAMOND, EMPTY]
        probs = [.1, .02, .1, .01, .77]
        for y in range(self.length - 1):
            for x in range(self.width - 2):
                self.goodies[y][x] = np.random.choice(goodies, p=probs)


class Racer:

    def __init__(self, x, y):
        self.pos = x, y
        self.x = x
        self.y = y
        self.states = (RIGHT, LEFT)
        self.state = 1

    def get_action(self, input_vector, x_pos):
        """ return action in RIGHT, LEFT, FORWARD, BACKWARD """

        x = x_pos
        current_row, row_in_front = input_vector.reshape([2, -1])

        if not row_in_front[x] or row_in_front[x] == GOAL:
            return FORWARD

        dx = -1 if self.state else 1
        if current_row[x + dx]:
            self.state += 1
        self.state %= 2

        return self.states[self.state]


def main():

    try:
        screen = curses.initscr()
        curses.start_color()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)

        screen.keypad(True)

        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_YELLOW)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_GREEN)
        curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLUE)
        curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_BLUE)
        curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(8, curses.COLOR_GREEN, curses.COLOR_BLUE)

        track = Track(50, 5)
        racer = Racer(*track.racer_pos)
        score = 0

        while True:
            height, width = screen.getmaxyx()
            # screen.addstr(1, 10, f"height: {height}, width: {width}")

            left_wall = width//2 - track.width//2

            for y in range(min(height, track.length)):
                for x in range(track.width):
                    pixel = track[y][x]
                    if x in (0, track.width - 1) or y == track.length - 1 or not track.goodies[y][x - 1]:
                        screen.addstr(height - y - 1, left_wall + x, ' ', curses.color_pair(pixel + 1))
                    else:
                        if track.goodies[y][x - 1] == COIN:
                            screen.addstr(height - y - 1, left_wall + x, '0', curses.color_pair(5))
                        elif track.goodies[y][x - 1] == BOMB:
                            screen.addstr(height - y - 1, left_wall + x, '#', curses.color_pair(6))
                        elif track.goodies[y][x - 1] == SPIKE:
                            screen.addstr(height - y - 1, left_wall + x, '^', curses.color_pair(7))
                        elif track.goodies[y][x - 1] == DIAMOND:
                            screen.addstr(height - y - 1, left_wall + x, '*', curses.color_pair(8))

            x, y = track.racer_pos
            if track[y][x] == GOAL:
                screen.addstr(5, 5, "YOU DID IT!!")
                screen.getch()
                break
            elif track.goodies[y][x - 1] == COIN:
                score += 1
                track.goodies[y][x - 1] = EMPTY
            elif track.goodies[y][x - 1] == BOMB:
                score -= 10
                track.goodies[y][x - 1] = EMPTY
            elif track.goodies[y][x - 1] == SPIKE:
                score -= 1
                track.goodies[y][x - 1] = EMPTY
            elif track.goodies[y][x - 1] == DIAMOND:
                score += 30
                track.goodies[y][x - 1] = EMPTY
            screen.addstr(height//4, width*3//4, f"SCORE: {score}       ")
            
            screen.addstr(height - y - 1, left_wall + x, ' ', curses.color_pair(RACER + 1))

            # action = racer.get_action(track[racer_y:racer_y + 2, :], racer_x)
            # track.move(action)

            screen.refresh()
            time.sleep(.1)

            char = screen.getch()
            if char == ord('q'):
                break
            elif char == curses.KEY_RIGHT or char == ord('d'):
                track.move(RIGHT)
            elif char == curses.KEY_LEFT or char == ord('a'):
                track.move(LEFT)
            elif char == curses.KEY_UP or char == ord('w'):
                track.move(FORWARD)
            elif char == curses.KEY_DOWN or char == ord('s'):
                track.move(BACKWARD)

    finally:
        # shut down cleanly
        curses.nocbreak()
        screen.keypad(0)
        curses.echo()
        curses.endwin()


if __name__ == '__main__':
    main()