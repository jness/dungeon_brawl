import re
from random import randint
from string import ascii_uppercase

from slugify import slugify

from exceptions import CookieLimit


def remove_monsters(brawl):
    """
    Remove monsters from brawl, leaving only charaters
    """

    # fetch only characters from monster list
    monsters = [m for m in brawl if m['is_character']]

    # update brawl's monster list
    brawl = monsters

    # return modified brawl
    return brawl


def remove_initative(brawl):
    """
    Removes initative from brawl
    """

    # remove the initative key from monsters
    monsters = [
        {k: v for k, v in m.items()
            if k not in {'initiative'}} for m in brawl
    ]

    # update brawl's monster list
    brawl = monsters

    # return modified brawl
    return brawl


def get_next_monster_identifier(brawl):
    """
    Get next identifier from brawl
    """

    # get a list of upper case letters for identifiers
    identifiers = list(ascii_uppercase)

    # iterate over all monsters removing their identifier from list
    for monster in brawl:
        try:
            identifiers.remove(monster['identifier'])
        except ValueError:
            pass

    # return the left most remaining identifier
    return identifiers[0]


def get_next_character_identifier(brawl):
    """
    Get next identifier from brawl
    """

    # get a list of upper case letters for identifiers
    identifiers = list(range(1, 10))

    # iterate over all monsters removing their identifier from list
    for monster in brawl:
        try:
            identifiers.remove(monster['identifier'])
        except ValueError:
            pass

    # return the left most remaining identifier
    return identifiers[0]


def add_monsters(brawl, monster, quantity):
    """
    Add monsters to brawl
    """

    # limit brawl size
    if len(brawl) + quantity > 10:
        raise CookieLimit('Browser cookie do not support more monsters')

    # need to import within function....
    from app import get_ability_modifier

    # handle multiple monsters
    for _ in range(quantity):

        # get a unique identifier for monster
        identifier = get_next_monster_identifier(brawl)

        # to keep cookie small, and allow modifications we create a
        # slim representation of our monster object
        slim_monster = {
            'identifier': identifier,
            'name': '%s (%s)' % (monster['name'], identifier),
            'slug_name': monster['slug_name'],
            'armor_class': monster['armor_class'],
            'hit_points': monster['hit_points'],
            'dexterity_modifier': get_ability_modifier(monster['dexterity']),
            'is_character': False,
            'notes': '',
            'conditions': []
        }

        # append monster to brawl
        brawl.append(slim_monster)

    # return modified brawl
    return brawl


def add_character(brawl, name, initiative_modifier, armor_class, hit_points):
    """
    Add character to brawl
    """

    # limit brawl size
    if len(brawl) + 1 > 10:
        raise CookieLimit('Browser cookie do not support more monsters')

    # get a unique identifier for monster
    identifier = get_next_character_identifier(brawl)

    # to keep cookie small, and allow modifications we create a
    # slim representation of our monster object
    slim_monster = {
        'identifier': identifier,
        'name': name,
        'slug_name': slugify(name),
        'armor_class': armor_class,
        'hit_points': hit_points,
        'dexterity_modifier': initiative_modifier,
        'is_character': True,
        'notes': '',
        'conditions': []
    }

    # append monster to brawl
    brawl.append(slim_monster)

    # return modified brawl
    return brawl


def roll_initiative(brawl):
    """
    Roll initative for the brawl
    """

    # iterate over all monsters
    for monster in brawl:

        # if monster doesn't already have a initative roll it now
        if 'initiative' not in monster:

            # roll a d20 and get results
            roll = randint(1, 20)

            # add d20 results to monsters modifier
            roll_result = eval('%s%s' % (roll, monster['dexterity_modifier']))

            # set initiative to modifiered d20 roll
            monster['initiative'] = roll_result

    # sort monsters in initative order
    brawl = sorted(
        brawl, key=lambda x: x.get('initiative', -99), reverse=True)

    # return modified brawl
    return brawl


def set_turn(brawl, identifier):
    """
    Set the current monster turn
    """

    for monster in brawl:

        # if monster's identifier matches set to his turn,
        # else not it's turn
        if monster['identifier'] == identifier:
            monster['my_turn'] = True
        else:
            monster['my_turn'] = False

    # return modified brawl
    return brawl


def remove_monster(brawl, identifier):
    """
    Remove a monster
    """

    # remove monster with identifier from list
    brawl = [m for m in brawl if m['identifier'] != identifier]

    # return modified brawl
    return brawl


def get_conditions():
    """
    List of conditions
    """

    return [
        'blinded',
        'charmed',
        'deafened',
        'fatigued',
        'frightened',
        'grappled',
        'incapacitated',
        'invisible',
        'paralyzed',
        'petrified',
        'poisoned',
        'prone',
        'restrained',
        'stunned',
        'unconscious',
        'exhaustion'
    ]


def update_monster(
        brawl, identifier, initiative, armor_class, hit_points, notes,
        conditions):
    """
    Update a monster
    """

    # iterate over all monsters
    for monster in brawl:

        # if our monster matches unique_id this is the monster
        # we plan to update
        if monster['identifier'] == identifier:

            # if posted hit_points starts with a + operator
            # we should increase current hits
            if re.search('^\+', hit_points):
                hit_points = int(monster['hit_points']) + int(hit_points)

            # if posted hit_points starts with a - operator
            # we should decrease current hits
            elif re.search('^\-', hit_points):
                hit_points = int(monster['hit_points']) + int(hit_points)

            # else if hit points is a number we should set hits points
            else:
                hit_points = int(hit_points)

            # set our initative, hit_points, and notes
            monster['initiative'] = int(initiative)
            monster['armor_class'] = int(armor_class)
            monster['hit_points'] = int(hit_points)
            monster['notes'] = notes

            # add conditions
            monster['conditions'] = []
            for condition in conditions:
                monster['conditions'].append(condition)

    # sort monsters in initative order
    brawl = sorted(
        brawl, key=lambda x: x.get('initiative', -99), reverse=True)

    # return modified brawl
    return brawl
