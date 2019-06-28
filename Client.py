import codecs
import glob
import pickle
import re
import socket
import webbrowser
import urllib


#import numpy as np
# import cv2
import cv2
import numpy as np

HOST = '127.0.0.50'  # The server's hostname or IP address
PORT = 5445    # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientSocket:
    clientSocket.connect((HOST, PORT))
    while True:
        message=  input("Enter your MESSAGE:  ")




        GetPattern= 'GET\s\w+.(txt|html|jpg|jpeg)\s\d+.\d+.\d+.\d+(\s*\d*)'
        GetResult = re.match(GetPattern, message)
        PostPattern= 'POST\s\w+.(txt|html|jpg|jpeg)\s\d+.\d+.\d+.\d+(\s*\d*)'
        PostResult = re.match(PostPattern, message)
        flag = 1
        if PostResult:
            messageTokens_1 = re.split("\s", message, 4)
            try:
                tempFile = open("ClientData/" + messageTokens_1[1], "r")

            except FileNotFoundError:
                    print("404 not found")
                    flag=0
            finally:
                print("")
        if flag==1 :
            clientSocket.sendall(message.encode())
            statusMessage = clientSocket.recv(40960).decode()
            print(statusMessage)

            if statusMessage!="HTTP/1.0 404 NOT FOUND\r\n":
                if GetResult:
                    modifiedMessage = clientSocket.recv(10240000).decode()
                    messageTokens= re.split("\s", message, 4)
                    if messageTokens[1].endswith(".txt"):
                        f = open("ClientData/"+messageTokens[1], "w+")

                        temp = re.split("\n", modifiedMessage, 50000)
                        for i in range(0, len(temp)):
                            f.write(temp[i]+"\n")
                            print(temp[i]+"\n")
                        f.close()

                    elif messageTokens[1].endswith(".jpeg"):
                        size = modifiedMessage
                        modifiedMessage = clientSocket.recv(409600000)
                        flatarray = [x for x in modifiedMessage]
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
                            cv2.imwrite('ClientData/' + messageTokens[1], c)


                    elif messageTokens[1].endswith(".jpg") :
                        size = modifiedMessage
                        modifiedMessage = clientSocket.recv(409600000)
                        flatarray = [x for x in modifiedMessage]
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
                            cv2.imwrite('ClientData/' + messageTokens[1], c)




                    elif messageTokens[1].endswith(".html"):
                        print("modified "+modifiedMessage)
                        f = open("ClientData/"+messageTokens[1], "w+")
                        temp = re.split("\n", modifiedMessage, 50000)
                        for i in range(0, len(temp)):
                            f.write(temp[i] + "\n")
                        f.close()
                        url = "ClientData/"+messageTokens[1]
                        new=2
                        webbrowser.open(url, new=new)

                elif PostResult:
                    messageTokens = re.split("\s", message, 4)
                    fileFoundFlag = 1
                    if messageTokens[1].endswith(".txt"):
                        try:
                            file = open("ClientData/" + messageTokens[1], "r")

                        except FileNotFoundError:

                            message = "Error 404 Not Found"
                            print(message)
                            clientSocket.sendall(message.encode())
                            fileFoundFlag = 0
                            break

                        finally:
                            print("")

                        if fileFoundFlag:
                            message = file.read()
                            clientSocket.sendall(message.encode())
                            print(file.read())  # send data from here
                        else:
                            print("error 404 ")
                    elif messageTokens[1].endswith(".jpg"):
                        path = glob.glob("ClientData/" + messageTokens[1])
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
                                 clientSocket.send(str(size).encode(), 6)
                                 clientSocket.send(bytesarray)
                    elif messageTokens[1].endswith(".jpeg"):
                        path = glob.glob("ClientData/" + messageTokens[1])
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
                                 clientSocket.send(str(size).encode(), 6)
                                 clientSocket.send(bytesarray)

                    elif messageTokens[1].endswith(".html"):
                        fileFoundFlag = 1
                        try:
                            f = codecs.open("ClientData/" + messageTokens[1], 'r')
                        except FileNotFoundError:
                            print("Error 404 Not Found")
                            message = "Error 404 Not Found"
                            clientSocket.sendall(message.encode())
                            fileFoundFlag = 0

                        finally:
                            print("")

                        if fileFoundFlag:
                            message = f.read()
                            clientSocket.sendall(message.encode())
                            print(message)  # send data from here
                        else:
                            print("error 404 ")
    ###close the connection




