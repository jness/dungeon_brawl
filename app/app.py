#!/usr/bin/env python3

import re
from fractions import Fraction

# 3rd party modules
from flask import (
    Flask, render_template, request, redirect, url_for
)

from flask_socketio import SocketIO, emit

# local modules
from exceptions import CookieLimit, NoMonster

from mongo import (
    find_monsters, find_spells, find_conditions, find_actions, find_one,
    find_monsters_with_spell, find_challenge_ratings, find_random_monster,
    full_text, count, find_random_encounter, find_environments,
    find_characters, save_brawl, get_brawl, clear_brawl
)

from brawl import (
    remove_monsters, remove_initative, add_monsters, add_character,
    roll_initiative, set_turn, remove_monster, get_conditions, update_monster,
    remove_turn
)


#
# create our Flask application
#

app = Flask(__name__)
app.config['SECRET_KEY'] = 'BRAWL!'
socketio = SocketIO(app)


# @socketio.on('my event')
# def socket_message(message):
#     print('Message sent')
#     emit('my response', {'data': message['data']})
#
#
# @socketio.on('connect')
# def socket_connect():
#     print('Client connected')
#
#
# @socketio.on('disconnect')
# def socket_disconnect():
#     print('Client disconnected')

#
# add a few custom jinja filters
#

@app.template_filter('get_ability_modifier')
def get_ability_modifier(stat):
    """
    Get ability modifier for a stat
    """

    # array of dnd ability modifiers
    modifiers = {
      "1": "-5", "2": "-4", "3": "-4", "4": "-3", "5": "-3", "6": "-2",
      "7": "-2", "8": "-1", "9": "-1", "10": "+0", "11": "+0", "12": "+1",
      "13": "+1", "14": "+2", "15": "+2", "16": "+3", "17": "+3", "18": "+4",
      "19": "+4", "20": "+5", "21": "+5", "22": "+6", "23": "+6", "24": "+7",
      "25": "+7", "26": "+8", "27": "+8", "28": "+9", "29": "+9", "30": "+10"
    }

    if str(stat) in modifiers:
        return modifiers[str(stat)]
    return '?'


@app.template_filter('get_challenge_fraction')
def get_challenge_fraction(cr):
    """
    Get challenge as fraction
    """

    return Fraction(cr)


#
# context processors runs on every request
#

@app.context_processor
def is_encounters_enabled():
    """
    Check if encounter need to be enabled
    """

    if count('encounters'):
        return dict(is_encounters_enabled=True)

    return dict(is_encounters_enabled=False)


@app.context_processor
def is_admin():
    """
    Check if user is admin
    """

    if '127.0.0.1' == request.host.split(':')[0]:
        return dict(admin=True)

    return dict(admin=False)

#
# all web routes
#

@app.route('/', methods=['GET'])
def monsters():
    """
    List all monsters
    """

    # get all monsters
    monsters = find_monsters()

    # perform column sort
    if 'sort' in request.args:
        monsters = monsters.sort(request.args['sort'])

    # render our template with results
    return render_template('monsters.html', monsters=monsters)


@app.route('/characters', methods=['GET'])
def characters():
    """
    List all characters
    """

    # get all monsters
    characters = find_characters()

    # perform column sort
    if 'sort' in request.args:
        characters = characters.sort(request.args['sort'])

    # render our template with results
    return render_template('characters.html', characters=characters)


@app.route('/monster_search', methods=['GET'])
def monster_search():
    """
    List filtered monsters
    """

    # required url params for search
    search_text = request.args.get('search_text')

    # perform search against all fields
    monsters = full_text('monsters', search_text)

    # # sort if url param passed
    if 'sort' in request.args:
        monsters = monsters.sort(request.args['sort'])

    # # render our template with results
    return render_template(
        'monsters.html',
        search_text=search_text,
        monsters=monsters
    )


