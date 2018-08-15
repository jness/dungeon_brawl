#!/usr/bin/env python3

import re
import json
import random

from slugify import slugify
from pymongo import MongoClient
from flask import Flask, render_template, request, abort, redirect, make_response

# create our Flask application
app = Flask(__name__)

# create our Mongo connection
mongo = MongoClient('mongo', username='root', password='password')

# connect to collections within our database
database = mongo.dungeon_brawl
monster_collection = database.monsters
spell_collection = database.spells

@app.route('/', methods=['GET'])
def main():
    """
    Main page
    """

    # get all monsters
    results = monster_collection.find({})

    # perform column sort
    if 'sort' in request.args:
        results = results.sort(request.args['sort'])

    return render_template('monsters.html', monsters=results)


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


@app.route('/search', methods=['GET'])
def monsters():
    """
    Return search results
    """

    # if we have expected url params perform search
    if 'search_text' and 'search_field' in request.args:
        search_text = request.args['search_text']
        search_field = request.args['search_field']

        # only certian fields are allowed
        allowed_fields = [
            'name', 'type', 'size', 'alignment', 'challenge_rating'
        ]

        # if type is not an allowed fields return failure
        if search_field not in allowed_fields:
            abort(400)

        # perform search
        if search_field == 'challenge_rating':
            results = monster_collection.find({search_field: search_text})
        else:
            regex = re.compile(search_text, re.IGNORECASE)
            results = monster_collection.find({search_field: regex})

        # perform column sort
        if 'sort' in request.args:
            results = results.sort(request.args['sort'])

        # build extra url params
        params = '&search_text=%s&search_field=%s' % (search_text, search_field)

        # render our template with results
        return render_template('monsters.html', params=params, monsters=results)

    # if we didn't have expected url params we render search template
    return render_template('search.html')


@app.route('/monster/<slug_name>', methods=['GET'])
def monster(slug_name):
    """
    Return a monster by name
    """

    # find monsters matching regex
    results = monster_collection.find_one({'slug_name': slug_name})


    if results:
        return render_template(
            'monster.html', monster=results, spells=spells)

    abort(404)


@app.route('/spell/<slug_name>', methods=['GET'])
def spell(slug_name):
    """
    Return a spell by name
    """

    # find monsters matching regex
    results = spell_collection.find_one({'slug_name': slug_name})

    if results:
        return render_template('spell.html', spell=results)

    abort(404)


@app.route('/brawl_add', methods=['GET'])
def brawl_add():
    """
    Add monster to brawl
    """

    _monsters = request.cookies.get('monsters') or '[]'
    monsters = json.loads(_monsters)

    if 'slug_name' in request.args:
        slug_name = request.args['slug_name']

        # make sure the slug_name is in database
        monster = monster_collection.find_one({'slug_name': slug_name})
        if monster:

            # add monster to monster json list
            monsters.append(
                dict(
                    unique_id = '%s_%s' % (monster['slug_name'], len(monsters) + 1),
                    name = monster['name'],
                    slug_name = monster['slug_name'],
                    hit_points = monster['hit_points'],
                    dexterity_modifier = monster['dexterity_modifier'],
                    character = False,
                    notes = ''
                )
            )

            # redirect to brawl page and set monster to cookie
            response = redirect('/brawl')
            response.set_cookie('monsters', json.dumps(monsters))
            return response

    # if we didn't pass slug_name, or monster didn't exist
    abort(400)


@app.route('/brawl_add_character', methods=['POST'])
def brawl_add_character():
    """
    Add character to brawl
    """

    _monsters = request.cookies.get('monsters') or '[]'
    monsters = json.loads(_monsters)

    name = request.form['name']
    initiative_modifier = request.form['initiative_modifier']
    hit_points = int(request.form['hit_points'])

    if hit_points < 0:
        abort(400)

    if not re.search('^[\-|\+]', initiative_modifier):
        abort(400)

    # add monster to monster json list
    monsters.append(
        dict(
            unique_id = '%s_%s' % (slugify(name), len(monsters) + 1),
            name = name,
            hit_points = hit_points,
            dexterity_modifier = initiative_modifier,
            character = True,
            notes = ''
        )
    )

    # redirect to brawl page and set monster to cookie
    response = redirect('/brawl')
    response.set_cookie('monsters', json.dumps(monsters))
    return response


@app.route('/brawl_clear', methods=['GET'])
def brawl_clear_only_monsters():
    """
    Clear brawl
    """

    _monsters = request.cookies.get('monsters') or '[]'
    monsters = json.loads(_monsters)

    monsters = [m for m in monsters if m['character'] == True]

    # redirect to brawl page and set monster to cookie
    response = redirect('/brawl')
    response.set_cookie('monsters', json.dumps(monsters))
    return response


@app.route('/brawl_clear_all', methods=['GET'])
def brawl_clear_all():
    """
    Clear brawl
    """

    response = redirect('/brawl')
    response.set_cookie('monsters', expires=0)
    return response


@app.route('/brawl_roll', methods=['GET'])
def brawl_roll():
    """
    Roll init for brawl
    """

    _monsters = request.cookies.get('monsters') or '[]'
    monsters = json.loads(_monsters)

    for monster in monsters:

        if 'initiative' not in monster:
            roll = random.randint(1, 20)
            roll_result = eval('%s%s' % (roll, monster['dexterity_modifier']))
            monster['initiative'] = roll_result

    # sort monsters
    monsters = sorted(monsters, key=lambda x:x.get('initiative', 0), reverse=True)

    response = redirect('/brawl')
    response.set_cookie('monsters', json.dumps(monsters))
    return response



@app.route('/brawl_update', methods=['POST'])
def brawl_update():
    """
    Roll init for brawl
    """

    _monsters = request.cookies.get('monsters') or '[]'
    monsters = json.loads(_monsters)

    unique_id = request.form['unique_id']
    initiative = request.form['initiative']
    hit_points = request.form['hit_points']
    notes = request.form.get('notes') or ''

    for monster in monsters:

        if monster['unique_id'] == unique_id:

            # perform math on hit points
            if '+' in str(hit_points):
                hit_points = int(monster['hit_points']) + int(hit_points)
            elif '-' in str(hit_points):
                hit_points = int(monster['hit_points']) + int(hit_points)
            else:
                hit_points = int(hit_points)

            # cant go below 0
            if hit_points < 0:
                hit_points = 0

            monster['initiative'] = int(initiative)
            monster['hit_points'] = int(hit_points)
            monster['notes'] = notes

    # sort monsters
    monsters = sorted(monsters, key=lambda x:x.get('initiative', 0), reverse=True)

    response = redirect('/brawl')
    response.set_cookie('monsters', json.dumps(monsters))
    return response


@app.route('/brawl_delete', methods=['GET'])
def brawl_delete():
    """
    Roll init for brawl
    """

    unique_id = request.args['unique_id']

    _monsters = request.cookies.get('monsters') or '[]'
    monsters = json.loads(_monsters)

    new_monsters = []

    for monster in monsters:
        if monster['unique_id'] != unique_id:
            new_monsters.append(monster)

    response = redirect('/brawl')
    response.set_cookie('monsters', json.dumps(new_monsters))
    return response


@app.route('/brawl', methods=['GET'])
def brawl():
    """
    Show brawl
    """

    _monsters = request.cookies.get('monsters') or '[]'
    monsters = json.loads(_monsters)

    return render_template('brawl.html', monsters=monsters)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
