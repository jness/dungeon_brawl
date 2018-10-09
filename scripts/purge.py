#!/usr/bin/env python3

from pymongo import MongoClient


# create our Mongo connection
mongo = MongoClient('mongo', username='root', password='password')

# connect to collection within our database
database = mongo.dungeon_brawl

# get a list of existing collections
collections = database.list_collection_names()

# drop each collection in the dungeon_brawl database
for collection in collections:

    print('Dropping collection %s' % collection)
    c = getattr(database, collection)
    c.drop()