@app.route('/monster/<slug_name>', methods=['GET'])
def monster(slug_name):
    """
    Return a monster by name
    """

    # find monsters by slug_name
    monster = find_one('monsters', slug_name=slug_name)

    # if we have a result render monster
    if monster:
        return render_template('monster.html', monster=monster)

    # if we do not have a result render error
    return render_template('error.html',
        message='Monster %s not found' % slug_name), 404


@app.route('/character/<slug_name>', methods=['GET'])
def character(slug_name):
    """
    Return a character by name
    """

    # find monsters by slug_name
    character = find_one('characters', slug_name=slug_name)

    # if we have a result render monster
    if character:
        return render_template('character.html', character=character)

    # if we do not have a result render error
    return render_template('error.html',
        message='Character %s not found' % slug_name), 404


@app.route('/raw_character/<slug_name>', methods=['GET'])
def raw_character(slug_name):
    """
    Return a raw character by name
    """

    # find monsters by slug_name
    character = find_one('characters', slug_name=slug_name)

    # if we have a result render monster
    if character:
        return render_template('raw_character.html', character=character)

    # if we do not have a result render error
    return render_template('error.html',
        message='Character %s not found' % slug_name), 404


@app.route('/spells', methods=['GET'])
def spells():
    """
    Main spell page
    """

    # perform mongo search
    spells = find_spells()

    # perform column sort
    if 'sort' in request.args:
        if request.args['sort'] == 'level':
            pass
        spells = spells.sort(request.args['sort'])

    # render our template with results
    return render_template('spells.html', spells=spells)


@app.route('/spell_search', methods=['GET'])
def spell_search():
    """
    List filtered monsters
    """

    # required url params for search
    search_text = request.args.get('search_text')

    # perform search against all fields
    spells = full_text('spells', search_text)

    # perform column sort
    if 'sort' in request.args:
        spells = spells.sort(request.args['sort'])

    # render our template with results
    return render_template(
        'spells.html',
        search_text=search_text,
        spells=spells
    )


@app.route('/spell/<slug_name>', methods=['GET'])
def spell(slug_name):
    """
    Return a spell by name
    """

    # find spell by slug_name
    spell = find_one('spells', slug_name=slug_name)

    # if we have a result render spell
    if spell:

        # get list of monsters with spell
        monsters = find_monsters_with_spell(slug_name)

        # render our template with results
        return render_template('spell.html', spell=spell, monsters=monsters)

    # if we do not have a result render error
    return render_template('error.html',
        message='Spell %s not found' % slug_name), 404


@app.route('/raw_spell/<slug_name>', methods=['GET'])
def raw_spell(slug_name):
    """
    Return a raw_spell by name
    """

    # find spell by slug_name
    spell = find_one('spells', slug_name=slug_name)

    # if we have a result render spell
    if spell:

        # get list of monsters with spell
        monsters = find_monsters_with_spell(slug_name)

        # render our template with results
        return render_template('raw_spell.html', spell=spell, monsters=monsters)

    # if we do not have a result render error
    return render_template('error.html',
        message='Spell %s not found' % slug_name), 404


@app.route('/conditions', methods=['GET'])
def conditions():
    """
    List all conditions
    """

    # get all conditions
    conditions = find_conditions()

    # render our template with results
    return render_template('conditions.html', conditions=conditions)


@app.route('/condition_search', methods=['GET'])
def condition_search():
    """
    List filtered conditions
    """

    # required url params for search
    search_text = request.args.get('search_text')

    # perform search against all fields
    conditions = full_text('conditions', search_text)

    # render our template with results
    return render_template(
        'conditions.html',
        search_text=search_text,
        conditions=conditions
    )


@app.route('/condition/<slug_name>', methods=['GET'])
def condition(slug_name):
    """
    Return a condition by name
    """

    # find condition by slug_name
    condition = find_one('conditions', slug_name=slug_name)

    # if we have a result render monster
    if condition:
        return render_template('condition.html', condition=condition)

    # if we do not have a result render error
    return render_template('error.html',
        message='Condition %s not found' % slug_name), 404


