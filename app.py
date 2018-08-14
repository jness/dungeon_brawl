#!/usr/bin/env python3

import re
import json
import random

from pymongo import MongoClient
from flask import Flask, render_template, request, abort, redirect, make_response

# create our Flask application
app = Flask(__name__)

# create our Mongo connection
mongo = MongoClient('mongo', username='root', password='password')

# connect to collection within our database
database = mongo.dungeon_brawl
collection = database.monsters

@app.route('/', methods=['GET'])
def main():
    """
    Main page
    """

    # get all monsters
    results = collection.find({})

    # perform column sort
    if 'sort' in request.args:
        results = results.sort(request.args['sort'])

    return render_template('monsters.html', monsters=results)


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
            results = collection.find({search_field: search_text})
        else:
            regex = re.compile(search_text, re.IGNORECASE)
            results = collection.find({search_field: regex})

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
    results = collection.find_one({'slug_name': slug_name})

    if results:
        return render_template('monster.html', monster=results)

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
        monster = collection.find_one({'slug_name': slug_name})
        if monster:

            # add monster to monster json list
            monsters.append(
                dict(
                    unique_id = '%s_%s' % (monster['name'], len(monsters) + 1),
                    name = monster['name'],
                    slug_name = monster['slug_name'],
                    hit_points = monster['hit_points'],
                    dexterity_modifier = monster['dexterity_modifier']
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
    hit_points = request.form['hit_points']

    # add monster to monster json list
    monsters.append(
        dict(
            unique_id = '%s_%s' % (name, len(monsters) + 1),
            name = name,
            hit_points = hit_points,
            dexterity_modifier = initiative_modifier
        )
    )

    # redirect to brawl page and set monster to cookie
    response = redirect('/brawl')
    response.set_cookie('monsters', json.dumps(monsters))
    return response


@app.route('/brawl_clear', methods=['GET'])
def brawl_clear():
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
        roll = random.randint(1, 20)
        roll_result = eval('%s%s' % (roll, monster['dexterity_modifier']))
        monster['initiative'] = roll_result

    return render_template(
        'brawl.html', monsters=sorted(
            monsters, key=lambda x:x['initiative'], reverse=True))


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
