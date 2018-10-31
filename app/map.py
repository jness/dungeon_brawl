from io import BytesIO
from random import randint

from flask import send_file
from PIL import Image


def get_positions():
    """
    Get positions for our 450x450 map
    """

    positions = [ i + 3 for i in list(range(0, 450, 75)) ]
    return sorted([ (x, y) for y in positions for x in positions ])


def draw(identifiers, static_folder):
    """
    Draw map for our identifiers
    """

    # get positions and load background
    positions = get_positions()
    background = Image.open('%s/images/map.png' % static_folder)

    for identifier in identifiers:

        # load token image
        token = Image.open('%s/images/%s_token.png' % (static_folder, identifier))

        # get a random positions
        position_id = randint(0, len(positions) - 1)
        position = positions[position_id]
        del(positions[position_id])

        # add token to position
        background.paste(token, position, mask=token)

    # save image using StringIO and Flask send_file
    # http://flask.pocoo.org/snippets/32/
    byte_io = BytesIO()
    background.save(byte_io, 'PNG', quality=70)
    byte_io.seek(0)
    return send_file(byte_io, mimetype='image/png')
