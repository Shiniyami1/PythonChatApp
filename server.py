from socket import AF_INET, socket, SOCK_STREAM
from socket import SHUT_RD, SHUT_WR, SHUT_RDWR
from threading import Thread
import threading

class socketThread(Thread):
    def __init__(self, client):
        self.stop = threading.Event()
        self._running_flag = False
        self.clientSocket = client
        Thread.__init__(self, target=self.threadMain)
    
    def threadMain(self):

        first = True
        try:
            while not self.stop.wait(0.1):
                self._running_flag = True
                if first:
                    client = self.clientSocket
                    client.send(bytes("Please enter your username", "utf8"))
                    name = client.recv(buffer).decode("utf8")
                    welcome = 'Type {disconnect} to exit.'
                    first = False
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
        except:
            pass
        finally:
            self._running_flag = False
    def broadcast(self, msg, room, prefix=""):  # prefix is for name identification.
        """Broadcasts a message to all the clients."""
        for user in clients.values():
            if user['room'] == room:
                try:
                    user['socket'].send(bytes(prefix, "utf8")+msg)
                except:
                    print("Client " +str(user['socket'])+ " has disconnected")

    def terminate(self):
        self.clientSocket.shutdown(SHUT_RD)
        self.clientSocket.close()
        self.stop.set()
            

class serverThread(Thread):
    def __init__(self):
        self.stop = threading.Event()
        self._running_flag = False
        Thread.__init__(self, target=self.threadMain)

    def threadMain(self):
        # Handles each incoming connection request
        counter = 0
        try:
            while not self.stop.wait(0.1):
                self._running_flag = True
                try: 
                    client, client_address = server.accept()
                    print("%s:%s has connected." % client_address)
                    addresses[client] = client_address
                    temp = socketThread(client)
                    temp.start()
                    _sockets[str(counter)] = temp
                    print(temp)
                    print(_sockets)
                except:
                    print("\nFailed to connect to client")
        finally:
                self._running_flag = False
            
                
    def terminate(self):
        try:
            for thread in _sockets.values():
                thread.terminate()
                thread.join()
        except:
            print('No socketThreads to terminate')
        socket(AF_INET, SOCK_STREAM).connect(('localhost',4200))
        self.stop.set()

        
clients = {}
addresses = {}
_sockets = {}

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
    while True:
        terminate = input("Enter 'shutdown' to terminate server\n")
        if terminate == 'shutdown':
            server_thread.terminate()
            server_thread.join()
            break
    server.close()