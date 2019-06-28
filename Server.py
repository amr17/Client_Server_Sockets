import glob
import pickle
import re
import codecs

import socket
import sys

#import cv2
import random

# import cv2
import webbrowser

import cv2
import numpy as np

HOST = '127.0.0.50'  # Standard loopback interface address (localhost)
PORT = 5445      # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serverSocket:
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSocket.bind((HOST, PORT))
    serverSocket.listen()
    conn, addr = serverSocket.accept()

    with conn:
        print('Connected by', addr)
        while True:
            message = conn.recv(1024).decode()
            GetPattern= 'GET\s\w+.(txt|html|jpg|jpeg)\s\d+.\d+.\d+.\d+(\s*\d*)'
            PostPattern= 'POST\s\w+.(txt|html|jpg|jpeg)\s\d+.\d+.\d+.\d+(\s*\d*)'
            GetResult=re.match(GetPattern,message)
            PostResult=re.match(PostPattern,message)
            print(message)


            if GetResult :
                tokens=[]
                temp = re.split("\s", message, 4)
                for i in range(0,len(temp)):                #copy temp array into tokens array
                    tokens.append(temp[i])
                if i==2:
                    tokens.append("80")                      # set to dafault portNumber


                fileFoundFlag = 1

                if tokens[1].endswith(".txt"):                   #For Text Files
                    try:
                        file = open("ServerData/" + tokens[1], "r")

                    except FileNotFoundError:
                        statusMessage="HTTP/1.0 404 NOT FOUND\r\n"
                        conn.sendall(statusMessage.encode())
                        fileFoundFlag = 0


                    finally:
                        print("")

                    if fileFoundFlag:
                        statusMessage = "HTTP/1.0 200 OK\r\n"
                        conn.sendall(statusMessage.encode())
                        message=file.read()
                        conn.sendall(message.encode())
                        #print(file.read())                         #send data from here

                elif tokens[1].endswith(".jpeg"):

                        fileFoundFlag=1

                        path = glob.glob("ServerData/" + tokens[1])
                        if str(path)=="[]":
                            statusMessage = "HTTP/1.0 404 NOT FOUND\r\n"
                            conn.sendall(statusMessage.encode())
                            fileFoundFlag = 0
                        if fileFoundFlag==1 :
                            statusMessage = "HTTP/1.0 200 OK\r\n"
                            conn.sendall(statusMessage.encode())
                            for file in path:
                             pixels = cv2.imread(file)
                             rows, cols, colors = pixels.shape
                             pixels_size = rows * cols * colors
                             flatarray = pixels.reshape(pixels_size)
                             bytesarray = bytearray()
                             size = len(flatarray) - 1
                             for i in range(0, len(flatarray)):
                                 bytesarray.append(flatarray[i])
                             bytesarray.append(rows)
                             bytesarray.append(cols)
                             bytesarray.append(colors)
                             conn.send(str(size).encode(), 6)
                             conn.send(bytesarray)
                elif tokens[1].endswith(".jpg"):
                    fileFoundFlag = 1
                    path = glob.glob("ServerData/" + tokens[1])
                    if str(path) == "[]":
                        statusMessage = "HTTP/1.0 404 NOT FOUND\r\n"
                        conn.sendall(statusMessage.encode())
                        fileFoundFlag = 0
                    if fileFoundFlag == 1:
                        statusMessage = "HTTP/1.0 200 OK\r\n"
                        conn.sendall(statusMessage.encode())
                        for file in path:
                            pixels = cv2.imread(file)
                            rows, cols, colors = pixels.shape
                            pixels_size = rows * cols * colors
                            flatarray = pixels.reshape(pixels_size)
                            bytesarray = bytearray()
                            size = len(flatarray) - 1
                            for i in range(0, len(flatarray)):
                                bytesarray.append(flatarray[i])
                            bytesarray.append(rows)
                            bytesarray.append(cols)
                            bytesarray.append(colors)
                            conn.send(str(size).encode(), 6)
                            conn.send(bytesarray)

                elif tokens[1].endswith(".html"):
                    fileFoundFlag = 1
                    try:
                        f = codecs.open("ServerData/" + tokens[1], 'r')
                    except FileNotFoundError:
                        statusMessage = "HTTP/1.0 404 NOT FOUND\r\n"
                        conn.sendall(statusMessage.encode())
                        fileFoundFlag = 0

                    finally:
                        print("")

                    if fileFoundFlag:
                        statusMessage = "HTTP/1.0 200 OK\r\n"
                        conn.sendall(statusMessage.encode())
                        message = f.read()
                        conn.sendall(message.encode())
                       # print(message)  # send data from here


            elif PostResult:
                tokens_P = []
                temp_P = re.split("\s", message, 4)
                for i in range(0, len(temp_P)):  # copy temp array into tokens array
                    tokens_P.append(temp_P[i])
                if i == 2:
                    tokens_P.append("80")  # set to dafault portNumber

                fileFoundFlag = 1
                statusMessage = "HTTP/1.0 200 OK\r\n"
                conn.sendall(statusMessage.encode())

                if tokens_P[1].endswith(".txt"):  # For Text Files


                    message=conn.recv(4096000).decode()
                    print(message)

                    f = open("ServerData/" + tokens_P[1], "w+")
                    temp = re.split("\n", message, 50000)
                    for i in range(0, len(temp)):
                        f.write(temp[i] + "\n")

                    f.close()
                elif tokens_P[1].endswith(".jpg"):

                        size =conn.recv(1024).decode()
                        message = conn.recv(409600000)
                        flatarray = [x for x in message]
                        rows = flatarray[len(flatarray) - 3]
                        cols = flatarray[len(flatarray) - 2]
                        colors = flatarray[len(flatarray) - 1]
                        flatarray.pop((len(flatarray) - 1))
                        flatarray.pop((len(flatarray) - 1))
                        flatarray.pop((len(flatarray) - 1))
                        array = np.asarray(flatarray)
                        size = int(size)
                        print(size, len(flatarray) - 1)
                        if size == (len(flatarray) - 1):
                            tempimage = array.reshape(rows, cols, colors)
                            c = cv2.cvtColor(tempimage.astype('uint8'), cv2.COLOR_BGR2RGB)
                            cv2.imshow('Color image', c)
                            k = cv2.waitKey(1000)
                            cv2.destroyAllWindows()
                            cv2.imwrite('ServerData/' + tokens_P[1], c)
                elif tokens_P[1].endswith(".jpeg"):
                        size =conn.recv(1024).decode()

                        message = conn.recv(409600000)
                        flatarray = [x for x in message]
                        rows = flatarray[len(flatarray) - 3]
                        cols = flatarray[len(flatarray) - 2]
                        colors = flatarray[len(flatarray) - 1]
                        flatarray.pop((len(flatarray) - 1))
                        flatarray.pop((len(flatarray) - 1))
                        flatarray.pop((len(flatarray) - 1))
                        array = np.asarray(flatarray)
                        size = int(size)
                        print(size, len(flatarray) - 1)
                        if size == (len(flatarray) - 1):
                            tempimage = array.reshape(rows, cols, colors)
                            c = cv2.cvtColor(tempimage.astype('uint8'), cv2.COLOR_BGR2RGB)
                            cv2.imshow('Color image', c)
                            k = cv2.waitKey(1000)
                            cv2.destroyAllWindows()
                            cv2.imwrite('ServerData/' + tokens_P[1], c)
                elif tokens_P[1].endswith(".html"):
                    message=conn.recv(10240000).decode()
                    print( message)
                    f = open("ServerData/" + tokens_P[1], "w+")
                    temp = re.split("\n", message, 50000)
                    for i in range(0, len(temp)):
                        f.write(temp[i] + "\n")
                    f.close()
                    url = "ServerData/" + tokens_P[1]
                    new = 2
                    webbrowser.open(url, new=new)

            else:
                print("SYNTAX ERROR")

