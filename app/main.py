import json
import os
import random
from enum import Enum

import bottle
import numpy as np

from app.api import ping_response, start_response, move_response, end_response

@bottle.route('/')
def index():
    return '''
    Battlesnake documentation can be found at
       <a href="https://docs.battlesnake.io">https://docs.battlesnake.io</a>.
    '''

@bottle.route('/static/<path:path>')
def static(path):
    """
    Given a path, return the static file located relative
    to the static folder.

    This can be used to return the snake head URL in an API response.
    """
    return bottle.static_file(path, root='static/')

@bottle.post('/ping')
def ping():
    """
    A keep-alive endpoint used to prevent cloud application platforms,
    such as Heroku, from sleeping the application instance.
    """
    return ping_response()

@bottle.post('/start')
def start():
    data = bottle.request.json

    """
    TODO: If you intend to have a stateful snake AI,
            initialize your snake state here using the
            request's data if necessary.
    """
    print(json.dumps(data))
    color = "#C0C0C0"
    headType = evil
    tailType = bolt

    return start_response(color, headType, tailType)


class BoardPieces(Enum):
    EMPTY = 0
    FOOD = 1
    ENEMY = 2
    ENEMY_HEAD = 3
    HEAD = 4
    BODY = 5


@bottle.post('/move')
def move():
    data = bottle.request.json

    """
    TODO: Using the data from the endpoint request object, your
            snake AI must choose a direction to move in.
    """

    print(data)

    board = data["board"]
    food = board["food"]
    snakes = data["snakes"]
    you = data["snakes"]["you"]
    game_id = data["game"]["id"]
    game_turn = data["game"]["turn"]

    game_board = np.zeros(shape=(board["width"], board["height"]))

    # Add food
    for f in food:
        fx = f["x"]
        fy = f["y"]
        game_board[fx][fy] = BoardPieces.FOOD.value

    # Add Snakes
    for s in snakes:
        for index, b in enumerate(s["body"]):
            bx = b["x"]
            by = b["y"]
            game_board[bx][by] = BoardPieces.ENEMY_HEAD.value \
                                    if index == 0 \
                                    else BoardPieces.ENEMY.value

    # Add self
    our_head = None
    direction = 0
    for index, y in enumerate(you["body"]):
        bx = y["x"]
        by = y["y"]
        if index == 0:
            our_head = (bx, by)
        game_board[bx][by] = BoardPieces.HEAD.value \
                                if index == 0 \
                                else BoardPieces.BODY.value

    possible_moves = []

    # Left, right, up, down
    moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    for x, y in moves:
        # Check surroundings
        next_square = (our_head[0] + x, our_head[1] + y)

        # check for out of bounds
        if next_square[0] < 0 or next_square[0] > game_board.size[0] or \
            next_square[1] < 0 or next_square[1] > game_board.size[1]:
            continue

        if game_board[next_square[0]][next_square[1]] in [BoardPieces.FOOD.value, BoardPieces.EMPTY.value]:
            possible_moves.append((x, y))


    directions = ['left', 'right', 'up', 'down']

    moves_zipped = zip(directions, moves)
    # [("left", (1, 0))]

    my_directions = [i for i, j in moves_zipped if j in possible_moves]

    direction = random.choice(my_directions)
    return move_response(direction)


@bottle.post('/end')
def end():
    data = bottle.request.json

    """
    TODO: If your snake AI was stateful,
        clean up any stateful objects here.
    """
    print(json.dumps(data))

    return end_response()

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=os.getenv('DEBUG', True)
    )
