import _thread
import socket

myHost = ''
myPort = 6667
version = '0.0.3'
defaultchannel = "#general"
# clients[connection] = client
clients = {}
# channels[channelName] = channel
channels = {}
# claimedusernames = [name1, name2, name3]
claimedusernames = []

# Creates a TCP Server with Port# 6667
sockobj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sockobj.bind((myHost, myPort))
sockobj.listen(10)


# channel class, Name and Password for Channel
# If password = ' ' a password is not required to join the server
# handles what users are in the channel and the channel information
class Channel:

    def __init__(self, name, password=' '):
        self.name = name
        self.password = password
        self.ispublic = False
        if password == ' ':
            self.ispublic = True
        # connectedclients[connection] = client
        self.connectedclients = {}
        channels[name] = self


# client class
# handles user data and connection
class Client:

    def __init__(self, connection, username):
        clients[connection] = self
        self.connection = connection
        self.username = get_username(username)
        self.lastmsgfrom = self
        claimedusernames.append(self.username)
        # List of Channels the Client is in, contains names of the channel
        self.channelsin = []
        client_connect_channel(defaultchannel, connection)

    def strchannelsin(self):
        c = ""
        for x in self.channelsin:
            c = c + x
        return c


# Connects client to the channel if the password is correct or the server password is ' '
# Adds client to connectedclients
# Adds channel to client.channelsin
def client_connect_channel(channelname, connection, password=' '):
    connectingclient = clients[connection]
    if channelname in channels:
        if channels[channelname].password == password or channels[channelname].password == ' ':
            channels[channelname].connectedclients[connection] = connectingclient
            connectingclient.channelsin.append(channelname)
            announce_connected_client(connection, channelname)
            return True
    return False


# removes client from specified channel
def client_remove_channel(channelname, connection):
    clients[connection].channelsin.remove(channelname)
    channels[channelname].connectedclients.pop(connection)


# announce when user is connected to channel
def announce_connected_client(connection, channelname):
    message = str(channelname + "&&" + "Server&&" + clients[connection].username + " has connected to " + channelname)
    for c in channels[channelname].connectedclients:
        if c != connection:
            c.send(message.encode())


# creates client when it first connects
# data should be in format password:username:autojoin
def client_first_connect(connection, data):
    Client(connection, data)
    print(clients[connection].username + " connected to " + clients[connection].strchannelsin())


# returns an available nickname
# if nickname is taken will use get_nickname_num if name is taken and append a number to end of nickname
def get_username(username):
    username = username.replace(" ", "")
    if username in claimedusernames and username != "Server":
        username = get_username_num(username, 1)
    return username


# used with get_username
def get_username_num(username, num):
    name = username + str(num)
    if name in claimedusernames:
        return get_username_num(username, num + 1)
    return name


# return true if user is in channel, false if otherwise
def user_in_channel(connection, channelname):
    return channelname in clients[connection].channelsin


# sends message to all clients in channel from user with time stamp
def server_send_channelmessage(channelname, user, data):
    message = str(channelname + "&&" + user + "&&" + data)
    for connection in clients:
        clientinchannel = clients[connection]
        if clientinchannel.username != user:
            connection.send(message.encode())


"""Commands from Client"""


# adds user to channel in data, if channel has a password it should be in data.
# returns "True&&" + data if connected (Where data is the channel name)
# return "False&&Password" if bad password
# return "False&&" + data if channel doesn't exist (Where data is the channel name)
def join(connection, data):
    if not data.startswith("#"):
        data = "#" + data
    try:
        data, password = data.split("&&")
        if data in channels:
            if client_connect_channel(data, connection, password):
                return "True&&" + data
        else:
            return "False&&Password"
    except ValueError:
        if client_connect_channel(data, connection):
            return "True&&" + data
        else:
            return "False&&" + data


# Sends a msg from connection to user containing message, contained in data
# Returns "True&&" + user if message sent
# Returns "False&&User" + user + " not found" if user could not be found
# Returns "False&&Message Format Error" if data is not formatted correctly
def msg(connection, data):
    print(data)
    try:
        user, message = data.split("&&")
        print(user)
        print(message)

        message = "/msg&&" + clients[connection].username + "&&" + message
        for x in clients:
            if clients[x].username == user:
                print("User found for msg")
                x.send(message.encode())
                x.lastmsgfrom = connection
                return "True&&" + user
    except ValueError:
        return "False&&Message Format Error"
    print("user not found for msg")
    return "False&&User " + user + " not found"


