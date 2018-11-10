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


class channel:

    def __init__(self, name, password=''):
        self.name = name
        self.password = password
        self.connectedclients = {}


class client:

    def __init__(self, connection, address, password, nickname, autojoin="General"):
        self.connection = connection
        self.address = address
        self.password = password
        self.nickname = get_nickname(nickname)
        if autojoin in channels and channels[autojoin].password == password:
            client_connect_channel(channels[autojoin], self)
            self.channel = channels[autojoin]
        else:
            client_connect_channel(channels["General"], self)
            self.channel = channels["General"]


def client_connect_channel(channel, client):
    channel.connectedclients[client.connection] = client


def clientFirstConnect(connection, address, data):
    password, nickname, autojoin = data.split(':')
    clients[connection] = client(connection, address, password, nickname, autojoin)


def now():
    return time.ctime(time.time())

def get_nickname(nickname):

    if nickname in claimedusernames:
        nickname = get_nickname_num(nickname, 1)
    return nickname

def get_nickname_num(nickname, num):
    if nickname.append(str(num)) in claimedusernames:
        nickname = get_nickname_num(nickname, num + 1)
    return nickname

def handleClient(connection):
    clientFirstConnect(connection.recv(1024).decode())
    connection.send(str(clients[connection].username) + ":" + str(clients[connection].channel))
    while True:
        data = connection.recv(1024).decode()
        if not data: break
        connection.send(('Echo=>%s at %s' % (data, now())).encode())
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
