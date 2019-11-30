#!/usr/bin/env python3
"""Server for multithreaded (asynchronous) chat application."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread


def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    while True:
        client, client_address = SERVER.accept()
        print("%s:%s has connected." % client_address)
        client.send(bytes("Please enter your username", "utf8"))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()


def handle_client(client):  # Takes client socket as argument.
    """Handles a single client connection."""

    name = client.recv(BUFSIZ).decode("utf8")
    welcome = 'Type {disconnect} to exit.'
    client.send(bytes(welcome, "utf8"))
    
    handle = {'socket' : client, 'room' : ''}
    clients[name] = handle
    roomPrompt = 'Please enter the chatroom you wish to join'
    client.send(bytes(roomPrompt, "utf8"))

    while True:
        msg = client.recv(BUFSIZ)
        if clients[name]['room'] == '':
            room = msg.decode("utf8")
            clients[name]['room'] = room
            msg = "%s has joined the chat!" % name
            broadcast(bytes(msg, "utf8"),room)
        elif msg != bytes("{quit}", "utf8"):
            broadcast(msg, room, name+": ")
        else:
            client.send(bytes("{quit}", "utf8"))
            client.close()
            del clients[client]
            broadcast(bytes("%s has left the chat." % name, "utf8"), room)
            break


def broadcast(msg, room, prefix=""):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""
    print(clients)
    for user in clients.values():
        if user['room'] == room:
            user['socket'].send(bytes(prefix, "utf8")+msg)

        
clients = {}
addresses = {}

HOST = ''
PORT = 4200
BUFSIZ = 1024
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

if __name__ == "__main__":
    SERVER.listen(5)
    print("Waiting for connection...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()