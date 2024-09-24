# WEB_1 Project

This project is a simple client-server application built using PyQt5 and Python. The application consists of two main components: a server and a client.

Server (server.py)
---
The server component is responsible for listening for incoming connections and sending random images to connected clients. The server uses a QTcpServer to listen for connections and a QLabel to display the sent images.

Client (client.py)
---
The client component is responsible for connecting to the server and sending messages to request images. The client uses a QTcpSocket to connect to the server and a QPushButton to send messages.

Utilities (util.py)
---
The utilities module provides common functions and variables used by both the server and client components. This includes the IP address and port number used for communication.
