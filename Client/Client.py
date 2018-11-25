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
                    app.addListItem(app.getTabbedFrameSelectedTab("Channels")+"List", "User does not exist.")
                else:
                    app.addListItem(app.getTabbedFrameSelectedTab("Channels")+"List", "<"+user+"> " + message)
                    global last_msg
                    last_msg = user
            elif msg.startswith("/reply"):

                try:
                    command, user, message = msg.split("&&")
                except ValueError:
                    command,message = msg.split("&&")
                if user:
                    app.addListItem("consoleList", message)
                else:
                    app.addListItem("consoleList", "<" + nickname + " --> " + last_msg + "> " + message)
            elif msg.startswith("/nick"):
                command, newnick = msg.split("&&")
                nickname = newnick
                app.addListItem(app.getTabbedFrameSelectedTab("Channels")+"List", "Changed nickname to: "+newnick)
            elif msg.startswith("/join"):
                command,success,channelName = msg.split("&&")
                if success == "False":
                    app.addListItem(app.getTabbedFrameSelectedTab("Channels")+"List", "Cannot join channel.")
                elif success == "Password":
                    app.addListItem(app.getTabbedFrameSelectedTab("Channels")+"List", "Incorrect Password for channel.")
                else:
                    channel(channelName)
            elif msg.startswith("/ping"):
                app.addListItem(app.getTabbedFrameSelectedTab("Channels")+"List", "Pong!")
            elif msg.startswith("/list"):
                command, channelList = msg.split("&&")
                app.addListItem(app.getTabbedFrameSelectedTab("Channels")+"List",channelList)
            elif msg.startswith("/version"):
                command, version = msg.split("&&")
                app.addListItem(app.getTabbedFrameSelectedTab("Channels") + "List", version)
            elif msg.startswith("/names"):
                command, nameList = msg.split("&&")
                app.addListItem(app.getTabbedFrameSelectedTab("Channels") + "List", nameList)
            elif msg.startswith("/part"):
                command, bool, message = msg.split("&&")
                if bool == "True":
                    if message.startswith("#"):
                        message = message.replace("#","")
                    app.setTabbedFrameDisabledTab("Channels", message, disabled=True)
                    app.addListItem(app.getTabbedFrameSelectedTab("Channels") + "List", "Successfully Left "+message)
                else:
                    app.addListItem(app.getTabbedFrameSelectedTab("Channels") + "List", message)
            elif msg.startswith("/kick"):
                command, bool, message = msg.split("&&")
                app.addListItem(app.getTabbedFrameSelectedTab("Channels") + "List", message)
            elif msg.startswith("/commands"):
                command, commandList = msg.split("&&")
                app.addListItem(app.getTabbedFrameSelectedTab("Channels") + "List", commandList)
            elif msg.startswith("/stats"):
                command, stats = msg.split("&&")
                app.addListItem(app.getTabbedFrameSelectedTab("Channels") + "List", stats)
            elif msg.startswith("/oper"):
                command, boolean, message = msg.split("&&")
                app.addListItem(app.getTabbedFrameSelectedTab("Channels") + "List", message)
            elif msg.startswith("Unknown Message Format"):
                app.addListItem("consoleList","Command not recognized by server.")
            else:
                msgChannel, msgUser, msgData = msg.split("&&")
                msgChannel = msgChannel.replace("#", "")
                print(msgChannel+" destination channel")
                app.addListItem(msgChannel+"List", msgUser+": "+msgData)

        except OSError:
            break


def send():  # event is passed by binders.
    """Handles sending of messages."""
    msg = "#"+app.getTabbedFrameSelectedTab("Channels") + "&&" +app.getEntry("Entry")

    if msg.startswith("#console&&") or app.getEntry("Entry").startswith("/"):
        print(app.getEntry("Entry")+" CONSOLE")
        msg = commandsend()
    else:
        channelMsg, msgBody = msg.split("&&")
        if channelMsg.startswith("#"):
            channelMsg = channelMsg.replace("#","")
        app.addListItem(channelMsg+"List", nickname +": " + msgBody)
    try:
        if msg:
            print(msg)
            clientSocket.send(msg.encode())
    except:
        app.errorBox("Could not send message.")
    app.setEntry("Entry", "")


