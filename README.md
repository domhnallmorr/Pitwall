# Pitwall

Pitwall is a free and open F1 manager game being developed in python. There is very limited features and gameplay at the moment. Details are provided further below.

The game starts in 1998 and will allow the player to compete through to modern day F1.

The current objective is reach V1.0, that represents a "bare bones" game with all the major required features included in their most basic format.

The UI is built using flet.


## Features

- Drivers retire
- Practice/Qualy and Race sessions are simulated
- New drivers become available each year to hire


## Gameplay Features

- Player can replace a retiring driver


## RUNNING THE GAME

The game uses poetry to manage dependencies. The `pyproject.toml` file is located in the src folder. Ensure you are running poetry from the src folder.

Install Poetry with the following pip command:

```
pip install poetry
```

Install the dependencies with the following command:

```
poetry install
```

Run the game with the following command:

```
poetry run flet main.py
```
 
## Preview

![p1](preview/preview1.png)

![p2](preview/preview2.png)