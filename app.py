#!/usr/bin/env python3

import re

from pymongo import MongoClient
from flask import Flask, render_template, request

# create our Flask application
app = Flask(__name__)

# create our Mongo connection
mongo = MongoClient('mongo', username='root', password='password')

# connect to collection within our database
database = mongo.dungeon_brawl
collection = database.monsters

@app.route('/', methods=['GET'])
def search():
    """
    Main search page
    """

    return render_template('search.html')


@app.route('/search', methods=['POST'])
def monsters():
    """
    Return search results
    """

    if 'name' in request.form:

        # create a case insensitive regex for compare
        regx = re.compile(request.form['name'], re.IGNORECASE)

        # find monsters matching regex
        results = collection.find({'name': regx})

        # render our template with results
        return render_template('monsters.html', monsters=results)


@app.route('/monster/<name>', methods=['GET'])
def monster(name):
    """
    Return a monster by name
    """

    # find monsters matching regex
    results = collection.find_one({'name': name})

    if results:
        return render_template('monster.html', monster=results)

    return 'Monster not found'


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
