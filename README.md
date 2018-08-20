# **Dungeon Brawl**

A simple [Flask](http://flask.pocoo.org/) + [MongoDB](https://www.mongodb.com/)
application for reading [Dungons and Dragons](http://dnd.wizards.com/) monster
stats.

--> [YouTube Demo](https://www.youtube.com/watch?v=Dt1mFPOkvcE)

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

The MongoDB collections are **ONLY** populated during container startup,
and **ONLY** if the collection does not already exist.

If you need to purge the database merely stop the containers:

> $ docker-compose down

Then delete the the `mongo_data/` directory.

## Running server

Use `docker-compose` to start the containers:

> $ docker-compose up

Finally visit the running server: http://localhost:5000/
