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
last_command = ''
channelList = []
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# When client hits the connect button
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
        password = app.getEntry("Autojoin Password")
        if not serverName:
            serverName = '127.0.0.1'
        if not serverPort:
            serverport = 6667
        if not nickname:
            nickname = 'Guest' + str(random.randint(1000, 9999))
        if not serverName:
            app.errorBox("noServer", "No server IP was given.")
        else:
            if connect():
                app.hideSubWindow("Connect")
                app.show()
    else:
        app.stop()
        clientSocket.close()
        exit(0)
#When client menu item is selected
def menuPress(choice):
    print(choice)

    if choice == "Join a New Server":
        clientSocket.close()
        app.go(startWindow="Connect")
    if choice == "Exit":
        exit(0)
    if choice == "font":
        print()
    if str.isdigit(choice):
        if int(choice) >= 10 & int(choice) <= 15:
            app.setFont(int(choice))
    bgColors = ["blue", "green", "white", "red", "black", "grey"]
    for color in bgColors:
        if str(choice) == color:
            app.setBg(str(choice))


# Handles server-to-client messages
def receive():
    global nickname
    counter = 0
    while True:
        try:
            msg = clientSocket.recv(1024).decode()
            print(msg + " original")
            if msg.startswith("/init"):
                command, user, ch = msg.split("&&")
                msgChannel = ch.replace("#", "")
                print(ch + " Channel")
                nickname = user
                channel(msgChannel)
            elif msg.startswith("/msg"):
                command, user, message = msg.split("&&")
                if user.startswith("False"):
                    app.addListItem(app.getTabbedFrameSelectedTab("Channels") + "List", "User does not exist.")
                else:
                    app.addListItem(app.getTabbedFrameSelectedTab("Channels") + "List", "<" + user + "> " + message)
                    global last_msg
                    last_msg = user
            elif msg.startswith("/reply"):

                try:
                    command, user, message = msg.split("&&")
                except ValueError:
                    command, message = msg.split("&&")
                if user:
                    app.addListItem("consoleList", message)
                else:
                    app.addListItem("consoleList", "<" + nickname + " --> " + last_msg + "> " + message)
            elif msg.startswith("/nick"):
                command, newnick = msg.split("&&")
                nickname = newnick
                app.addListItem(app.getTabbedFrameSelectedTab("Channels") + "List", "Changed nickname to: " + newnick)
            elif msg.startswith("/join"):
                command, success, channelName = msg.split("&&")
                if success == "False":
                    app.addListItem(app.getTabbedFrameSelectedTab("Channels") + "List", "Cannot join channel.")
                elif success == "Password":
                    app.addListItem(app.getTabbedFrameSelectedTab("Channels") + "List",
                                    "Incorrect Password for channel.")
                else:
                    channel(channelName)
            elif msg.startswith("/ping"):
                app.addListItem(app.getTabbedFrameSelectedTab("Channels") + "List", "Pong!")
            elif msg.startswith("/list"):
                command, channelList = msg.split("&&")
                app.addListItem(app.getTabbedFrameSelectedTab("Channels") + "List", channelList)
            elif msg.startswith("/version"):
                command, version = msg.split("&&")
                app.addListItem(app.getTabbedFrameSelectedTab("Channels") + "List", version)
            elif msg.startswith("/names"):
                try:
                    command, bool, nameList = msg.split("&&")
                    app.addListItem(app.getTabbedFrameSelectedTab("Channels") + "List", nameList)
                except ValueError:
                    stuff = msg.split("&&")
                    app.addListItem(app.getTabbedFrameSelectedTab("Channels") + "List",
                                    "Could not print List ")
                    print(*stuff)
            elif msg.startswith("/part"):
                command, bool, message = msg.split("&&")
                if bool == "True":
                    if message.startswith("#"):
                        message = message.replace("#", "")
                    app.setTabbedFrameDisabledTab("Channels", message, disabled=True)
                    app.addListItem(app.getTabbedFrameSelectedTab("Channels") + "List", "Successfully Left " + message)
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
                app.addListItem("consoleList", "Command not recognized by server.")
            else:
                msgChannel, msgUser, msgData = msg.split("&&")
                msgChannel = msgChannel.replace("#", "")
                print(msgChannel + " destination channel")
                app.addListItem(msgChannel + "List", msgUser + ": " + msgData)

        except OSError:
            app.setStatusbarBg("red",0)
            break


# handles client-to-server messages
def send(event=None):
    global last_command
    msg = "#" + app.getTabbedFrameSelectedTab("Channels") + "&&" + app.getEntry("Entry")
    if "&&" in app.getEntry("Entry"):
        app.addListItem(app.getTabbedFrameSelectedTab("Channels") + "List",
                        "I can't believe you tried to break my program :(")
    elif msg.startswith("#console&&") or app.getEntry("Entry").startswith("/"):
        print(app.getEntry("Entry") + " CONSOLE")
        msg = commandsend()
    else:
        channelMsg, msgBody = msg.split("&&")
        if channelMsg.startswith("#"):
            channelMsg = channelMsg.replace("#", "")
        app.addListItem(channelMsg + "List", nickname + ": " + msgBody)
    try:
        if msg:
            print(msg)
            clientSocket.send(msg.encode())
    except:
        app.errorBox("Could not send message.")
    last_command = app.getEntry("Entry")
    app.setEntry("Entry", "")


