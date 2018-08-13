#!/usr/bin/env python3

import re

from pymongo import MongoClient
from flask import Flask, render_template, request, abort, redirect

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
