#!/usr/bin/env python3

import sys
import glob
import json
import yaml

from pymongo import MongoClient, TEXT


# first input should be module name
try:
    module = sys.argv[1]
except IndexError:
    print('%s must be called with a module name' % sys.argv[0])
    sys.exit(1)

# create our Mongo connection
mongo = MongoClient('mongo', username='root', password='password')

# connect to collection within our database
database = mongo.dungeon_brawl

# get a list of existing collections
collections = database.list_collection_names()

# get a list of module specific monsters
with open('modules/%s/monsters.yaml' % module) as f:
    module_monsters = yaml.load(f.read())


def populate(collection_name):
    """
    Populate a collection
    """

    # only populate if collection doesn't exists
    if collection_name not in collections:

        # link to our collection
        collection = getattr(database, collection_name)

        # module data lives in it's own directory
        if collection_name == 'encounters':
            path = 'modules/%s/encounters/*.yaml' % module
        else:
            path = 'data/%s/*.yaml' % collection_name

        # iterate over data files for collection name
        for file_path in sorted(glob.glob(path)):
            with open(file_path) as f:

                # load json file into python dictionary
                document = yaml.load(f.read())

                # if we are acting on monsters collection we need
                # to compare against our module specific monsters,
                # and skip monsters not referenced
                if collection_name == 'monsters':
                    if document['slug_name'] not in module_monsters:
                        continue

                # check if document already exists
                slug_name = document['slug_name']

                if collection.find_one({'slug_name': slug_name}):
                    print('Document %s already exists in collection %s' % (
                        slug_name, collection_name)
                    )
                    continue

                # import document into collection
                print('Inserting %s into collection %s' % (
                    slug_name, collection_name)
                )
                collection.insert_one(document)


def main():
    """
    Main function that calls populate on all the things
    """

    populate('monsters')
    populate('spells')
    populate('conditions')
    populate('encounters')
    populate('characters')
    populate('actions')


if __name__ == '__main__':
    main()
