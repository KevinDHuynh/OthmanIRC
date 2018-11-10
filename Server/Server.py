# -*- coding: utf-8 -*-

import _thread
import time
import socket

import _thread
import time
import socket                     # get socket constructor and constants

myHost = ''                              # server machine, '' means local host
myPort = 6667                           # listen on a non-reserved port number

clients = {}
channels = {}

sockobj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)           # make a TCP socket object
sockobj.bind((myHost, myPort))                   # bind it to server port number
sockobj.listen(10)                                # allow up to 10 pending connects

class channel:

    def __init__(self, name, password=''):
        self.name = name
        self.password = password
        self.connectedclients = {}


class client:

    def __init__(self, connection, address, password, nickname, autojoin):
        self.connection = connection
        self.address = address
        self.password = password
        self.nickname = nickname
        if autojoin in channels:
            if channels[autojoin].password == password:

        self.channel = autojoin

def client_connect_channel(channel, client):
    channel.connectedclients[client.connection] = client

def clientFirstConnect(connection, address, data):
    password, nickname, autojoin = data.split(':')
    clients[connection] = client(connection, address, password, nickname, autojoin)

def now( ):
    return time.ctime(time.time( ))               # current time on the server

def handleClient(connection):                    # in spawned thread: reply
    clientFirstConnect(connection.recv(1024).decode())
    while True:                                  # read, write a client socket
        data = connection.recv(1024).decode()
        if not data: break
        connection.send(('Echo=>%s at %s' % (data, now( ))).encode())
    connection.close( )

def dispatcher( ):                                # listen until process killed
    while True:                                    # wait for next connection,
        connection, address = sockobj.accept( )   # pass to thread for service
        clients[address] = connection
        print ('Server connected by', address)
        print ('at', now( ))
        for x in clients:
            print(str(x))
        _thread.start_new(handleClient, (connection,))

generalChannel = channel("General", ' ')
dispatcher( )