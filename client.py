# Imports
from socket import AF_INET, socket, SOCK_STREAM
import socketserver
from threading import Thread
from tkinter import *
import time, pygame

pygame.mixer.init()
def getMsg():
    """Handles receiving of messages."""
    while True:
        try:
            recvMsg = client_socket.recv(buffer_size).decode("utf8")
            chatWindow.insert(END, recvMsg)
            chatWindow.yview(END)
            if 'has joined' in recvMsg:
                joinNotification = pygame.mixer.Sound('eventually.wav')
                joinNotification.play()
            elif 'has disconnected from the chat.' in recvMsg:
                discNotification = pygame.mixer.Sound('deduction.wav')
                discNotification.play()
            elif recvMsg == "{disconnect}":
                closeClient()

            else:
                recvNotification = pygame.mixer.Sound('when.wav')
                recvNotification.play()
        except OSError as err:  # Possibly client has left the chat.
            print(err)
            closeClient()
            break

def on_closing(event=None):
    """This function is to be called when the window is closed."""
    userInput.set("{disconnect}")
    sendMsg()

def sendMsg(event=None):  # event is passed by binders.
    """Handles sending of messages."""
    sendMsg = userInput.get()
    userInput.set("")  # Clears input field.
    try:
        client_socket.send(bytes(sendMsg, "utf8"))
    except OSError as err:
        print(err)
        errMsg = "***Sending message failed. Connection to Server may have been Interrupted.***"
        time.sleep(1.5)
        closeClient()
        chatWindow.insert(END, errMsg)
        chatWindow.yview(END)

    if sendMsg == "{disconnect}":
        closeClient()

def closeClient():
    try:
        #client_socket.shutdown(0)
        client_socket.close()
    except:
        print('socket is already closed')
    root.quit()

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

"""GUI stuff"""
# Frames foramin window
root = Tk()
root.title("SE3313 Project 2019 Chat")
msgFrame = Frame(root)  #Frame for messages
inputFrame = Frame(root)    #Frame for user input stuff
displayModeFrame = Frame(root)  #Frame for GUI mode buttons

# Listbox to display  messages
scrollbar = Scrollbar(msgFrame)
scrollbar.pack(side=RIGHT, fill=Y)
chatWindow = Listbox(msgFrame, height=30, width=100, yscrollcommand=scrollbar.set)
chatWindow.pack(side=LEFT, pady=20, padx=10,fill=BOTH)
msgFrame.pack()

# Individual GUI Elements
userInput = StringVar()
inputBar = Entry(inputFrame, textvariable=userInput)
inputBar.bind("<Return>", sendMsg)
inputBar.pack(ipadx=175,side=LEFT, pady=20, padx=10)
send_button = Button(inputFrame, text="Send", command=sendMsg)
send_button.pack(side=LEFT, pady=20)
inputFrame.pack()

guiLabel = Label(displayModeFrame, text="Change Colour Scheme: ")
guiLabel.pack(side=TOP)
light_button = Button(displayModeFrame, text='Light mode', command=lightMode)
dark_button = Button(displayModeFrame, text='Dark mode', command=darkMode)
dark_button.pack(side=LEFT)
light_button.pack(side=LEFT,pady=10)
displayModeFrame.pack()

#colours for GUI
darkBG = '#383736'
darkChat = '#2b2b2b'
darkRed = '#a12d25'
orig_colour = root.cget("background")

# Brute Exit Window via GUI escape button (The Big Red X)
root.protocol("WM_DELETE_WINDOW", on_closing)

"""Connection/Socket Code"""
# Initialize Connection 
host_addr = '192.168.0.21'
port_num = 4200

buffer_size = 1024
conn_addr = (host_addr, port_num)

client_socket = socket(AF_INET, SOCK_STREAM)
try:
    client_socket.connect(conn_addr)
except OSError as err:
    print(err)
    chatWindow.insert(END, 'Client failed to connect to server!')
    client_socket.close()
    time.sleep(5)
    root.quit()

receive_thread = Thread(target=getMsg)
receive_thread.start()
mainloop()  # Starts GUI