import json

from flask import url_for, redirect


# https://stackoverflow.com/questions/3290424/set-a-cookie-to-never-expire
# Make cookie as persistent as possible,
# this keeps the brawl around even if browser is closed
cookie_age = 2147483647


def get_brawl_cookie(request):
    """
    Get brawl cookie
    """

    return json.loads(request.cookies.get('brawl') or '[]')


def set_brawl_cookie(payload):
    """
    Set brawl cookie with payload
    """

    # new redirect response to brawl page
    response = redirect(url_for('brawl'))

    # set cookie for monsters
    response.set_cookie('brawl', json.dumps(payload), max_age=cookie_age)

    # return response object
    return response


def clear_brawl_cookie():
    """
    Clear brawl cookie
    """

    # new redirect response to brawl page
    response = redirect(url_for('brawl'))

    # set the monsters and monster_counter cookie to expire
    response.set_cookie('brawl', expires=0)

    # return the response object
    return response
