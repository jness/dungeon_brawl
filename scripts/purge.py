#!/usr/bin/env python3

import sys

from pymongo import MongoClient


# create our Mongo connection
mongo = MongoClient('mongo', username='root', password='password')

# connect to collection within our database
database = mongo.dungeon_brawl


try:

    # if argv was passed delete single collection
    collection_name = sys.argv[1]

    print('Dropping collection %s' % collection_name)
    c = getattr(database, collection_name)
    c.drop()

except IndexError:

    # get a list of existing collections
    collections = database.list_collection_names()

    # drop each collection in the dungeon_brawl database
    for collection in collections:

        print('Dropping collection %s' % collection)
        c = getattr(database, collection)
        c.drop()
