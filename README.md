# **Dungeon Brawl**

Dungeon brawl is a Python [Flask](http://flask.pocoo.org/) application
with a [MongoDB](https://www.mongodb.com/) datastore, the stack runs
inside [Docker](https://www.docker.com/) with the help of
[docker-compose](https://docs.docker.com/compose/).

Using this application a Dungeon Master can easily
track all things combat for their [Dungeons and Dragons](http://dnd.wizards.com/)
group.

Some of the application's major features include:

* Monster search
* Spell search
* Conditions search
* RPG Dice
* Combat turn tracking

![alt text](https://i.imgur.com/2du0tY7.png")

A demo of the application can be viewed here: [http://dnd.nessy.info](http://dnd.nessy.info)

## Requirements

 * [Docker](https://www.docker.com/)
 * [docker-compose](https://docs.docker.com/compose/)

## Datastore

Mongo's collections are **ONLY** populated during container startup,
and **ONLY** if the collection does not already exist; this is thanks to the `populate.py` script.

If you need to purge the datastore, first stop any running containers:

> $ docker-compose down

then delete the `mongo_data/` directory, this directory
will be recreated and populated the next time you start the stack.

## Startup

Use `docker-compose` to start the stack:

> $ docker-compose up

Once running visit: http://localhost:5000/
