#!/usr/bin/env python3

import re
import json
import yaml
import random
from fractions import Fraction

from slugify import slugify
from pymongo import MongoClient
from flask import (
    Flask, render_template, request, abort, redirect, url_for, make_response)


# create our Flask application
app = Flask(__name__)

# https://stackoverflow.com/questions/3290424/set-a-cookie-to-never-expire
# Make cookie as persistent as possible,
# this keeps the brawl around even if browser is closed
cookie_age = 2147483647

# create our Mongo connection
mongo = MongoClient('mongo', username='root', password='password')

# connect to collections within our database
database = mongo.dungeon_brawl
monster_collection = database.monsters
spell_collection = database.spells
condition_collection = database.conditions
encounter_collection = database.encounters


# add a few Jinja filters
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


@app.template_filter('enable_encounters')
def enable_encounters(_):
    """
    Check if encounters are enabled
    """

    # get a list of existing collections
    collections = database.collection_names()

    # iterate over all monster files
    if 'encounters' in collections:
        return True
    return False


# add web endpoints
@app.route('/', methods=['GET'])
def monsters():
    """
    List all monsters
    """

    # get all monsters
    results = monster_collection.find({})

    # perform column sort
    if 'sort' in request.args:
        results = results.sort(request.args['sort'])

    return render_template('monsters.html', monsters=results)


@app.route('/monster_search', methods=['GET'])
def monster_search():
    """
    List filtered monsters
    """

    # required url params for search
    search_text = request.args.get('search_text', 'zombie')
    search_field = request.args.get('search_field', 'name')

    # certian fields should not be searched with regex
    non_regex = ['challenge_rating']

    # perform a non regex search
    if search_field in non_regex:
        results = monster_collection.find({search_field: search_text})

    # perform a regex search
    else:
        regex = re.compile(search_text, re.IGNORECASE)
        results = monster_collection.find({search_field: regex})

    # sort if url param passed
    if 'sort' in request.args:
        results = results.sort(request.args['sort'])

    # render our template with results
    return render_template(
        'monsters.html',
        search_text=search_text,
        search_field=search_field,
        monsters=results
    )


@app.route('/monster/<slug_name>', methods=['GET'])
def monster(slug_name):
    """
    Return a monster by name
    """

    # find monsters by slug_name
    results = monster_collection.find_one({'slug_name': slug_name})

    # if we have a result render monster
    if results:
        return render_template('monster.html', monster=results)

    # if we do not have a result render error
    return render_template('error.html',
        message='Monster %s not found' % slug_name), 404


@app.route('/spells', methods=['GET'])
def spells():
    """
    Main spell page
    """

    # get all monsters
    results = spell_collection.find({})

    # perform column sort
    if 'sort' in request.args:
        results = results.sort(request.args['sort'])

    return render_template('spells.html', spells=results)


@app.route('/spell_search', methods=['GET'])
def spell_search():
    """
    List filtered monsters
    """

    # required url params for search
    search_text = request.args.get('search_text', 'cure')
    search_field = request.args.get('search_field', 'name')

    # perform a regex search
    regex = re.compile(search_text, re.IGNORECASE)
    results = spell_collection.find({search_field: regex})

    # sort if url param passed
    if 'sort' in request.args:
        results = results.sort(request.args['sort'])

    # render our template with results
    return render_template(
        'spells.html',
        search_text=search_text,
        search_field=search_field,
        spells=results
    )


@app.route('/spell/<slug_name>', methods=['GET'])
def spell(slug_name):
    """
    Return a spell by name
    """

    # find spell by slug_name
    results = spell_collection.find_one({'slug_name': slug_name})

    # if we have a result render spell
    if results:

        # get list of monsters with spell
        monsters = monster_collection.find(
            {'spell_casting.spell_list.spells': {
                '$elemMatch': { 'slug_name': results['slug_name'] }
                }
            }
        )

        return render_template('spell.html', spell=results, monsters=monsters)

    # if we do not have a result render error
    return render_template('error.html',
        message='Spell %s not found' % slug_name), 404


