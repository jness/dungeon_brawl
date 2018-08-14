#!/usr/bin/env python3

import glob
import json

from pymongo import MongoClient

# create our Mongo connection
mongo = MongoClient('mongo', username='root', password='password')

# connect to collection within our database
database = mongo.dungeon_brawl
collection = database.monsters

# iterate over all monster files
for file_path in sorted(glob.glob('monsters/*.json')):
    with open(file_path) as f:

        # load json file into python dictionary
        document = json.loads(f.read())

        # check if document exists in mongo
        slug_name = document['slug_name']
        if collection.find_one({'slug_name': slug_name}):
            print('Document %s already exists' % slug_name)
            continue

        # import monster into mongo
        print('Inserting %s' % slug_name)
        collection.insert_one(document)
