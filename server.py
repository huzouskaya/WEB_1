import socket
import pickle
import time
from threading import Thread

from constants import SERVER_ADDR
from board import Board


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(SERVER_ADDR)
server_socket.listen()

boards = []
connection_sockets = []
client_names = []
connection_count = 0


def client_thread(client_socket: socket.socket, board: Board, connection_number: int) -> None:
    global connection_count

    if connection_number%2 == 0:
        communicating_client_num = connection_number + 1
        while communicating_client_num >= len(connection_sockets):
            continue
    else:
        communicating_client_num = connection_number - 1

    client_name = client_socket.recv(1024).decode("utf-8")
    client_names.append(client_name)
    board.set_name(client_name)
    time.sleep(1) # wait until both clients have set the name

    if client_names[connection_number] == client_names[communicating_client_num]:
        client_socket.close()
        print("[LOST] connection to a client")
        connection_count -= 1
        return


    client_socket.send(pickle.dumps(board))

    while True:
        try:
            command = client_socket.recv(4096)
            board.command(pickle.loads(command))
            connection_sockets[communicating_client_num].send(command)
        except (ConnectionResetError, ConnectionAbortedError, EOFError):
            client_socket.close()
            print("[LOST] connection to a client")
            connection_sockets[communicating_client_num].close()
            print("[LOST] connection to a client")
            connection_count -= 1
            return


if __name__ == "__main__":
    print("[WAITING] for incoming connections")

    while True:
        client_socket, addr = server_socket.accept()
        connection_sockets.append(client_socket)
        connection_count += 1

        print(f"[CONNECTION] total: {connection_count}")
        
        if (len(connection_sockets)-1)//2 >= len(boards):
            boards.append(Board())
            print(f"[CREATED] new board, total: {len(boards)}")
        
        thread = Thread(target=client_thread, args=(client_socket, boards[-1], len(connection_sockets)-1))
        thread.start()
        
