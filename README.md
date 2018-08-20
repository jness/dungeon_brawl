# **Dungeon Brawl**

A simple [Flask](http://flask.pocoo.org/) + [MongoDB](https://www.mongodb.com/)
application for reading [Dungons and Dragons](http://dnd.wizards.com/) monster
stats.

--> [YouTube Demo](https://www.youtube.com/watch?v=qo70m7hlmwg)

![alt text](https://i.imgur.com/GaFVBLn.png")

![alt text](https://i.imgur.com/CN6LZEe.png")

![alt text](https://i.imgur.com/l89RqzR.png")

![alt text](https://i.imgur.com/GYcN8F4.png")

![alt text](https://i.imgur.com/M84sffF.png")

![alt text](https://i.imgur.com/hazMySq.png")


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
