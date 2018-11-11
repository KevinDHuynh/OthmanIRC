import _thread
import socket  # get socket constructor and constants

myHost = ''  # server machine, '' means local host
myPort = 6667  # listen on a non-reserved port number

clients = {}
channels = {}
claimednicknames = []

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
        self.connectedclients = {}
        channels[name] = self


# client class
# handles user data and connection
class client:

    def __init__(self, connection, password, nickname, autojoin="#general"):
        self.connection = connection
        self.password = password
        self.nickname = get_nickname(nickname)
        claimednicknames.append(self.nickname)
        self.channelsin = {}
        if autojoin in channels and channels[autojoin].password == password:
            client_connect_channel(channels[autojoin], self)
            self.channelsin = channels[autojoin]
        else:
            client_connect_channel(channels["#general"], self)
            self.channelsin = channels["#general"]
            clients[connection] = self


# Connects client to the channel if the password is correct or the server password is ' '
def client_connect_channel(channelname, client, password=' '):
    print("client connect channel")
    if channelname in channels:
        print("channelname in channels")
        if channels[channelname].password == password or channels[channelname].password == ' ':
            print("Password Match")
            channels[channelname].connectedclients[client.connection] = client
            client.channel[channelname] = channels[channelname]
            return True
    return False


# creates client when it first connects
# data should be in format password:nickname:autojoin
def clientFirstConnect(connection, data):
    password, nickname, autojoin = data.split("&&")
    clients[connection] = client(connection, password, nickname, autojoin)


# returns an available nickname
# if nickname is taken will use get_nickname_num if name is taken and append a number to end of nickname
def get_nickname(nickname):
    print("test")
    if nickname in claimednicknames:
        nickname = get_nickname_num(nickname, 1)
    return nickname


# used with get_nickname
def get_nickname_num(nickname, num):
    name = nickname + str(num)
    print(name)
    if name in claimednicknames:
        return get_nickname_num(nickname, num + 1)
    return name

def user_in_channel(connection, channelname):
    return channelname in clients[connection].channelsin

# sends message to all clients in channel from user with time stamp
def server_send_channelmessage(channelname, user, data):
    message = str(channelname + "&&" + user + "&&" + data)
    print(channels[channelname].connectedclients)
    for connection in clients:
        client = clients[connection]
        if client.nickname != user:
            connection.send(message.encode())
    print(message)


def handleClient(connection):
    clientFirstConnect(connection, connection.recv(1024).decode())
    connection.send((str(clients[connection].nickname) + "&&" + str(clients[connection].channelsin.name)).encode())
    print(str(clients[connection].nickname) + "&&" + str(clients[connection].channelsin.name))
    while True:
        data = connection.recv(1024).decode()
        print(data)
        header, data = data.split("&&")
        print(header)
        if header in channels:
            server_send_channelmessage(header, clients[connection].nickname, data)

    connection.close()


def dispatcher():  # listen until process killed
    while True:  # wait for next connection
        connection, address = sockobj.accept()  # pass to thread for service
        _thread.start_new(handleClient, (connection,))


generalChannel = channel("#general", ' ')
dispatcher()
