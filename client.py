#!/usr/bin/env python3
"""Script for Tkinter GUI chat client."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter, time, pygame


def receive():
    """Handles receiving of messages."""
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            msg_list.insert(tkinter.END, msg)
            pygame.mixer.init()
            recvNotification = pygame.mixer.Sound('when.wav')
            recvNotification.play()
        except OSError:  # Possibly client has left the chat.
            break


def send(event=None):  # event is passed by binders.
    """Handles sending of messages."""
    msg = my_msg.get()
    my_msg.set("")  # Clears input field.
    client_socket.send(bytes(msg, "utf8"))

    if msg == "{disconnect}":
        pygame.mixer.init()
        sendNotification = pygame.mixer.Sound('eventually.wav')
        sendNotification.play()
        client_socket.close()
        top.quit()
            


def on_closing(event=None):
    """This function is to be called when the window is closed."""
    my_msg.set("{disconnect}")
    send()

top = tkinter.Tk()
top.title("SE3313 Project 2019 Chat")

messages_frame = tkinter.Frame(top)
my_msg = tkinter.StringVar()  # For the messages to be sent.
# my_msg.set("Type your messages here.")
scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
# Following will contain the messages.
msg_list = tkinter.Listbox(messages_frame, height=30, width=100, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()
messages_frame.pack()

entry_field = tkinter.Entry(top, textvariable=my_msg)
entry_field.bind("<Return>", send)
entry_field.pack(ipadx=175)
send_button = tkinter.Button(top, text="Send", command=send)
send_button.pack()

top.protocol("WM_DELETE_WINDOW", on_closing)

#----Now comes the sockets part----
HOST = '34.207.137.115'
PORT = 4200

BUFSIZ = 1024
ADDR = (HOST, PORT)

client_socket = socket(AF_INET, SOCK_STREAM)
try:
    client_socket.connect(ADDR)
except (ConnectionRefusedError, ConnectionRefusedError, ConnectionError) as error:
    msg_list.insert(tkinter.END, 'Client failed to connect to server!')
    client_socket.recv(BUFSIZ)
    client_socket.close()
    time.sleep(5)
    top.quit()

receive_thread = Thread(target=receive)
receive_thread.start()
tkinter.mainloop()  # Starts GUI execution.