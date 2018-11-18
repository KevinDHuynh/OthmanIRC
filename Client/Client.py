# -*- coding: utf-8 -*-

import socket
from threading import Thread
from appJar import gui
import random

serverName = ''
serverPort = int(1)
nickname = ''
autojoin = ''
password = ''
my_msg = ''
last_msg = ''
channelList = []
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def press(button):
    if button == "Connect":
        global serverName
        global serverPort
        global nickname
        global autojoin
        global password
        global serverPort
        serverName = app.getEntry("Server")
        serverPort = 6667
        nickname = app.getEntry("Nickname")
        autojoin = app.getEntry("Autojoin")
        password = app.getEntry("Password")
        if not serverName:
            serverName = '127.0.0.1'
        if not serverPort:
            serverport = 6667
        if not nickname:
            nickname = 'Guest' + str(random.randint(1000,9999))
        if not serverName:
            app.errorBox("noServer", "No server IP was given.")
        else:
            if connect():
                app.hideSubWindow("Connect")
                app.show()
    else:
        app.stop()
        clientSocket.close()

def receive():
    global nickname
    """Handles receiving of messages."""
    while True:
        try:
            msg = clientSocket.recv(1024).decode("utf8")

            if msg.startswith("/msg"):
                command,user,message = msg.split("&&")
                if user.startswith("False"):
                    app.addListItem("MessageList", "User does not exist.")
                else:
                    app.addListItem("MessageList", "<"+user+" --> " + nickname + "> " + message)
                    global last_msg
                    last_msg = user
                    """/msg&&fromuser&&message"""
            elif msg.startswith("/ping"):
                app.addListItem("MessageList", "Pong!")
            elif msg.startswith("/nick"):
                command,newnick = msg.split("&&")
                nickname = newnick
                app.addListItem("MessageList", "Changed nickname to: "+newnick)
            elif msg.startswith("/join"):
                command,success,channelName = msg.split("&&")
                if success == "False":
                    app.addListItem("MessageList", "Cannot join channel.")
                elif success == "Password":
                    app.addListItem("MessageList", "Incorrect Password for channel.")
                else:
                    channel(channelName)
            else:
                msgChannel, msgUser, msgData = msg.split("&&")
                app.addListItem("MessageList", msgUser+": "+msgData)

        except OSError:
            break


def send(event=None):  # event is passed by binders.
    """Handles sending of messages."""
    """ValueError"""
    channel = "#general"
    msg = channel+"&&" +app.getEntry("Entry")
    if app.getEntry("Entry").startswith("/quit"):
        clientSocket.close()
        exit(0)
        return
    elif app.getEntry("Entry").startswith("/msg"):
        command,user,message=app.getEntry("Entry").split(" ",2)
        app.addListItem("console", "<" + nickname + " --> " + user + "> " + message)
        msg = command+"&&"+user+"&&"+message
    elif app.getEntry("Entry").startswith("/reply"):
        command,message = app.getEntry("Entry").split(" ",1)
        app.addListItem("console", "<" + nickname + " --> " + last_msg + "> " + message)
        msg = command + "&&" + message
    elif app.getEntry("Entry").startswith("/join"):
        command,channel,password = app.getEntry("Entry").split(" ",2)
        msg = command + "&&" + channel + "&&" + password
    else:
        channelMsg, msgBody = msg.split("&&")
        app.addListItem(channelMsg+"List", nickname +": " + msgBody)

    try:
        clientSocket.send(msg.encode())
    except:
        app.errorBox("Could not send message.")

    app.setEntry("Entry", "")
def channel(channelName):
    global channelList
    if channelName in channelList:
        app.addListItem("channelList","ERROR: Already connected to channel")
    else:
        app.openTabbedFrame("Channels")
        app.startTab(channelName)
        app.addListBox(channelName+"List")
        app.addListItem(channelName+"List" , "Joined channel")
        app.stopTab()
        app.stopTabbedFrame()
        channelList.append(channelName)

def connect():
    global nickname
    try:
        clientSocket.connect((serverName, serverPort))
    except:
        return False
    initMessage = password + "&&" + nickname + '&&' + autojoin
    clientSocket.send(initMessage.encode())
    handshake = clientSocket.recv(1024).decode()
    if not handshake:
        app.errorBox("Could not connect.")
        return False
    print(handshake)
    newNickname,channelJoin = handshake.split("&&")
    nickname = newNickname

    channel(channelJoin)
    receive_thread = Thread(target=receive)
    receive_thread.start()
    return True

def on_closing(event=None):
    """This function is to be called when the window is closed."""
    app.stop()
    clientSocket.close()
    exit(0)


app = gui("OthmanIRC 0.03b")
app.setSize(1020,780)
app.icon = "icon.gif"
app.startTabbedFrame("Channels")
app.startTab("console")
app.addListBox("consoleList")
app.addListItem("consoleList", "Successfully connected to server")
app.stopTab()
app.stopTabbedFrame()

app.addLabelEntry("Entry").bind("<Return>", send)
app.setEntryDefault("Entry","Enter message here.")
app.addButton("Send", send)

app.startSubWindow("Connect")
app.addLabelEntry("Server")
app.addLabelEntry("Port")
app.addLabelSecretEntry("Password")
app.addLabelEntry("Nickname")
app.addLabelEntry("Autojoin")
app.setEntryDefault("Server", "127.0.0.1")
app.setEntryDefault("Nickname", "guest")
app.setEntry("Port", "6667")
app.addButtons(["Connect", "Cancel"], press)
app.stopSubWindow()

app.go(startWindow="Connect")
