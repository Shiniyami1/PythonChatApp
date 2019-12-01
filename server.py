from socket import AF_INET, socket, SOCK_STREAM
import socketserver
from threading import Thread
import threading

class socketThread(Thread):
    def __init__(self, client):
        self._running = False
        self.stop = threading.Event()
        self.clientSocket = client
        Thread.__init__(self, target=self.threadMain)
        print('init')
    
    def threadMain(self): 
        # Handles each client request
        print('test')
        print(self.clientSocket)
        client = self.clientSocket
        client.send(bytes("Please enter your username", "utf8"))
        name = client.recv(buffer).decode("utf8")
        welcome = 'Type {disconnect} to exit.'
        try:
            client.send(bytes(welcome, "utf8"))
        except:
            print('\nCould not send welcome message')
    
        handle = {'socket' : client, 'room' : ''}
        clients[name] = handle
        roomPrompt = '\nPlease enter the chatroom you wish to join'
        try:
            client.send(bytes(roomPrompt, "utf8"))
        except:
            print("\nFailed to send room prompt message to client")
    
        while True:
            message = client.recv(buffer)
            if clients[name]['room'] == '':
                room = message.decode("utf8")
                clients[name]['room'] = room
                message = "%s has joined %s!" % (name,room)
                self.broadcast(bytes(message, "utf8"),room)
            elif message != bytes("{disconnect}", "utf8"):
                self.broadcast(message, room, name+": ")
            else:
                try:
                    client.send(bytes("{disconnect}", "utf8"))
                except:
                    pass
                finally:
                    self.broadcast(bytes("%s has left the chat." % name, "utf8"), room)
                break
    def broadcast(self, msg, room, prefix=""):  # prefix is for name identification.
        """Broadcasts a message to all the clients."""
        for user in clients.values():
            if user['room'] == room:
                try:
                    user['socket'].send(bytes(prefix, "utf8")+msg)
                except:
                    print("Client " +str(user['socket'])+ " has disconnected")

    def terminate(self):
        self.stop.set()
            

class serverThread(Thread):
    def __init__(self):
        self._running = False
        self._sockets = list()
        self.stop = threading.Event()
        Thread.__init__(self, target=self.threadMain)

    def threadMain(self):
        # Handles each incoming connection request
        while not self.stop.wait(1):
            print('running')
            try: 
                self._running = True
                client, client_address = server.accept()
                print("%s:%s has connected." % client_address)
                addresses[client] = client_address
                socketThread(client)
            except:
                print("\nFailed to connect to client")
            finally:
                self._running = False
                
    def terminate(self):
        self.stop.set()

        
clients = {}
addresses = {}

host = ''
port = 4200
buffer = 1024
address = (host, port)

server = socket(AF_INET, SOCK_STREAM)
server.bind(address)

if __name__ == "__main__":
    server.listen(5)
    print("Waiting for connections...\n")
    server_thread = serverThread()
    server_thread.start()
    terminate = input("Enter 'shutdown' to terminate server\n")
    if terminate == 'shutdown':
        server_thread.terminate()
        server_thread.join()
    server.close()