# Sends message to the last user to private message you
# Returns "True&&" + clients[connection].lastmsgfrom if message sent correctly
# returns "False&&User " + clients[connection].lastmsgfrom + " not found" if user not found
def reply(connection, data):
    if clients[connection].lastmsgfrom in clients:
        clients[connection].lastmsgfrom.send(clients[connection].username + "&&" + data.encode())
        clients[clients[connection].lastmsgfrom].lastmsgfrom = connection
        return "True&&" + clients[connection].lastmsgfrom
    return "False&&User " + clients[connection].lastmsgfrom + " not found"


# Returns "pong"
def ping(connection):
    print("ping from" + clients[connection].username)
    return "pong"


# change client name
# returns newname
def nick(connection, username):
    claimedusernames.remove(clients[connection].username)
    newname = get_username(username)
    claimedusernames.append(newname)
    clients[connection].username = newname
    return newname


# lists all public servers (servers without password)
# returns #defaultChannel, #publicChannel ..... , #publicChannel
def list_public_channels():
    channel_list = defaultchannel
    for x in channels:
        if channels[x].ispublic and not x == defaultchannel:
            channel_list = channel_list + ", " + x
    return channel_list


# if connection is in the channel then return list of all names in channel
# returns "clientsusername, username, username..., username"
# if connection is not in the channel then return "False"
def names(connection, channelname):
    list_of_names = clients[connection].username
    if channelname in clients[connection].channelsin:
        for name in channels[channelname].connectedclients:
            if name not in clients[connection].username:
                list_of_names = list_of_names + ", " + name
        return list_of_names
    return False


"""End Commands from Client"""


# Removes client from
def clientremoved(connection, error="for unknown reason"):
    print(str(clients[connection].username) + " removed from server " + str(error))
    # remove client from all connected channels connectedclients list
    for channelname in clients[connection].channelsin:
        channels[channelname].connectedclients.pop(connection)
    claimedusernames.remove(clients[connection].username)
    clients.pop(connection)


# Handles the client with the thread
def handle_client(connection):
    client_first_connect(connection, connection.recv(1024).decode())
    thisclient = clients[connection]
    connection.send(("/init&&" + str(thisclient.username) + "&&" + thisclient.strchannelsin()).encode())

    while True:
        try:
            data = connection.recv(1024).decode()
            print("Received from " + thisclient.username + ":" + data)
            header, data = data.split("&&", 1)
            # Checks and uses command from Client
            if header[:1] == '/':
                if header == "/quit":
                    clientremoved(connection, "closed by client")
                    break
                elif header == "/join":
                    connection.send(("/join&&" + str(join(connection, data))).encode())
                elif header == "/msg":
                    print("Received Message")
                    connection.send(("/msg&&" + str(msg(connection, data))).encode())
                elif header == "/reply":
                    connection.send(("/reply&&" + str(reply(connection, data))).encode())
                elif header == "/ping":
                    ping(connection)
                    connection.send("/ping".encode())
                elif header == "/nick":
                    connection.send(("/nick&&" + str(nick(connection, data))).encode())
                elif header == "/list":
                    connection.send(("/list&&" + list_public_channels()).encode())
                elif header == "/version":
                    connection.send(("/version&&" + version).encode())
                elif header == "/names":
                    connection.send(("/names&&" + names(connection, data)).encode())
                else:
                    connection.send((header + " is unknown command").encode())

            # Checks and sends message to channel
            elif header[:1] == '#':
                if header in thisclient.channelsin:
                    server_send_channelmessage(header, thisclient.username, data)
                else:
                    connection.send(str(header + " is an unknown channel").encode())
            else:
                connection.send("Unknown Message Format".encode())
        # Connection Randomly Closed by Client
        except ConnectionResetError or ConnectionAbortedError:
            clientremoved(connection, "because connection was forcibly closed by the client")
            break
        # Split function fails
        except ValueError:
            connection.send("Unknown Message Format".encode())
            continue

    connection.close()


# listen until process killed
def dispatcher():
    while True:  # wait for next connection
        connection, address = sockobj.accept()  # pass to thread for service
        _thread.start_new(handle_client, (connection,))


# Creates the general channel
Channel(defaultchannel)
Channel("#seceret", "1234")
Channel("#test")

dispatcher()
