# online-socket-chess
An online chess application using pygame and socket.

## Setup
Requirements:
- python 3.10

You can run the server.py file on a server. Then you'll be able to connect to it from anywhere.
To start an instance of a game (that can connect to the server) you need to run the window.py file.

The SERVER_ADDR constant in constants.py must match the server address of you server (host, port).

If you do not have a server and want to test it, you can also test it locally on your machine.
To do that you need to clone this repo, run the server.py file and then run some instances of the game by running the window.py file a few times.

## Hints
- Checkmate will not work. You will need to kill the king in order to win the game.
- En Passant won't work either.