# handles command execution (server or client-side
def commandsend():
    msg = None
    if app.getEntry("Entry").startswith("/msg"):
        try:
            command, user, message = app.getEntry("Entry").split(" ", 2)
            app.addListItem("consoleList", "<" + nickname + " --> " + user + "> " + message)
            msg = command + "&&" + user + "&&" + message
        except ValueError:
            app.addListItem(app.getTabbedFrameSelectedTab("Channels") + "List",
                            "Correct syntax is /msg [user] (message)")
    elif app.getEntry("Entry").startswith("/reply"):
        try:
            command, message = app.getEntry("Entry").split(" ", 1)
            app.addListItem("consoleList", "<" + nickname + " --> " + last_msg + "> " + message)
            msg = command + "&&" + message
        except:
            app.addListItem(app.getTabbedFrameSelectedTab("Channels") + "List",
                            "Correct syntax is /reply (message)")
    elif app.getEntry("Entry").startswith("/join"):
        try:
            command, channelstuff, channelPassword = app.getEntry("Entry").split(" ")
            if not channelstuff.startswith("#"):
                channelstuff = "#" + channelstuff
            msg = command + "&&" + channelstuff + "&&" + channelPassword
        except ValueError:
            try:
                command, channelstuff = app.getEntry("Entry").split(" ")
                if not channelstuff.startswith("#"):
                    channelstuff = "#" + channelstuff
                msg = command + "&&" + channelstuff + "&&" + " "
            except ValueError:
                app.addListItem(app.getTabbedFrameSelectedTab("Channels") + "List",
                                "Correct syntax is /join [channel] [password]")
    elif app.getEntry("Entry").startswith("/nick"):
        try:
            command, nick = app.getEntry("Entry").split(" ")
            msg = command + "&&" + nick
        except ValueError:
            app.addListItem(app.getTabbedFrameSelectedTab("Channels") + "List",
                            "Please supply a nickname")
    elif app.getEntry("Entry").startswith("/oper") or app.getEntry("Entry").startswith("/op"):
        try:
            command, user, password = app.getEntry("Entry").split(" ")
            msg = "/oper&&" + user + "&&" + password
        except ValueError:
            app.addListItem(app.getTabbedFrameSelectedTab("Channels") + "List",
                            "Correct syntax is /op [user] [password]")
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
            msg = command + "&&" + channel
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
        clientSocket.send("/quit&&".encode())
        clientSocket.close()
        app.quit()
        exit(0)
    else:
        app.addListItem(app.getTabbedFrameSelectedTab("Channels") + "List",
                        "Command not recognized by client.")
        msg = None
    return msg


# joins channel and creates new tab in GUI
def channel(channelName):
    global channelList
    if channelName in channelList:
        app.addListItem("channelList", "ERROR: Already connected to channel")
    else:
        if channelName.startswith("#"):
            channelName = channelName.replace("#", "")
        app.openTabbedFrame("Channels")
        app.startTab(channelName)
        app.addListBox(channelName + "List")
        app.addListItem(channelName + "List", "Joined channel")
        app.stopTab()
        app.stopTabbedFrame()
        channelList.append(channelName)


# Inital connection
def connect():
    global nickname
    global autojoin
    global password
    try:
        clientSocket.connect((serverName, serverPort))
    except:
        return False
    initMessage = nickname
    clientSocket.send(initMessage.encode())
    receive_thread = Thread(target=receive)
    receive_thread.start()
    if autojoin:
        if password:
            app.setEntry("Entry", "/join " + autojoin + " " + password)
        else:
            app.setEntry("Entry", "/join " + autojoin + " " + password)
        send()
    return True


# Used for pressing up for last command
def lastMessage():
    global last_command
    app.setEntry("Entry", last_command)


# Used when gui is closed
def on_closing(event=None):
    clientSocket.close()
    exit(0)


# GUI execution
app = gui("OthmanIRC Client 0.08")
app.setSize(800,600)
app.setFont(10)
app.icon = "icon.gif"

app.addMenuList('File', ["Join a New Server", "Exit"], menuPress)
app.createMenu("Config")
app.addSubMenu("Config", "Font Size")
for i in range(6):
    app.addMenuRadioButton("Font Size", "1" + str(i), "1" + str(i), menuPress)
app.addSubMenu('Config', "Background Color")
app.addMenuList("Background Color", ["blue", "green", "white", "red", "black", "grey"], menuPress)

app.startTabbedFrame("Channels",1,0,3)
app.startTab("console")
app.addListBox("consoleList")
app.addListItem("consoleList", "Successfully connected to server")
app.stopTab()
app.stopTabbedFrame()

app.addLabelEntry("Entry",2,0,2).bind("<Return>", send)
app.bindKey("<Up>", lastMessage)
app.setEntryDefault("Entry","Enter your message/command here.")
app.addButton("Send", send,2,2,3)

app.addStatusbar(fields=1)
app.setStatusbar("Connection Status",0)
app.setStatusbarBg("green", 0)

app.startSubWindow("Connect")
app.addLabelEntry("Server")
app.addLabelEntry("Port")
app.addLabelEntry("Nickname")
app.addLabelEntry("Autojoin")
app.addLabelSecretEntry("Autojoin Password")
app.setEntryDefault("Server", "127.0.0.1")
app.setEntryDefault("Nickname", "guest")
app.setEntry("Port", "6667")
app.addButtons(["Connect", "Cancel"], press)
app.stopSubWindow()

# Start GUI and set end condition
app.go(startWindow="Connect")
app.setStopFunction(on_closing())
