from socket import AF_INET, socket, SOCK_STREAM
from socket import SHUT_RD, SHUT_WR, SHUT_RDWR
from threading import Thread
import threading

class socketThread(Thread):
    def __init__(self, client):
        # Event stop can be set to stop to exit while loop if thread is not blocking
        self.stop = threading.Event()
        self.clientSocket = client
        self._guard = threading.Lock()
        Thread.__init__(self, target=self.threadMain)
    
    def threadMain(self):

        first = True
        try:
            while self.stop.is_set():
                print(self.stop.is_set())
                # Deliver username and chatroom prompt
                if first:
                    client = self.clientSocket
                    client.send(bytes("Please enter your username", "utf8"))
                    username = client.recv(buffer_size).decode("utf8")
                    instr_Msg = 'Type {disconnect} to exit.'
                    first = False
                    try:
                        client.send(bytes(instr_Msg, "utf8"))
                    except:
                        print('\nCould not send welcome message')

                    # Save socket information in dictionary clients
                    handle = {'socket' : client, 'room' : ''}
                    clients[username] = handle
                    roomPrompt = '\nPlease enter the chatroom you wish to join'
                    try:
                        client.send(bytes(roomPrompt, "utf8"))
                    except:
                        print("\nFailed to send room prompt message to client")
                
                # Chatroom functionality
                # If client has not entered a chatroom first recv input is chat room
                # Otherwise accept user input and broadcast to all clients that are associated with chatroom
                userInput = client.recv(buffer_size)
                if clients[username]['room'] == '':
                    roomName = userInput.decode("utf8")
                    clients[username]['room'] = roomName
                    userInput = "%s has joined %s!" % (username,roomName)
                    with self._guard:
                        self.broadcast(bytes(userInput, "utf8"),roomName)
                elif userInput != bytes("{disconnect}", "utf8"):
                    with self._guard:
                        self.broadcast(userInput, roomName, username+": ")
                # When a user disconnects broadcast that they have disconnected to chatroom
                else:
                    try:
                        client.send(bytes("{disconnect}", "utf8"))
                    except:
                        pass
                    finally:
                        with self._guard:
                            self.broadcast(bytes("%s has disconnected from the chat." % username, "utf8"), roomName)
                        break
        except:
            print('\nClient Socket Closed:\n' +str(self.clientSocket))
        finally:
            self.stop.set
    # Broadcast function: sends all clients associated with a chatroom a message
    def broadcast(self, msg, room, prefix=""):
        # Each user has an object containing socket and chatroom in the clients dictionary
        # Send a message using a socket only to the users in the chatroom
        # If a user has closed a connection handle the ConnectionResetError by printing a message in terminal
        for user in clients.values():
            if user['room'] == room:
                try:
                    user['socket'].send(bytes(prefix, "utf8")+msg)
                except:
                    print("Client " +str(addresses[user['socket']])+ " has disconnected")

    # Shutdowns down each socket preventing subsequent reads and closes the socket, unblocking the thread
    # Sets stop flag on Event that allows threadMain to exit if thread is not blocking
    def terminate(self):
        self.clientSocket.close()
        self.stop.set()
            

class serverThread(Thread):
    def __init__(self):
        self.stop = threading.Event()
        self.counter = 0
        self.flag = False
        Thread.__init__(self, target=self.threadMain)

    def threadMain(self):
        # Handles each incoming connection request
        # A socketThread is created per connection to handle chatroom functionality
        # Each IP and port of incoming connection is saved in addresses dictionary
        
        
        while not self.stop.is_set():
            try: 
                client, client_address = server.accept()
                print("%s:%s has connected." % client_address)
                addresses[client] = client_address
                # create new socketThread and start it
                temp = socketThread(client)
                temp.start()
                # save each socketThread in _sockets dictionary
                _sockets[str(self.counter)] = temp
                self.counter+=1
            except:
                print("\nFailed to connect to client")
        
            
            
    # Shutdowns down the serverThread
    # Calls terminate on each socketThread in _sockets
    # If no socketThreads have been created handle error
    def terminate(self):
        try:
            for thread in _sockets.values():
                print(thread)
                thread.terminate()
                thread.join()
        except:
            print('No socketThreads to terminate')
        # Create a local connection to server socket to unblock accept() call
        t = socket(AF_INET, SOCK_STREAM)
        addr = ('localhost',4200)
        t.connect(addr)
        self.stop.set()

        
clients = {}
addresses = {}
_sockets = {}


host_addr = ''
port_num = 4200
buffer_size = 1024
conn_addr = (host_addr, port_num)

server = socket(AF_INET, SOCK_STREAM)
server.bind(conn_addr)

# start serverThread
# terminate entire server when user enters 'shutdown
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
            print(server_thread)
            break
    server.close()