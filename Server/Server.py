# -*- coding: utf-8 -*-
"""
Created on Tue Nov  6 09:59:18 2018

@author: zschaub
"""

import socket

serverPort = 9999

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)

while (True):
    connectionSocket, addr = serverSocket.accept()
    print("Session Started with" + str(addr))

    while (True):
        inputMessage = connectionSocket.recv(1024).decode()
        if inputMessage == "/end":
            print("The Session Ended by Client")
            break
        print("Client: " + inputMessage)
        outputMessage = input()
        connectionSocket.send(outputMessage.encode())
        if outputMessage == "/end":
            print("The Session Ended by Server")
            break
    connectionSocket.close()