@app.route('/conditions', methods=['GET'])
def conditions():
    """
    List all conditions
    """

    # get all monsters
    results = condition_collection.find({})

    return render_template('conditions.html', conditions=results)


@app.route('/condition_search', methods=['GET'])
def condition_search():
    """
    List filtered conditions
    """

    # required url params for search
    search_text = request.args.get('search_text', 'blind')

    # perform a regex search
    regex = re.compile(search_text, re.IGNORECASE)
    results = condition_collection.find({'name': regex})

    # render our template with results
    return render_template(
        'conditions.html',
        search_text=search_text,
        conditions=results
    )


@app.route('/condition/<slug_name>', methods=['GET'])
def condition(slug_name):
    """
    Return a condition by name
    """

    # find monsters by slug_name
    results = condition_collection.find_one({'slug_name': slug_name})

    # if we have a result render monster
    if results:
        return render_template('condition.html', condition=results)

    # if we do not have a result render error
    return render_template('error.html',
        message='Condition %s not found' % slug_name), 404


@app.route('/brawl', methods=['GET'])
def brawl():
    """
    Show brawl
    """

    # load monsters from cookie
    monsters = json.loads(request.cookies.get('monsters') or '[]')

    # render brawl
    return render_template('brawl.html', monsters=monsters)


@app.route('/brawl_reset', methods=['GET'])
def brawl_reset():
    """
    Clear monsters from brawl
    """

    # load monsters from cookie
    monsters = json.loads(request.cookies.get('monsters') or '[]')

    # fetch non monsters from cookie
    monsters = [m for m in monsters if m['is_character'] == True]

    # reset initiative
    new_monsters = []
    for monster in monsters:
        if 'initiative' in monster:
            del(monster['initiative'])
        new_monsters.append(monster)

    # create redirect to brawl page
    response = redirect(url_for('brawl'))

    # set cookie to non monsters (characters only)
    response.set_cookie(
        'monsters', json.dumps(new_monsters), max_age=cookie_age)
    return response


@app.route('/brawl_clear', methods=['GET'])
def brawl_clear():
    """
    Clear all from brawl
    """

    # create redirect to brawl page
    response = redirect(url_for('brawl'))

    # expire the monsters cookie (deletes the cookie)
    response.set_cookie('monsters', expires=0)
    return response


@app.route('/brawl_add_monster', methods=['GET'])
def brawl_add_monster():
    """
    Add monster to brawl
    """

    # load monsters from cookie
    monsters = json.loads(request.cookies.get('monsters') or '[]')

    # required url params for search
    slug_name = request.args['slug_name']
    quantity = int(request.args.get('quantity', 1))

    # max and min our quantity
    if quantity < 1:
        quantity = 1
    elif quantity >5:
        quantity = 5

    # perform a search
    monster = monster_collection.find_one({'slug_name': slug_name})

    # if we have a result render monster
    if monster:

        # handle multiple monsters
        for _ in range(quantity):

            # add counter to monster name for easy tracking
            name = '%s (%s)' % (monster['name'], len(monsters) + 1)

            # create a slim monster object to store in cookie
            slim_monster = {
                'unique_id': '%s_%s' % (monster['slug_name'], len(monsters) + 1),
                'name': name,
                'slug_name': monster['slug_name'],
                'armor_class': monster['armor_class'],
                'hit_points': monster['hit_points'],
                'dexterity_modifier': get_ability_modifier(monster['dexterity']),
                'is_character': False,
                'notes': '',
                'conditions': []
            }

            # add slim_monster to monsters list
            monsters.append(
                slim_monster
            )

        # create redirect to brawl page
        response = redirect(url_for('brawl'))

        # set cookie for monsters
        response.set_cookie('monsters', json.dumps(monsters), max_age=cookie_age)
        return response

    # if we do not have a result render error
    return render_template('error.html',
        message='Monster %s not found' % slug_name), 404


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

    # load monsters from cookie
    monsters = json.loads(request.cookies.get('monsters') or '[]')

    # if - or + operator not added to initiative, set it positive modifier
    if not re.search('^[\-|\+]', initiative_modifier):
        initiative_modifier = '+%s' % int(initiative_modifier)

    # create a slim character object to store in cookie
    slim_character = {
        'unique_id': '%s_%s' % (slugify(name), len(monsters) + 1),
        'name': name,
        'slug_name': slugify(name),
        'armor_class': armor_class,
        'hit_points': hit_points,
        'dexterity_modifier': initiative_modifier,
        'is_character': True,
        'notes': '',
        'conditions': []
    }

    # add slim_character to monsters list
    monsters.append(
        slim_character
    )

    # create redirect to brawl page
    response = redirect(url_for('brawl'))

    # set cookie for monsters
    response.set_cookie('monsters', json.dumps(monsters), max_age=cookie_age)
    return response


