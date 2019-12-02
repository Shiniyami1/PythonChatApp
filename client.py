# Imports
from socket import AF_INET, socket, SOCK_STREAM
import socketserver
from threading import Thread
from tkinter import *
import time, pygame

pygame.mixer.init()
def receive():
    """Handles receiving of messages."""
    while True:
        try:
            msg = client_socket.recv(buffer_size).decode("utf8")
            msg_list.insert(END, msg)
            if 'has joined' in msg:
                sendNotification = pygame.mixer.Sound('eventually.wav')
                sendNotification.play()
            elif 'has left the chat.' in msg:
                sendNotification = pygame.mixer.Sound('deduction.wav')
                sendNotification.play()
            else:
                recvNotification = pygame.mixer.Sound('when.wav')
                recvNotification.play()
        except OSError:  # Possibly client has left the chat.
            break


def send(event=None):  # event is passed by binders.
    """Handles sending of messages."""
    msg = userInput.get()
    userInput.set("")  # Clears input field.
    client_socket.send(bytes(msg, "utf8"))

    if msg == "{disconnect}":
        client_socket.close()
        root.quit()

def on_closing(event=None):
    """This function is to be called when the window is closed."""
    userInput.set("{disconnect}")
    send()

root = Tk()
root.title("SE3313 Project 2019 Chat")

msgBox = Frame(root)
userInput = StringVar()  # For the messages to be sent.
# my_msg.set("Type your messages here.")
scrollbar = Scrollbar(msgBox)  # To navigate through past messages.
scrollbar.pack(side=RIGHT, fill=Y)
# Following will contain the messages.
msg_list = Listbox(msgBox, height=30, width=100, yscrollcommand=scrollbar.set)
msg_list.pack(side=LEFT, fill=BOTH)
msgBox.pack()

inputBar = Entry(root, textvariable=userInput)
inputBar.bind("<Return>", send)
inputBar.pack(ipadx=175,side=LEFT,pady=20,padx=10)
send_button = Button(root, text="Send", command=send)
send_button.pack(side=LEFT,padx=10)


root.protocol("WM_DELETE_WINDOW", on_closing)

#----Now comes the sockets part----
host_addr = 'localhost'
port_num = 4200

buffer_size = 1024
conn_addr = (host_addr, port_num)

client_socket = socket(AF_INET, SOCK_STREAM)
try:
    client_socket.connect(conn_addr)
except (ConnectionRefusedError, ConnectionRefusedError, ConnectionError) as error:
    msg_list.insert(END, 'Client failed to connect to server!')

    client_socket.close()
    
    time.sleep(5)
    root.quit()

receive_thread = Thread(target=receive)
receive_thread.start()
mainloop()  # Starts GUI