def commandsend():
    msg = None
    if app.getEntry("Entry").startswith("/msg"):
        command, user, message = app.getEntry("Entry").split(" ", 2)
        app.addListItem("consoleList", "<" + nickname + " --> " + user + "> " + message)
        msg = command + "&&" + user + "&&" + message
    elif app.getEntry("Entry").startswith("/reply"):
        command, message = app.getEntry("Entry").split(" ", 1)
        app.addListItem("consoleList", "<" + nickname + " --> " + last_msg + "> " + message)
        msg = command + "&&" + message
    elif app.getEntry("Entry").startswith("/join"):
        channelPassword = " "
        try:
            command, channelstuff, channelPassword = app.getEntry("Entry").split(" ")
        except ValueError:
            command, channelstuff = app.getEntry("Entry").split(" ")
        if not channelstuff.startswith("#"):
            channelstuff = "#" + channelstuff
        msg = command + "&&" + channelstuff + "&&" + channelPassword
    elif app.getEntry("Entry").startswith("/nick"):
        try:
            command, nick = app.getEntry("Entry").split(" ")
            msg = command+"&&"+nick
        except ValueError:
            app.addListItem(app.getTabbedFrameSelectedTab("Channels") + "List",
                            "Please supply a nickname")
    elif app.getEntry("Entry").startswith("/oper") or app.getEntry("Entry").startswith("/op"):
        try:
            command, user, password = app.getEntry("Entry").split(" ")
            msg = command + "&&" + user + "&&" + password
        except ValueError:
            msg = None
    elif app.getEntry("Entry").startswith("/kick"):
        try:
            command, channel, user = app.getEntry("Entry").split(" ")
            if not channel.startswith("#"):
                channel = "#" + channel
            msg = command + "&&" + channel + "&&" + user
        except ValueError:
            app.addListItem(app.getTabbedFrameSelectedTab("Channels") + "List",
                            "Correct syntax is /kick [channel] [user]")
            msg = None
    elif app.getEntry("Entry").startswith("/part"):
        try:
            command, channel = app.getEntry("Entry").split(" ")
            msg = command+"&&"+channel
        except ValueError:
            app.addListItem(app.getTabbedFrameSelectedTab("Channels") + "List",
                            "Please specify a channel name.")
            msg = None
    elif app.getEntry("Entry").startswith("/names"):
        try:
            command, channel = app.getEntry("Entry").split(" ")
            if channel.startswith("#"):
                msg = "/names&&" + channel
            else:
                msg = "/names&&#" + channel
        except ValueError:
            msg = "/names&&#general"
    elif app.getEntry("Entry").startswith("/version"):
        msg = "/version&&"
    elif app.getEntry("Entry").startswith("/list"):
        msg = "/list&&"
    elif app.getEntry("Entry").startswith("/help") or app.getEntry("Entry").startswith("/commands"):
        msg = "/commands&&"
    elif app.getEntry("Entry").startswith("/ping"):
        msg = "/ping&&"
    elif app.getEntry("Entry").startswith("/stats"):
        msg = "/stats&&"
    elif app.getEntry("Entry").startswith("/quit"):
        clientSocket.close()
        app.quit()
        exit(0)
    else:
        app.addListItem("consoleList", "Command not recognized by client.")
        msg = None
    return msg


def channel(channelName):
    global channelList
    if channelName in channelList:
        app.addListItem("channelList","ERROR: Already connected to channel")
    else:
        if channelName.startswith("#"):
            channelName = channelName.replace("#", "")
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
    clientSocket.close()
    exit(0)


app = gui("OthmanIRC 0.04")
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
app.setStopFunction(on_closing())
