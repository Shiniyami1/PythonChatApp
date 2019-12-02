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
            chatWindow.insert(END, msg)
            if 'has joined' in msg:
                sendNotification = pygame.mixer.Sound('eventually.wav')
                sendNotification.play()
            elif 'has disconnected from the chat.' in msg:
                msg.split()
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

"""GUI stuff"""
root = Tk()
root.title("SE3313 Project 2019 Chat")
msgFrame = Frame(root)  #Frame for messages
inputFrame = Frame(root)    #Frame for user input stuff
displayModeFrame = Frame(root)  #Frame for GUI mode buttons
scrollbar = Scrollbar(msgFrame)  # To navigate through past messages.
scrollbar.pack(side=RIGHT, fill=Y)
# Following will contain the messages.
chatWindow = Listbox(msgFrame, height=30, width=100, yscrollcommand=scrollbar.set)
chatWindow.pack(side=LEFT, pady=20, padx=10,fill=BOTH)
msgFrame.pack()

#colours for GUI
darkBG = '#383736'
darkChat = '#2b2b2b'
darkRed = '#a12d25'
orig_colour = root.cget("background")

def darkMode(event=None):
    root.configure(background=darkBG)
    msgFrame.configure(background=darkBG)
    chatWindow.configure(background=darkChat, fg=darkRed)
    send_button.configure(background=darkRed,fg='white')
    inputBar.configure(background='gray', fg=darkRed)
    inputFrame.configure(background=darkBG)
    dark_button.configure(background=darkRed, fg='white')
    light_button.configure(background=darkRed, fg='white')
    guiLabel.configure(background=darkBG, fg='white')
    displayModeFrame.configure(background=darkBG)

def lightMode(event=None):
    root.configure(background=orig_colour)
    msgFrame.configure(background=orig_colour)
    chatWindow.configure(background='white',fg='black')
    send_button.configure(background=orig_colour,fg='black')
    inputBar.configure(background='white')
    inputFrame.configure(background=orig_colour)
    dark_button.configure(background=orig_colour, fg='black')
    light_button.configure(background=orig_colour, fg='black')
    guiLabel.configure(background=orig_colour, fg='black')
    displayModeFrame.configure(background=orig_colour)

userInput = StringVar()  # For the messages to be sent.
#userInput.set("Type your messages here.")
inputBar = Entry(inputFrame, textvariable=userInput)
inputBar.bind("<Return>", send)
inputBar.pack(ipadx=175,side=LEFT, pady=20, padx=10)
send_button = Button(inputFrame, text="Send", command=send)
send_button.pack(side=LEFT, pady=20)
inputFrame.pack()

guiLabel = Label(displayModeFrame, text="Change Colour Scheme: ")
guiLabel.pack(side=TOP)
light_button = Button(displayModeFrame, text='Light mode', command=lightMode)
dark_button = Button(displayModeFrame, text='Dark mode', command=darkMode)
dark_button.pack(side=LEFT)
light_button.pack(side=LEFT,pady=10)
displayModeFrame.pack()


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
    chatWindow.insert(END, 'Client failed to connect to server!')

    client_socket.close()
    
    time.sleep(5)
    root.quit()

receive_thread = Thread(target=receive)
receive_thread.start()
mainloop()  # Starts GUI