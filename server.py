from socket import AF_INET, socket, SOCK_STREAM
from socket import SHUT_RD, SHUT_WR, SHUT_RDWR
from threading import Thread
import threading
import select
import os

class socketThread(Thread):
    def __init__(self, client):
        # Event stop can be set to stop to exit while loop if thread is not blocking
        self.stop = threading.Event()
        self.clientSocket = client
        self._guard = threading.Lock()
        self.first = True
        Thread.__init__(self, target=self.threadMain)
    
    def threadMain(self):
        client = self.clientSocket
        while not self.stop.wait(0.1):            
            # Deliver username and chatroom prompt
            if self.first:
                self.first = False
                try:
                    client.send(bytes("Please enter your username", "utf8"))
                except:
                    print("Failed to send username prompt")
                    break
                try:
                    username = client.recv(buffer_size).decode("utf8")
                except:
                    print("Failed to read socket")
                
                instr_Msg = 'Type {disconnect} to exit.'
                try:
                    client.send(bytes(instr_Msg, "utf8"))
                except:
                    print('\nCould not send welcome message')
                    break

                # Save socket information in dictionary clients
                handle = {'socket' : client, 'room' : ''}
                clients[username] = handle
                roomPrompt = '\nPlease enter the chatroom you wish to join'
                try:
                    client.send(bytes(roomPrompt, "utf8"))
                except:
                    print("\nFailed to send room prompt message to client")
                    break
                try:
                    userInput = client.recv(buffer_size)
                except:
                    print("Failed to read socket")
                    break
                
                roomName = userInput.decode("utf8")
                clients[username]['room'] = roomName
                userInput = "%s has joined %s!" % (username,roomName)
                with self._guard:
                    self.broadcast(bytes(userInput, "utf8"),roomName)
            
            try:
                userInput = client.recv(buffer_size)
            except:
                print("Failed to read socket")
                break
            # If socket sends empty object b'' exit loop as client has closed socket on their end
            if not userInput:
                break
            # Broadcast userinput to chatroom
            if userInput != bytes("{disconnect}", "utf8"):
                with self._guard:
                    self.broadcast(userInput, roomName, username+": ")
            # Broadcast disconnect message and terminate thread
            else:
                with self._guard:
                    self.broadcast(bytes("%s has disconnected from the chat." % username, "utf8"), roomName)
                self.terminate()
        
        

    # Broadcast function: sends all clients associated with a chatroom a message
    def broadcast(self, msg, room, prefix=""):
        # Each user has an object containing socket and chatroom in the clients dictionary
        # Send a message using a socket only to the users in the chatroom
        # If a user has closed a connection handle the ConnectionResetError by printing a message in terminal
        
        for user in clients.values():
            if user['room'] == room and user['room'] != '':
                try:
                    user['socket'].send(bytes(prefix, "utf8")+msg)
                except OSError:
                    print("Client " +str(addresses[user['socket']])+ " has disconnected")
                    break

    # Shutdowns down each socket preventing subsequent reads and closes the socket, unblocking the thread
    # Sets stop flag on Event that allows threadMain to exit if thread is not blocking
    def terminate(self):
        #
        try:
            self.clientSocket.send((bytes("{disconnect}","utf8")))
            self.clientSocket.shutdown(SHUT_RD)
            self.clientSocket.close()
        except OSError:
            print('Socket closed, terminate message not sent')
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
        
        
        while not self.stop.wait(0.1):
            try:
                client, client_address = server.accept()
            except:
                print("Server socket closed")
                break
            print("%s:%s has connected." % client_address)
            addresses[client] = client_address

            # if a local connection has been made, terminate() has been called
            if client_address[0] == '127.0.0.1' and self.stop.is_set():
                break
            # create new socketThread and start it
            temp = socketThread(client)
            temp.start()
            # save each socketThread in _sockets dictionary
            _sockets[str(self.counter)] = temp
            self.counter+=1
            
            
    # Shutdowns down the serverThread
    # Calls terminate on each socketThread in _sockets
    # If no socketThreads have been created handle error
    def terminate(self):
        try:
            for thread in _sockets.values():
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
            break
    try:
        server.shutdown(SHUT_RDWR)
    except:
        pass    
    server.close()
    