@app.route('/actions', methods=['GET'])
def actions():
    """
    List all actions
    """

    # get all actions
    actions = find_actions()

    # render our template with results
    return render_template('actions.html', actions=actions)


@app.route('/action_search', methods=['GET'])
def action_search():
    """
    List filtered actions
    """

    # required url params for search
    search_text = request.args.get('search_text')

    # perform search against all fields
    actions = full_text('actions', search_text)

    # render our template with results
    return render_template(
        'actions.html',
        search_text=search_text,
        actions=actions
    )


@app.route('/action/<slug_name>', methods=['GET'])
def action(slug_name):
    """
    Return a action by name
    """

    # find action by slug_name
    action = find_one('actions', slug_name=slug_name)

    # if we have a result render monster
    if action:
        return render_template('action.html', action=action)

    # if we do not have a result render error
    return render_template('error.html',
        message='Action %s not found' % slug_name), 404


@app.route('/brawl', methods=['GET'])
def brawl():
    """
    Show brawl
    """

    # load brawl from cookie
    brawl = get_brawl()

    # get list of monster challenge_ratings
    cr = find_challenge_ratings()

    # get list of environments
    environments = find_environments()

    # render brawl
    return render_template('brawl.html', brawl=brawl, challenge_rating=cr,
        environments=environments, async_mode=socketio.async_mode)


@app.route('/brawl_clear', methods=['GET'])
def brawl_clear():
    """
    Clear all from brawl
    """

    # clear our brawl cookie
    socketio.emit('my_response', {'data': 'State changed'})
    return clear_brawl()


@app.route('/brawl_reset', methods=['GET'])
def brawl_reset():
    """
    Clear monsters from brawl and reset initiative
    """

    # load brawl from cookie
    brawl = get_brawl()

    # remove monsters and initative from brawl
    brawl = remove_monsters(brawl)
    brawl = remove_initative(brawl)
    brawl = remove_turn(brawl)

    # render brawl
    socketio.emit('my_response', {'data': 'State changed'})
    return save_brawl(brawl)


@app.route('/brawl_add_monster', methods=['GET'])
def brawl_add_monster():
    """
    Add monster to brawl
    """

    # required url params
    slug_name = request.args['slug_name']
    quantity = int(request.args.get('quantity', 1))

    # load brawl from cookie
    brawl = get_brawl()

    # perform a search
    monster = find_one('monsters', slug_name=slug_name)

    # if we have a result render monster
    if monster:

        # handle multiple monsters
        try:
            brawl = add_monsters(brawl, monster, quantity)
        except CookieLimit:
            return render_template('error.html',
                message='Browser cookie do not support more monsters'), 409

        # render brawl
        socketio.emit('my_response', {'data': 'State changed'})
        return save_brawl(brawl)

    # if we do not have a result render error
    return render_template('error.html',
        message='Monster %s not found' % slug_name), 404


@app.route('/brawl_add_random_monster', methods=['GET', 'POST'])
def brawl_add_random_monster():
    """
    Add random monster to brawl
    """

    if request.method == 'POST':
        min_cr = request.form.get('min_cr')
        max_cr = request.form.get('max_cr')
        quantity = int(request.form.get('quantity', 1))
        environment = request.form.get('environment')

    elif request.method == 'GET':
        min_cr = request.args.get('min_cr')
        max_cr = request.args.get('max_cr')
        quantity = int(request.args.get('quantity', 1))
        environment = request.args.get('environment')

    # load brawl from cookie
    brawl = get_brawl()

    # handle multiple monsters
    for _ in range(quantity):

        # get a random monster
        try:
            monster = find_random_monster(min_cr, max_cr, environment)
        except NoMonster:
            return render_template('error.html',
                message='No monster with challage rating found'), 404

        # add monster to brawl
        try:
            brawl = add_monsters(brawl, monster, 1)
        except CookieLimit:
            return render_template('error.html',
                message='Browser cookie do not support more monsters'), 409

    # render brawl
    socketio.emit('my_response', {'data': 'State changed'})
    return save_brawl(brawl)


