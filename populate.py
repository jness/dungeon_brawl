#!/usr/bin/env python3

import glob
import json
import yaml

from pymongo import MongoClient


# create our Mongo connection
mongo = MongoClient('mongo', username='root', password='password')

# connect to collection within our database
database = mongo.dungeon_brawl

# get a list of existing collections
collections = database.collection_names()

# iterate over all monster files
if 'monsters' not in collections:

    # link to our collections
    monsters = database.monsters

    for file_path in sorted(glob.glob('monsters/*.yaml')):
        with open(file_path) as f:

            # load json file into python dictionary
            document = yaml.load(f.read())

            # check if document exists in mongo
            slug_name = document['slug_name']
            if monsters.find_one({'slug_name': slug_name}):
                print('Document %s already exists' % slug_name)
                continue

            # import monster into mongo
            print('Inserting %s into monsters collection' % slug_name)
            monsters.insert_one(document)

# iterate over all spells files
if 'spells' not in collections:

    # link to our collections
    spells = database.spells

    for file_path in sorted(glob.glob('spells/*.yaml')):
        with open(file_path) as f:

            # load json file into python dictionary
            document = yaml.load(f.read())

            # check if document exists in mongo
            slug_name = document['slug_name']
            if spells.find_one({'slug_name': slug_name}):
                print('Document %s already exists' % slug_name)
                continue

            # import monster into mongo
            print('Inserting %s into spells collection' % slug_name)
            spells.insert_one(document)

# iterate over all condition files
if 'conditions' not in collections:

    # link to our collections
    conditions = database.conditions

    for file_path in sorted(glob.glob('conditions/*.yaml')):
        with open(file_path) as f:

            # load json file into python dictionary
            document = yaml.load(f.read())

            # check if document exists in mongo
            slug_name = document['slug_name']
            if conditions.find_one({'slug_name': slug_name}):
                print('Document %s already exists' % slug_name)
                continue

            # import monster into mongo
            print('Inserting %s into conditions collection' % slug_name)
            conditions.insert_one(document)
