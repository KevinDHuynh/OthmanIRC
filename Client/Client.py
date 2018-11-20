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
            msg = clientSocket.recv(1024).decode()
            print(msg+" original")
            if msg.startswith("/init"):
                command, user, ch = msg.split("&&")
                msgChannel = ch.replace("#", "")
                print(ch+" Channel")
                nickname = user
                channel(msgChannel)
            elif msg.startswith("/msg"):
                command,user,message = msg.split("&&")
                if user.startswith("False"):
                    app.addListItem("consoleList", "User does not exist.")
                else:
                    app.addListItem("consoleList", "<"+user+" --> " + nickname + "> " + message)
                    global last_msg
                    last_msg = user
                    """/msg&&fromuser&&message"""
            elif msg.startswith("/ping"):
                app.addListItem("consoleList", "Pong!")
            elif msg.startswith("/nick"):
                command, newnick = msg.split("&&")
                nickname = newnick
                app.addListItem("consoleList", "Changed nickname to: "+newnick)
            elif msg.startswith("/join"):
                command,success,channelName = msg.split("&&")
                if success == "False":
                    app.addListItem("consoleList", "Cannot join channel.")
                elif success == "Password":
                    app.addListItem("consoleList", "Incorrect Password for channel.")
                else:
                    channel(channelName)
            else:
                msgChannel, msgUser, msgData = msg.split("&&")
                msgChannel = msgChannel.replace("#", "")
                print(msgChannel+" destination channel")
                app.addListItem(msgChannel+"List", msgUser+": "+msgData)

        except OSError:
            break


def send(event=None):  # event is passed by binders.
    """Handles sending of messages."""
    """ValueError"""
    msg = "#"+app.getTabbedFrameSelectedTab("Channels") + "&&" +app.getEntry("Entry")
    if msg.startswith("#console&&"):
        if msg.startswith("#console&&/"):
            if app.getEntry("Entry").startswith("/msg"):
                command, user, message = app.getEntry("Entry").split(" ", 2)
                app.addListItem("console", "<" + nickname + " --> " + user + "> " + message)
                msg = command + "&&" + user + "&&" + message
            elif app.getEntry("Entry").startswith("/reply"):
                command, message = app.getEntry("Entry").split(" ", 1)
                app.addListItem("console", "<" + nickname + " --> " + last_msg + "> " + message)
                msg = command + "&&" + message
            elif app.getEntry("Entry").startswith("/join"):
                try:
                    password = " "
                    command, channelstuff, password = app.getEntry("Entry").split(" ")
                except ValueError:
                    command, channelstuff = app.getEntry("Entry").split(" ")
                msg = command + "&&" + channelstuff + "&&" + password
            elif app.getEntry("Entry").startswith("/quit"):
                clientSocket.close()
                app.quit
                exit(0)

            elif app.getEntry("Entry").startswith("/ping"):
                msg = "/ping"
            else:
                app.addListItem("generalList", "You can only send commands to the console.")
    else:
        channelMsg, msgBody = msg.split("&&")
        if channelMsg.startswith("#"):
            channelMsg = channelMsg.replace("#", "")
        app.addListItem(channelMsg+"List", nickname +": " + msgBody)
        try:
            print(msg)
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
        app.addListItem(channelName+"List", "Joined channel")
        app.stopTab()
        app.stopTabbedFrame()
        channelList.append(channelName)

def connect():
    global nickname
    try:
        clientSocket.connect((serverName, serverPort))
    except:
        return False
    initMessage = nickname
    clientSocket.send(initMessage.encode())
    receive_thread = Thread(target=receive)
    receive_thread.start()
    return True

def on_closing(event=None):
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
