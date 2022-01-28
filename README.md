# Homecoming
The best game ever

A 2D platform game based on the python language and the pygame library.

You will play as a yellow square that travels through 2D dimensions.
His goal is to go through all dimensions and return to his own.

<img src="https://github.com/nikita-popov/Homecoming/blob/master/docs/example1.png?raw=true" alt="example1" width="350"/>

<img src="https://github.com/nikita-popov/Homecoming/blob/master/docs/example2.png?raw=true" alt="example2" width="350"/>

Game objects:

- square character that can move around and spit fireballs
- wall
- platform
- door
- unstable wall
- fire
- spikes
- three types of monsters
- object

There are five levels in total, arranged in order of increasing difficulty:

- The first level is training. In it, the player will understand all the basic mechanics of the game.
- The next two levels are more difficult than the previous one, but do not cause difficulties.
- The fourth and fifth levels are especially difficult.
- At the end, the player will see a text with congratulations.

The player's results are saved.

## Implementation features

The engine.py file contains classes for all objects, functions for building and running the level, all sprite groups, and user events. Every object in the game is an instance of a class that inherits from Sprite.
The main.py file contains the game loop, saves the results, moves the camera behind the character, checks for events, exit functions to the main menu and the level selection menu.

Each level is a csv file. It represents the color and coordinates of objects. The data is separated by the symbol ";".
To create a level, you need to arrange the pixels of the corresponding color in a graphic editor, save the image in png format, after which you need to run the engine.py file and enter the level number. After that, a file will appear in the data folder, which can already be opened by the game as a level.
Such level creation mechanics greatly facilitated development and made it possible to quickly add new levels without affecting the game code in any way.
The player's progress is saved in the progress file.

## Usage

The following libraries are required to run the game:

- Pygame version 2.1.2
- Pillow version 9.0.0
