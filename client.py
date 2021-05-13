import io
import logging
import socket
import os
import platform
import time
import multiprocessing


#P2P request
# Request to get the RFC information
from multiprocessing import Process, freeze_support


def  get_RFC_request(RFC_number, cl_hostName):
    message = "GET RFC " + str(RFC_number) + " P2P-CI/1.0 \r\n"\
        "Host: " + str(cl_hostName) + " \r\n"\
        "OS: " + os_inform + " \r\n\r\n"
    return message 


# P2S Reqeust
# Request to add RFC number and title 
def add_RFC_request(RFC_number, RFC_title, cl_hostName, cl_port_number):
    message = "ADD RFC " + str(RFC_number) + " P2P-CI/1.0 \r\n"\
            "Host: " + str(cl_hostName) + " \r\n"\
            "Port: " + str(cl_port_number) + " \r\n"\
            "Title: " + str(RFC_title) + " \r\n\r\n"
    return message

# Request to lookUp RFC information
def lookUp_RFC_request(RFC_number, RFC_title, cl_hostName, cl_port_number):
    message = "LOOKUP RFC " + str(RFC_number) + " P2P-CI/1.0 \r\n"\
            "Host: " + str(cl_hostName) + " \r\n"\
            "Port: " + str(cl_port_number) + " \r\n"\
            "Title: " + str(RFC_title) + " \r\n\r\n"
    return message


# Request to list RFC information
def list_RFC_request(client_hostname, upload_client_port_number):
    message = "LIST ALL P2P-CI/1.0 \r\n"\
    "Host: "+str(client_hostname)+" \r\n"\
	"Port: "+str(upload_client_port_number)+" \r\n\r\n"
    return message

##################################################################################
# Johns code for Peer 2 Peer connection upload/download
#################################################################################
def down_RFC(hostName, peerName, peerPort, curSocket, rfcNum, serverName, portAddress):
    # establish connection
    downloadSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    downloadSock.connect((peerName, peerPort))
    # send request
    msg = ("GET" + " " + str(rfcNum) + " " + "P2P-CI/1.0" + " \r\n" +
                   "Host: " + hostName + " \r\n" +
                   "OS: " + platform.system() + " " + platform.version() + " \r\n\r\n")
    downloadSock.send(msg.encode())
    #get header back
    arr = downloadSock.recv(1024).decode()
    arr.split()
    print(f'\r\nResponse to GET from peer:\r\n{arr}')
    file = io.open(os.getcwd() + "/RFC/rfc" + str(rfcNum) + ".txt", mode='a')
    print("Downloading...\r\n")
    while True:
        peerReply = downloadSock.recv(1024).decode()
        if not peerReply:
            break
        file.write(peerReply)
    file.close()
    downloadSock.close()
    print("Download Complete\r\n")
    return


def hasRFC(rfcNum):
    rfcFileName = "rfc" + str(rfcNum) + ".txt"
    for file in os.listdir(os.getcwd() + "/RFC"):
        if (file == rfcFileName):
            return True
    return False


def processRequest(connectionSocket):
    request = connectionSocket.recv(1024)
    request = request.decode()
    dataArr = request.split()
    statusCode = 200
    statusMessage = "OK"
    if (dataArr[0] != "GET" or dataArr[3] != "Host:" or dataArr[5] != "OS:"):
        statusCode = 400
        statusMessage = "Bad Request"
    elif (dataArr[2] != "P2P-CI/1.0"):
        statusCode = 505
        statusMessage = "P2P-CI Version Not Supported"
    elif not hasRFC(dataArr[1]):          #dataArr[2] is the RFC number
        statusCode = 404
        statusMessage = "Not Found"

    requestedFile = "RFC/rfc" + dataArr[1] + ".txt"
    # establish and send header
    reply = "P2P-CI/1.0 " + str(statusCode) + " " + statusMessage + " \r\n"
    reply += time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime()) + " GMT \r\n"
    reply += "OS: " + platform.system() + " " + platform.version() + " \r\n"
    reply += "Last-Modified: " + time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime(os.stat(requestedFile)[8])) + " GMT \r\n"
    reply += "Content-Length: " + str(os.stat(requestedFile)[6]) + " \r\n"
    reply += "Content-Type: text/text" + " \r\n"
    reply += " \r\n"

    connectionSocket.send(reply.encode())
    # send file data after header
    if statusCode == 200:
        rfcFile = open("RFC/rfc" + dataArr[1] + ".txt", "r")
        while True:
            fileContents = rfcFile.read(1024)
            if fileContents == '':
                break
            connectionSocket.send(fileContents.encode())
    connectionSocket.shutdown(socket.SHUT_RDWR)
    rfcFile.close()
    print("SERVER: Request has been responded to.")
    exit(0)