@app.route('/brawl_add_random_monster', methods=['GET', 'POST'])
def brawl_add_random_monster():
    """
    Add random monster to brawl
    """

    if request.method == 'POST':
        # grab required form elements from POST
        cr = request.form['cr']
        quantity = int(request.form['quantity'])

    elif request.method == 'GET':
        # grab required url params
        cr = request.args['cr']
        quantity = int(request.args.get('quantity', 1))

    # max and min our quantity
    if quantity < 1:
        quantity = 1
    elif quantity >5:
        quantity = 5

    # load monsters from cookie
    monsters = json.loads(request.cookies.get('monsters') or '[]')

    for _ in range(quantity):

        # perform a random search of size 1
        _monster = monster_collection.aggregate(
            [
                { '$match': { 'challenge_rating': float(cr) } },
                { '$sample': { 'size': 1 } }
            ]
        )

        # get our single monster
        monster = _monster.next()

        # add counter to monster name for easy tracking
        name = '%s (%s)' % (monster['name'], len(monsters) + 1)

        # create a slim monster object to store in cookie
        slim_monster = {
            'unique_id': '%s_%s' % (monster['slug_name'], len(monsters) + 1),
            'name': name,
            'slug_name': monster['slug_name'],
            'armor_class': monster['armor_class'],
            'hit_points': monster['hit_points'],
            'dexterity_modifier': get_ability_modifier(monster['dexterity']),
            'is_character': False,
            'notes': '',
            'conditions': []
        }

        # add slim_character to monsters list
        monsters.append(
            slim_monster
        )

    # create redirect to brawl page
    response = redirect(url_for('brawl'))

    # set cookie for monsters
    response.set_cookie('monsters', json.dumps(monsters), max_age=cookie_age)
    return response


@app.route('/brawl_roll_initiative', methods=['GET'])
def brawl_roll_initiative():
    """
    Roll initiative for brawl
    """

    # load monsters from cookie
    monsters = json.loads(request.cookies.get('monsters') or '[]')

    # iterate over all monsters
    for monster in monsters:

        # if monster doesn't already have a initative roll it now
        if 'initiative' not in monster:

            # roll a d20 and get results
            roll = random.randint(1, 20)

            # add d20 results to monsters modifier
            roll_result = eval('%s%s' % (roll, monster['dexterity_modifier']))

            # set initiative to modifiered d20 roll
            monster['initiative'] = roll_result

    # sort monsters in initative order
    monsters = sorted(
        monsters, key=lambda x:x.get('initiative', -99), reverse=True)

    # create redirect to brawl page
    response = redirect(url_for('brawl'))

    # set cookie for monsters
    response.set_cookie('monsters', json.dumps(monsters), max_age=cookie_age)
    return response



