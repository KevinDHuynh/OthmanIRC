# -*- coding: utf-8 -*-

import socket
from threading import Thread
from appJar import gui

serverName = ''
serverPort = 0
nickname = ''
autojoin = ''
password = ''
my_msg = ''
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def press(button):
    if button == "Connect":
        global serverName
        global serverPort
        global nickname
        global autojoin
        global password
        serverName = app.getEntry("Server")
        serverPort = app.getEntry("Port")
        nickname = app.getEntry("Nickname")
        autojoin = app.getEntry("Autojoin")
        password = app.getEntry("Password")
        app.hide()
        connect()
    else:
        app.stop()

def receive():
    """Handles receiving of messages."""
    while True:
        try:
            msg = clientSocket.recv(1024).decode("utf8")
            gui.addLabel("lastMessage", msg)
        except OSError:  # Possibly client has left the chat.
            break


def send(event=None):  # event is passed by binders.
    """Handles sending of messages."""
    msg = my_msg.get()
    my_msg.set("")  # Clears input field.
    clientSocket.send(bytes(msg, "utf8"))
    if msg == "{quit}":
        clientSocket.close()
        app.quit()


def on_closing(event=None):
    """This function is to be called when the window is closed."""
    my_msg.set("{quit}")
    send()

def connect():
    clientSocket.connect((serverName, serverPort))

    initialMessage = password + ":" + nickname + ':' + autojoin

    outputMessage = input()
    clientSocket.send(outputMessage.encode())
    inputMessage = clientSocket.recv(1024).decode()
    print('Server:', inputMessage)

    clientSocket.close()


app = gui("OthmanIRC 0.01")
app.setSize(300,200)
app.addLabelEntry("Server")
app.addLabelEntry("Port")
app.addLabelSecretEntry("Password")
app.addLabelEntry("Nickname")
app.addLabelEntry("Autojoin")
app.setEntryDefault("Server","127.0.0.1")
app.setEntryDefault("Nickname","guest")
app.setEntryDefault("Port", "6667")
app.addButtons(["Connect", "Cancel"], press)


""""""""""""""""""""""""""""""""""""





receive_thread = Thread(target=receive)
receive_thread.start()

app.go()
