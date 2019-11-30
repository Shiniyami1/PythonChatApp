from socket import AF_INET, socket, SOCK_STREAM
import socketserver
from threading import Thread
import threading

class serverThread(Thread):
    def __init__(self):
        self._running = False
        self.stop = threading.Event()
        Thread.__init__(self, target=self.threadMain)

    def threadMain(self):
        # Handles each incoming connection request
        while True:
            try: 
                self._running = True
                client, client_address = server.accept()
                #print("%s:%s has connected." % client_address)
                client.send(bytes("Please enter your username", "utf8"))
                addresses[client] = client_address
                Thread(target=socketThread, args=(client,)).start()
            except:
                print("Failed to connect to client")
            finally:
                self._running = False
    
    def terminate(self):
        self.stop.set()


def socketThread(client): 
    # Handles each client request

    name = client.recv(buffer).decode("utf8")
    welcome = 'Type {disconnect} to exit.'
    client.send(bytes(welcome, "utf8"))
    
    handle = {'socket' : client, 'room' : ''}
    clients[name] = handle
    roomPrompt = 'Please enter the chatroom you wish to join'
    try:
        client.send(bytes(roomPrompt, "utf8"))
    except:
        print("Failed to send room prompt message to client")
    

    while True:
        message = client.recv(buffer)
        if clients[name]['room'] == '':
            room = message.decode("utf8")
            clients[name]['room'] = room
            message = "%s has joined %s!" % (name,room)
            broadcast(bytes(message, "utf8"),room)
        elif message != bytes("{disconnect}", "utf8"):
            broadcast(message, room, name+": ")
        else:
            try:
                client.send(bytes("{disconnect}", "utf8"))
                broadcast(bytes("%s has left the chat." % name, "utf8"), room)
            except:
                pass
            break
            


def broadcast(msg, room, prefix=""):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""

    for user in clients.values():
        print(user['socket'])
        if user['room'] == room:
            try:
                user['socket'].send(bytes(prefix, "utf8")+msg)
            except:
                pass

        
clients = {}
addresses = {}

host = ''
port = 4200
buffer = 1024
ADDR = (host, port)

server = socket(AF_INET, SOCK_STREAM)
server.bind(ADDR)

if __name__ == "__main__":
    server.listen(5)
    print("Waiting for connection...")
    server_thread = serverThread()
    server_thread.start()
    server_thread.terminate()
    server_thread.join()
    server.close()