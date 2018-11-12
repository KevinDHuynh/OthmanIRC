import _thread
import socket  # get socket constructor and constants

myHost = ''  # server machine, '' means local host
myPort = 6667  # listen on a non-reserved port number
version = '0.0.1'

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
        self.ispublic = False
        if password == ' ':
            self.ispublic = True
        self.connectedclients = {}
        channels[name] = self


# client class
# handles user data and connection
class client:

    def __init__(self, connection, nickname, autojoin="#general", password = ' '):
        self.connection = connection
        self.password = password
        self.nickname = get_nickname(nickname)
        self.lastmsgfrom = self
        claimednicknames.append(self.nickname)
        #List of Channels the Client is in, contains names of the channel
        self.channelsin = ["#general"]
        client_connect_channel(channels["#general"], self)
        if autojoin !="#general":
            client_connect_channel(autojoin, connection, password)

    def strchannelsin(self):
        c = str(self.channelsin[0])

        for x in self.channelsin:
            if(x != "#general"):
                c = c + " " + x
        return c


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


# removes client from specified channel
def client_remove_channel(channelname, client):
    clients[client].channelsin.remove(channelname)
    channels[channelname].connectedclients.pop(client)


# creates client when it first connects
# data should be in format password:nickname:autojoin
def clientFirstConnect(connection, data):
    password, nickname, autojoin = data.split("&&")
    clients[connection] = client(connection, nickname, autojoin, password)


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


# return true if user is in channel, false if otherwise
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


"""Commands from Client"""


# adds user to channel in data, if channel has a password it should be in data.
# returns true if successful, false otherwise
def join(connection, data):
    try:
        data, password = data.split("&&")
        return client_connect_channel(data, connection, password)
    except ValueError:
        return client_connect_channel(data, connection)

# Sends a msg from connection to user containing message, contained in data
# Returns true if successfully send, false is otherwise
def msg(connection, data):
    try:
        user, message = data.split("&&")
        message = str(clients[connection].nickname) + "&&" + message
        for x in clients:
            if x.nickname == user:
                x.send(message.encode())
                x.lastmsgfrom = connection
                return True
    except:
        return False
    return False


def reply(connection, data):
    try:
        if clients[connection].lastmsgfrom in clients:
            clients[connection].lastmsgfrom.send(data.encode())
            return True
    except:
        return False
    return False


def ping(connection):
    print("ping from" + clients[connection].nickname)
    connection.send("pong".encode())


"""End Commands from Client"""


def clientremoved(connection, error="unknown reason"):
    print(str(clients[connection].nickname) + " removed from server because " + str(error))


def handleClient(connection):
    clientFirstConnect(connection, connection.recv(1024).decode())
    thisclient = clients[connection]
    connection.send((str(thisclient.nickname) + "&&" + thisclient.strchannelsin()).encode())
    print(str(thisclient.nickname) + "&&" + str(thisclient.strchannelsin()))

    while True:
        try:
            data = connection.recv(1024).decode()
            print(data)
            header, data = data.split("&&")
            # Checks and uses command from Client
            if header[:1] == '/':
                if header == "/quit":
                    clientremoved(connection, "closed by client")
                    break
                elif header == "/join":
                    connection.send(join(connection, data).encode())
                elif header == "/msg":
                    connection.send(msg(connection, data).encode())
                elif header == "/reply":
                    connection.send(reply(connection, data).encode())
                elif header == "/ping":
                    ping(connection)
                else:
                    connection.send(str(header + " is unknown command").encode())
            # Checks and sends message to channel
            elif header[:1] == '#':
                if header in thisclient.channelsin:
                    server_send_channelmessage(header, thisclient.nickname, data)
                else:
                    connection.send(str(header + " is an unknown channel").encode())
            else:
                connection.send("Unknown Message Format".encode())
        except ConnectionResetError:
            clientremoved(connection, "connection was forcibly closed by the client")
            break
        except ValueError:
            connection.send("Unknown Message Format".encode())
            continue

    connection.close()


def dispatcher():  # listen until process killed
    while True:  # wait for next connection
        connection, address = sockobj.accept()  # pass to thread for service
        _thread.start_new(handleClient, (connection,))


generalChannel = channel("#general", ' ')
dispatcher()
