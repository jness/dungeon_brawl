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

A demo of the application can be viewed here, this is as long as my [RaspberryPi](https://nessy.info/post/2023-01-21-running-dungeon-brawl-on-localhost/) keeps up: [https://dungeonbrawl.ngrok.io/](https://dungeonbrawl.ngrok.io/)

## Requirements

 * [Docker](https://www.docker.com/)
 * [docker-compose](https://docs.docker.com/compose/)

## Starting Containers

Use `docker-compose` to start the stacks:

```
$ docker-compose up
```

Once complete you will be able to visit the local web interface:

 > http://localhost:5000/

## Populate Data

MongoDB's collections are populated as a **module** *(see modules/ directory)*.

Once you've started the containers, use `docker-compose exec` to run module population.

```
$ docker-compose exec web scripts/populate.py firestorm_peak
```

## Purge Data

If you wish to populate a new **module**, first purge the existing data:

```
$ docker-compose exec web scripts/purge.py
```

## Stopping Containers

When you are done with the application use `docker-compose` to stop the containers:

```
$ docker-compose down
```
