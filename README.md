# **Dungeon Brawl**

A simple [Flask](http://flask.pocoo.org/) + [MongoDB](https://www.mongodb.com/)
application for reading [Dungons and Dragons](http://dnd.wizards.com/) monster
stats.

![alt text](https://i.imgur.com/ypveomF.png")

![alt text](https://i.imgur.com/0I50nq1.png")

## Requirements

 * Docker
 * docker-compose

## Populate database

The Mongo database is populated with the `monsters.json` file
and the `mongoimport` command.

Run the following command within the repository directory:

> $ docker-compose run web mongoimport -h mongo -u root -p password -d dungeon_brawl -c monsters --file monsters.json --authenticationDatabase admin --jsonArray

Then make sure all docker containers are stopped:

> $ docker-compose down

## Running server

Once the database has been populated merely run `docker-compose up`

> $ docker-compose up

Finally visit the running server: http://localhost:5000/
