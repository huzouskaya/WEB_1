# Remote System Backup
## Overview

This project implements a remote system backup system that allows users to backup files from one computer to another over a local network. The system consists of a client and a server, where the client initiates the backup process and the server provides the files to be backed up.

---
Features
+ Backup files from a remote computer to a local computer over a local network
+ Simple and efficient file transfer protocol
+ Easy to use and configure

##### How does it work

Client-Server Architecture
---
The system uses a client-server architecture, where the client (RemoteSystemBackup) initiates the backup process and the server (RemoteSystemBackupServer) provides the files to be backed up.
Network Communication

The client and server communicate over a local network using TCP sockets. The client sends a request to the server to backup a specific file, and the server responds by sending the file over the network.
File Transfer

The file transfer process is done in chunks, where the server reads the file in chunks and sends them to the client, which writes them to a local file.
Getting Started

Prerequisites
---
+ Two computers connected to the same local network
+ C++ compiler (e.g., GCC)
+ Socket library (e.g., Berkeley sockets)

Building and Running
---
+ Compile the client and server code using a C++ compiler.
+ Run the server on one computer, specifying the port number to listen on.
+ Run the client on the other computer, specifying the IP address and port number of the server.
+ The client will prompt the user to enter the file path to backup.
+ The server will send the file to the client, which will write it to a local file.

Limitations
---
+ This is a basic implementation and does not include error handling, security measures, or advanced features.
+ The system is designed for a local network and may not work over the internet.
+ The file transfer process is not optimized for large files or high-speed networks.

Future Development
---
+ Implement error handling and logging
+ Add security measures, such as encryption and authentication
+ Optimize the file transfer process for large files and high-speed networks
+ Add support for multiple file backups and scheduling
