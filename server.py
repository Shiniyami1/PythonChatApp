#!/usr/bin/env python3
"""Server for multithreaded (asynchronous) chat application."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

clients = {}
addresses = {}
HOST = ''
PORT = 4200
BUFSIZ = 1024
ADDR = (HOST, PORT)
SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    while True:
        client, client_address = SERVER.accept()
        print("%s:%s has connected." % client_address)
        client.send(bytes("Welcome to SE3313 Project - Chat Application"
                                  "\r\n\tPlease enter your username", "utf8"))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()

def handle_client(client):  # Takes client socket as argument.
    """Handles a single client connection."""
    name = client.recv(BUFSIZ).decode("utf8")
    welcome = 'Welcome %s! If you ever want to quit, type {disconnect} to exit. \r\n\tPlease enter the chatroom you wish to join' % name
    client.send(bytes(welcome, "utf8"))
    clients[client] = name
    first = True
    while True:
        msg = client.recv(BUFSIZ)
        if first:
            clients['room'] = msg
            now = 'Now chatting in '+msg.decode("utf8")+' room'
            client.send(bytes(now, "utf8"))
            msg = "%s has joined the chat!" % name
            broadcast(bytes(msg, "utf8"), clients['room'])
        if msg != bytes("{disconnect}", "utf8"):
            broadcast(msg, name+": ",clients['room'])
        else:
            client.send(bytes("{disconnect}", "utf8"))
            client.close()
            del clients[client]
            broadcast(bytes("%s has left the chat." % name, "utf8"), clients['room'])
            break

def broadcast(msg, room, prefix=""):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""
    for sock in clients:
        if clients[room] == room:
            sock.send(bytes(prefix, "utf8")+msg)            

if __name__ == "__main__":
    SERVER.listen(5)
    print("Waiting for connection...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()