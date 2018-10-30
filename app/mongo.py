from pymongo import MongoClient

from exceptions import NoMonster, NoEncounter


# create our Mongo connection
mongo = MongoClient('mongo', username='root', password='password')

# connect to collections within our database
database = mongo.dungeon_brawl


def find(collection_name, **kwargs):
    """
    Perform a mongo search operation
    """

    collection = getattr(database, collection_name)
    return collection.find(kwargs)


def find_one(collection_name, **kwargs):
    """
    Perform a mongo search operation for one document
    """

    collection = getattr(database, collection_name)
    return collection.find_one(kwargs)


def full_text(collection_name, text):
    """
    Perform a mongo full text search
    """

    # fields to perform regex search against
    fields = ['name', 'alignment', 'type', 'size', 'school']

    # empty mongo or query
    kwargs = {'$or': []}

    # populate mongo or query with all fields
    for field in fields:
        kwargs['$or'].append(
            {
                field: {
                    '$regex': text,
                    '$options': 'i'
                }
            }
        )

    return find(collection_name, **kwargs)


def count(collection_name, **kwargs):
    """
    Get document count from collection
    """

    collection = getattr(database, collection_name)
    return collection.count_documents(kwargs)


def find_monsters(**kwargs):
    """
    Get all monsters with optional keyword arguments
    """

    return find('monsters', **kwargs)


def find_random_monster(min_cr=None, max_cr=None):
    """
    Find a random monster
    """

    filters = [
        {'$sample': {'size': 1}}
    ]

    if min_cr:
        query = {'$match': {'challenge_rating': {"$gte": float(min_cr)}}}
        filters.insert(0, query)

    if max_cr:
        query = {'$match': {'challenge_rating': {"$lte": float(max_cr)}}}
        filters.insert(0, query)

    collection = getattr(database, 'monsters')
    monster = collection.aggregate(filters)

    # get our single monster
    try:
        return monster.next()
    except StopIteration:
        raise NoMonster('No monster with challage rating found')


def find_monsters_with_spell(slug_name):
    """
    Get all monsters with spell
    """

    kwargs = {
        'spell_casting.spell_list.spells': {
            '$elemMatch': {'slug_name': slug_name}
        }
    }

    return find('monsters', **kwargs)


def find_spells(**kwargs):
    """
    Get all spell with optional keyword arguments
    """

    return find('spells', **kwargs)


def find_conditions(**kwargs):
    """
    Get all conditions with optional keyword arguments
    """

    return find('conditions', **kwargs)


def find_encounters(**kwargs):
    """
    Get all encounters with optional keyword arguments
    """

    return find('encounters', **kwargs)


def find_challenge_ratings():
    """
    Get a distinct challenge ratings
    """

    collection = getattr(database, 'monsters')
    return sorted(collection.distinct("challenge_rating"))


def find_random_encounter():
    """
    Find a random encounter
    """

    filters = [
        {'$sample': {'size': 1}}
    ]

    collection = getattr(database, 'encounters')
    encounter = collection.aggregate(filters)

    # get our single monster
    try:
        return encounter.next()
    except StopIteration:
        raise NoEncounter('No encounter with challage rating found')