@app.route('/brawl_add_character', methods=['POST'])
def brawl_add_character():
    """
    Add character to brawl
    """

    # grab required form elements from POST
    name = request.form['name']
    initiative_modifier = request.form['initiative_modifier']
    armor_class = int(request.form['armor_class'])
    hit_points = int(request.form['hit_points'])

    # load brawl from cookie
    brawl = get_brawl()

    # if - or + operator not added to initiative, set it positive modifier
    if not re.search('^[\-|\+]', initiative_modifier):
        initiative_modifier = '+%s' % int(initiative_modifier)

    if 'url' in request.form:
        url = request.form['url']
    else:
        url = None

    # handle multiple monsters
    try:
        brawl = add_character(
            brawl, name, initiative_modifier, armor_class, hit_points, url)
    except CookieLimit:
        return render_template('error.html',
            message='Browser cookie do not support more monsters'), 409

    # render brawl
    socketio.emit('my_response', {'data': 'State changed'})
    return save_brawl(brawl)


@app.route('/brawl_roll_initiative', methods=['GET'])
def brawl_roll_initiative():
    """
    Roll initiative for brawl
    """

    # load brawl from cookie
    brawl = get_brawl()

    # roll initiaive
    brawl = roll_initiative(brawl)

    # render brawl
    socketio.emit('my_response', {'data': 'State changed'})
    return save_brawl(brawl)


@app.route('/brawl_update_monster', methods=['POST'])
def brawl_update_monster():
    """
    Update a monsters stats
    """

    # grab required form elements from POST
    name = request.form['name']
    color = request.form['color']
    identifier = request.form['identifier']
    armor_class = int(request.form['armor_class'])
    hit_points = request.form['hit_points']
    notes = request.form.get('notes') or ''
    conditions = [c for c in get_conditions() if c in request.form]

    # handle blank initiaive
    initiative = request.form['initiative']
    if initiative:
        initiative = int(initiative)

    # load brawl from cookie
    brawl = get_brawl()

    # update monster
    brawl = update_monster(
        name, brawl, identifier, initiative, armor_class, hit_points,
        notes, conditions, color)

    # render brawl
    socketio.emit('my_response', {'data': 'State changed'})
    return save_brawl(brawl)


@app.route('/brawl_remove_monster', methods=['GET'])
def brawl_remove_monster():
    """
    Remove monster from brawl
    """

    # grab required form elements from POST
    identifier = request.args['identifier']

    # load brawl from cookie
    brawl = get_brawl()

    # roll initiaive
    brawl = remove_monster(brawl, identifier)

    # render brawl
    socketio.emit('my_response', {'data': 'State changed'})
    return save_brawl(brawl)


@app.route('/brawl_set_turn', methods=['POST'])
def brawl_set_turn():
    """
    Set monsters turn
    """

    # grab required form elements from POST
    identifier = request.form['identifier']

    # load brawl from cookie
    brawl = get_brawl()

    # roll initiaive
    brawl = set_turn(brawl, identifier)

    # render brawl
    socketio.emit('my_response', {'data': 'State changed'})
    return save_brawl(brawl)


@app.route('/encounters', methods=['GET'])
def encounters():
    """
    Get random encounter
    """

    # get a random encounter
    try:
        encounter = find_random_encounter()
    except NoMonster:
        return render_template('error.html',
            message='No encounter found'), 404

    # build a redirect to random encounter
    response = redirect(url_for('encounter', slug_name=encounter['slug_name']))
    return response


@app.route('/encounter/<slug_name>', methods=['GET'])
def encounter(slug_name):
    """
    Get specific enounter
    """

    # find encounter by slug_name
    encounter = find_one('encounters', slug_name=slug_name)

    # if we have a result render encounter
    if encounter:
        return render_template('encounter.html', encounter=encounter)

    # if we do not have a result render error
    return render_template('error.html',
        message='Encounter %s not found' % slug_name), 404


if __name__ == "__main__":
    #app.run(host="0.0.0.0", debug=True)
    socketio.run(app, host="0.0.0.0", debug=True)
