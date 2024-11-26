# E-logbook

This project provides a web-based application that allows managing the structure of a building, including floors, rooms, and equipment, with the capability to add, update, and delete items. The data is stored in an SQLite database using the Tortoise ORM, and the server is built with aiohttp.

## Overview

The system is designed to manage various types of rooms and equipment in a building. The core models represent a hierarchical structure consisting of:
- **Building**: Represents a building which may contain multiple floors.
- **Floor**: Represents a floor in a building which may contains various types of rooms.
- **Room**: Represents a room on a floor, with different room types like *industrial*, *auxiliary*, and *other*.
- **Equipment**: Represents equipment that resides in an *industrial* room.

## Project Structure

- `data_model.py`: Contains the data models for the application, defining the relationships between buildings, floors, rooms, and equipment.
- `main.py`: Contains the web server logic using aiohttp, routes for handling HTTP requests, and business logic for interacting with the database.
- `templates/`: A directory containing the html template for rendering the web interface.


## Working with this Project

- After pulling this project use `pip install -r requirements.txt` to install all the necessary libraries.
- Run `main.py` file after which the SQLite database and the aiohttp web-service will instantiate
- You can access the web-service by launching a browser of your choosing and opening `http://localhost:8080/` webpage
