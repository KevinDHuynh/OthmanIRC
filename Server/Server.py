import _thread
import time
import socket  # get socket constructor and constants

myHost = ''  # server machine, '' means local host
myPort = 6667  # listen on a non-reserved port number

clients = {}
channels = {}
claimedusernames = {}

sockobj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sockobj.bind((myHost, myPort))
sockobj.listen(10)


# channel class, Name and Password for Channel
# If password = ' ' a password is not required to join the server
# handles what users are in the channel and the channel infomation
class channel:

    def __init__(self, name, password=' '):
        self.name = name
        self.password = password
        # connectedclients[connection] = client
        self.connectedclients = {}
        channels[name] = self


# client class
# handles user data and connection
class client:

    def __init__(self, connection, address, password, nickname, autojoin="General"):
        self.connection = connection
        self.address = address
        self.password = password
        self.nickname = get_nickname(nickname)
        self.channel = {}
        if autojoin in channels and channels[autojoin].password == password:
            client_connect_channel(channels[autojoin], self)
            self.channel = channels[autojoin]
        else:
            client_connect_channel(channels["General"], self)
            self.channel = channels["General"]
            clients[connection] = self


# Connects cient to the channel if the password is correct or the server password is ' '
def client_connect_channel(channelname, client, password=' '):
    if channelname in channels:
        if channels[channelname].password == password or channels[channelname].password == ' ':
            channel.connectedclients[client.connection] = client
            client.channel[channelname] = channels[channelname]
            return True
    return False


# creates client when it first connects
# data should be in format password:nickname:autojoin
def clientFirstConnect(connection, address, data):
    password, nickname, autojoin = data.split(':')
    clients[connection] = client(connection, address, password, nickname, autojoin)


# return current time
def now():
    return time.ctime(time.time())


# returns an available nickname
# if nickname is taken will use get_nickname_num if name is taken and append a number to end of nickname
def get_nickname(nickname):
    if nickname in claimedusernames:
        nickname = get_nickname_num(nickname, 1)
    return nickname


# used with get_nickname
def get_nickname_num(nickname, num):
    if nickname.append(str(num)) in claimedusernames:
        nickname = get_nickname_num(nickname, num + 1)
    return nickname


# sends message to all clients in channel from user with time stamp
def server_send_channelmessage(channel, user, data):
    message = str(now() + ':' + channel + ':' + user + ':' + data)
    for connection in channels[channel].connectedclients:
        connection.send(message.encode())


def handleClient(connection):
    clientFirstConnect(connection.recv(1024).decode())
    connection.send(str(clients[connection].username) + ":" + str(clients[connection].channel))
    while True:
        data = connection.recv(1024).decode()
        header, data = data.split(":")
        if header in channel:
            server_send_channelmessage(header, clients[connection].nickname, data)
    connection.close()


def dispatcher():  # listen until process killed
    while True:  # wait for next connection,
        connection, address = sockobj.accept()  # pass to thread for service
        clients[address] = connection
        print('Server connected by', address)
        print('at', now())
        for x in clients:
            print(str(x))
        _thread.start_new(handleClient, (connection,))


generalChannel = channel("General", ' ')

dispatcher()