def up_RFCs_SERVER(peerServSock):

    while True:
        connectionSocket, address = peerServSock.accept()
        print("SERVER: A Peer has requested an RFC from you...")
        proc = Process(target=processRequest, args=(connectionSocket,))
        proc.start()

def up_RFCs_INIT(peerServPort):

    peerServSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peerServSock.bind(('', peerServPort))
    peerServSock.listen()

    up_RFCs_SERVER(peerServSock)
    return


##################################################################################

########### User Interface for the program#########
########### BY TaeJoon Kim
if __name__ == '__main__':
    freeze_support()

    # OS infomatipn

    os_inform = platform.platform()
    portAddress = 7734
    serverName = socket.gethostname()

    # Connecting to server using TCP
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((serverName, portAddress))
    print(f"The server({serverName}) and the port({portAddress})is now connected")

    # Define Host name of the client
    cl_hostName = clientSocket.getsockname()[0]
    cl_port_number = int(input("What port number would you like to listen to request on between 49152-65535: "))
    while cl_port_number < 49152 or cl_port_number > 65535:
        cl_port_number = int(input("Please reenter port number between 49152-65535: "))

    p = Process(target=up_RFCs_INIT, args=(cl_port_number,))
    p.start()
    isTrue = True
    while isTrue:
        print("Enter the behavior you want to operate")
        print("1.ADD 2.LIST 3.LOOKUP 4.GET 5.UPVOTE 6.QUIT")
        user_input = int(input())

        # when the user selects ADD option
        if user_input == 1:

            input_rfc_number = input("RFC Number: ")
            while not str(input_rfc_number).isnumeric() or int(input_rfc_number) < 1:
                input_rfc_number = input("Please enter a valid rfc number: ")
            input_rfc_title = input("RFC Title: ")

            RFC_filepath = os.getcwd() + "/RFC/rfc" + str(input_rfc_number) + ".txt"
            if os.path.isfile(RFC_filepath):
                message = add_RFC_request(input_rfc_number, input_rfc_title, cl_hostName, cl_port_number)
                print(f"ADD request for the server:\r\n{message}")
                clientSocket.send(message.encode())
                res_from_server = clientSocket.recv(1024).decode()
                print(f"Response to ADD request from the server:\r\n{res_from_server}")
            else: 
                print("File does not exist in the directory")

        # When the user selects LIST option
        elif user_input == 2:
            # List request sent to the server
            message = list_RFC_request(cl_hostName, cl_port_number)
            print(f"LIST request for the server: \r\n{message}")
            # Send the LIST request to the server
            clientSocket.send(message.encode())
            res_from_server = clientSocket.recv(10000)
            print(f"Response to LIST request from the server: \r\n{res_from_server.decode()}")
        # When the user selects GET option
        elif user_input == 3:

            input_rfc_number = int(input('RFC Number: '))
            input_rfc_title = input("RFC Title: ")

            message = lookUp_RFC_request(input_rfc_number, input_rfc_title, cl_hostName, cl_port_number)

            print(f"LOOKUP request for the server: \r\n{message}")

            # Send the LOOKUP request to the server
            clientSocket.send(message.encode())
            res_from_server = clientSocket.recv(1024)
            print(f"Response to LOOKUP request from the server: \r\n{res_from_server.decode()}")
        elif user_input == 4:
            input_rfc_number = int(input("RFC Number: "))
            if hasRFC(input_rfc_number):
                print("You can't download RFCs that you already have. Delete your version and resubmit to download\r\n")
            else:
                input_rfc_title = input("RFC Title: ")
                hostName = input("Enter name of peer: ")
                hostPort = int(input("Enter port of peer: "))
                down_RFC(cl_hostName, hostName, hostPort, clientSocket, input_rfc_number, serverName, portAddress)

        elif user_input == 5:
            upvoteHostname = input("Hostname: ")
            upvotePortNum = int(input("Host Port Number: "))
            if upvoteHostname == cl_hostName and int(upvotePortNum) == int(cl_port_number):
                print("You cannot upvote yourself.\r\n")
            else:
                message = f"UPVOTE \r\nHost: {upvoteHostname} \r\nPort: {upvotePortNum} \r\n\r\n"
                clientSocket.send(message.encode())

                res_from_server = clientSocket.recv(1024)
                print(f"Response to UPVOTE request from the server: \r\n{res_from_server.decode()}")

        elif user_input == 6:
            message = "QUIT \r\nHost: " + cl_hostName + " \r\n" + "Port: "+str(cl_port_number) + " \r\n\r\n"
            clientSocket.send(message.encode())
            clientSocket.close()
            isTrue = False
            p.kill()
            exit(0)
        else: 
            print("You should enter number 1 to 6")

