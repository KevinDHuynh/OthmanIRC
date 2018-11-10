# -*- coding: utf-8 -*-
"""
Created on Tue Nov  6 09:59:28 2018

@author: zschaub
"""

import socket
serverName = 'localhost'
serverPort = 9999

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((serverName,serverPort))
print("Session Started")

while (True):
    outputMessage = input()
    clientSocket.send(outputMessage.encode())
    if outputMessage == "/end":
        print("The Session Ended by Client")
        break
    inputMessage = clientSocket.recv(1024).decode()
    if inputMessage == "/end":
        print("The Session Ended by Server")
        break
    print ('Server:', inputMessage)
clientSocket.close()