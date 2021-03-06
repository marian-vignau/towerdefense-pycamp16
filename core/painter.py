import os
import glob
import sys

import pyglet

pyglet.clock.set_fps_limit(60)

# set images paths
pyglet.resource.path = ['media/images']
pyglet.resource.reindex()
# load bitmaps to the boardbitmap
img_grass = pyglet.resource.image('grass.png')
img_route = pyglet.resource.image('route.png')

# calculate field pixel resolution
HORIZ_RES = 5 * img_grass.width
VERT_RES = 5 * img_grass.height
# calculate lenght in pixels of units in game
VERT_UNIT = VERT_RES // 100
HORIZ_UNIT = HORIZ_RES // 100

DAMAGE_LIMIT = 80

# load tower image
img_tower = pyglet.resource.image('tower.png')
img_tower.anchor_x = img_tower.width // 2
img_tower.anchor_y = img_tower.height // 2 - 11

img_deaths = []
for n in range(3):
    img = pyglet.resource.image('death{}.png'.format(n))
    img.anchor_x = img.width // 2
    img.anchor_y = img.height // 2
    img_deaths.append(img)

# creates a dict of images of monsters
IMG_MONSTERS = {}
for filename in glob.glob("media/images/monster*.png"):
    filename = os.path.split(filename)[1]
    name_file = os.path.splitext(filename)[0]

    attribs = name_file.split('-')
    attribs.remove('monster')
    attribs.sort()
    key = ''.join([k[0] for k in attribs])
    img_monster = pyglet.resource.image(filename)
    img_monster.anchor_x = img_monster.width // 2
    img_monster.anchor_y = img_monster.height // 2
    IMG_MONSTERS[key] = img_monster

game_window = None


class Drawables():
    """Store the objects on the screen."""
    board = []
    towers = []
    monsters = []
    death_monsters = []
    score = 0
    shooting_info = []

_drawables = Drawables()


def draw_field(board, towers):
    """Draw the board and towers."""
    global game_window

    _drawables.board = board
    _drawables.towers = towers
    game_window = pyglet.window.Window(HORIZ_RES, VERT_RES)

    game_window.push_handlers(on_draw)
    game_window.push_handlers(on_close)
    _refresh()


def draw(monsters, death_monsters, score, shooting_info):
    """Draw dynamic objecs: monsters and score."""
    _drawables.monsters = monsters
    for m in death_monsters:
        _drawables.death_monsters.append([m.position, 6])
    _drawables.score = score
    _drawables.shooting_info = shooting_info
    _refresh()


def on_close():
    game_window.has_exit = True
    game_window.close()


def on_draw():
    _paint_background()
    pyglet.gl.glLineWidth(2)

    for tower in _drawables.towers:
        sprite = _paint_sprite(img_tower, tower.position)
        label = pyglet.text.Label(
            str(tower.__class__.__name__),
            font_name='Times New Roman',
            font_size=11,
            x=sprite.x, y=sprite.y - img_tower.anchor_y,
            anchor_x='left', anchor_y='top')
        label.draw()

    for monster in _drawables.death_monsters:
        if monster[1]:
            img_death_idx = (monster[1] - 1) // 2
            img_death = img_deaths[img_death_idx]
            sprite = _paint_sprite(img_death, monster[0])
            monster[1] -= 1

    for monster in _drawables.monsters:
        key = ''
        if monster.life < DAMAGE_LIMIT:
            key += 'd'  # damaged
        if monster.freeze:
            key += 'f'
        if monster.poison:
            key += 'p'
        if monster.rage:
            key += 'r'

        sprite = _paint_sprite(IMG_MONSTERS[key], monster.position)

    label = pyglet.text.Label(
        'Score:' + str(_drawables.score),
        font_name='Times New Roman',
        font_size=16,
        x=game_window.width - 5, y=game_window.height - 5,
        anchor_x='right', anchor_y='top')
    label.draw()

    for tower, monsters in _drawables.shooting_info:
        tow_x = tower.position[0] * HORIZ_UNIT
        tow_y = VERT_RES - tower.position[1] * VERT_UNIT

        if monsters:
            for monster in monsters:
                mon_x = monster.position[0] * HORIZ_UNIT
                mon_y = VERT_RES - monster.position[1] * VERT_UNIT

                pyglet.graphics.draw(
                    2, pyglet.gl.GL_LINES,
                    ("v2i", (tow_x, tow_y, mon_x, mon_y)),
                    ("c4B", (255, 0, 0, 255) * 2),
                )


def _paint_background():
    for row, line in enumerate(_drawables.board):
        for col, value in enumerate(line):
            if value == 'G':
                image = img_grass
            else:
                image = img_route
            x = col * image.width
            y = VERT_RES - (row + 1) * image.height
            image.blit(x, y)


def _paint_sprite(img, pos):
    x = pos[0] * HORIZ_UNIT
    y = VERT_RES - pos[1] * VERT_UNIT
    sprite = pyglet.sprite.Sprite(img, x=x, y=y)
    sprite.draw()
    return sprite


def _refresh():
    pyglet.clock.tick()
    if not game_window.has_exit:
        game_window.dispatch_events()
        game_window.dispatch_event('on_draw')
        game_window.flip()
    else:
        sys.exit()
