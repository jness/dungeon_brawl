# **Dungeon Brawl**

A simple [Flask](http://flask.pocoo.org/) + [MongoDB](https://www.mongodb.com/)
application for reading [Dungons and Dragons](http://dnd.wizards.com/) monster
stats.

![alt text](https://i.imgur.com/1e8zOe9.png")

![alt text](https://i.imgur.com/ctQiDbs.png")

![alt text](https://i.imgur.com/ubFJBGI.png")

![alt text](https://i.imgur.com/k79KLJW.png")

![alt text](https://i.imgur.com/r6Pp8fy.png")

![alt text](https://i.imgur.com/JC6gRsm.png")

## Requirements

 * Docker
 * docker-compose

## Database

The Mongo database is populated with new json documents
from the `monsters/` directory on each run.

If you need to purge this database merely stop the containers:

> $ docker-compose down

Then delete the the `mongo_data/` directory.

## Running server

To start the application:

> $ docker-compose up

Finally visit the running server: http://localhost:5000/