@app.route('/brawl_update_monster', methods=['POST'])
def brawl_update_monster():
    """
    Update a monsters stats
    """

    # grab required form elements from POST
    unique_id = request.form['unique_id']
    initiative = int(request.form['initiative'])
    armor_class = int(request.form['armor_class'])
    hit_points = request.form['hit_points']
    notes = request.form.get('notes') or ''

    # create list of all conditions
    conditions = [
        'blinded',
        'charmed',
        'deafened',
        'fatigued',
        'frightened',
        'grappled',
        'incapacitated',
        'invisible',
        'paralyzed',
        'petrified',
        'poisoned',
        'prone',
        'restrained',
        'stunned',
        'unconscious',
        'exhaustion'
    ]

    # load monsters from cookie
    monsters = json.loads(request.cookies.get('monsters') or '[]')

    # iterate over all monsters
    for monster in monsters:

        # if our monster matches unique_id this is the monster
        # we plan to update
        if monster['unique_id'] == unique_id:

            # if posted hit_points starts with a + operator
            # we should increase current hits
            if re.search('^\+', hit_points):
                hit_points = int(monster['hit_points']) + int(hit_points)

            # if posted hit_points starts with a - operator
            # we should decrease current hits
            elif re.search('^\-', hit_points):
                hit_points = int(monster['hit_points']) + int(hit_points)

            # else if hit points is a number we should set hits points
            else:
                hit_points = int(hit_points)

            # set our initative, hit_points, and notes
            monster['initiative'] = int(initiative)
            monster['armor_class'] = int(armor_class)
            monster['hit_points'] = int(hit_points)
            monster['notes'] = notes

            # add conditions
            monster['conditions'] = []
            for condition in conditions:
                if condition in request.form:
                    monster['conditions'].append(condition)

    # sort monsters in initative order
    monsters = sorted(
        monsters, key=lambda x:x.get('initiative', -99), reverse=True)

    # create redirect to brawl page
    response = redirect(url_for('brawl'))

    # set cookie for monsters
    response.set_cookie('monsters', json.dumps(monsters), max_age=cookie_age)
    return response


@app.route('/brawl_remove_monster', methods=['GET'])
def brawl_remove_monster():
    """
    Remove monster from brawl
    """

    # grab required form elements from POST
    unique_id = request.args['unique_id']

    # load monsters from cookie
    monsters = json.loads(request.cookies.get('monsters') or '[]')

    # create a new list to holder expected monsters
    new_monsters = []

    # iterate over all monsters
    for monster in monsters:

        # if monster's unique_id should not be deleted
        # add it to new monster list
        if monster['unique_id'] != unique_id:
            new_monsters.append(monster)

    # create redirect to brawl page
    response = redirect(url_for('brawl'))

    # set cookie for monsters to new monster list
    response.set_cookie('monsters', json.dumps(new_monsters), max_age=cookie_age)
    return response


@app.route('/brawl_set_turn', methods=['POST'])
def brawl_set_turn():
    """
    Set monsters turn
    """

    # grab required form elements from POST
    unique_id = request.form['unique_id']

    # load monsters from cookie
    monsters = json.loads(request.cookies.get('monsters') or '[]')

    # iterate over all monsters
    for monster in monsters:

        # if monster's unique_id matches set to his turn,
        # else not it's turn
        if monster['unique_id'] == unique_id:
            monster['my_turn'] = True
        else:
            monster['my_turn'] = False

    # create redirect to brawl page
    response = redirect(url_for('brawl'))

    # set cookie for monsters to new monster list
    response.set_cookie('monsters', json.dumps(monsters), max_age=cookie_age)
    return response


@app.route('/encounter', methods=['GET'])
def encounter():
    """
    Get random encounter
    """

    # perform a random search of size 1
    _encounter = encounter_collection.aggregate(
        [
            { '$sample': { 'size': 1 } }
        ]
    )

    # fetch single encounter
    encounter = _encounter.next()

    # render our template with results
    return render_template(
        'encounter.html',
        encounter=encounter
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
