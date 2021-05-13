import logging
from _thread import start_new_thread
from socket import *
import os
import sys
import multiprocessing
import collections
import threading

SERVER_PORT = 7734
# AD_INET: IPv4   SOCK_STREAM: TCP
# Connect serrver to the socket via IPv4 and TCP for the socket stream
serverSocket = socket(AF_INET, SOCK_STREAM)


# peer class
class Peer:
    def __init__(self, hostname, portNum):
        self.hostname = hostname
        self.portNum = portNum
        self.rfcs = collections.deque()
        self.rating = 0


    def addPeerRFC(self, newRFC):
        self.rfcs.append(newRFC)

# list of active peers
peers = []


# rfc class
class RFC:
    def __init__(self, rfcNum, rfcTitle, rfcHostname, portNum):
        self.rfcNum = rfcNum
        self.rfcTitle = rfcTitle
        self.rfcHostname = rfcHostname
        self.portNum = portNum


def handlePeer(sock):
    while True:
        msg = sock.recv(1024)
        msg = msg.decode()
        print(msg)
        if len(msg) == 0:
            sock.close()
            return
        arr = msg.split(' ')

        # Add rfc to the list of rfcs if the name is 'ADD'
        if arr[0] == 'ADD':

            rfcNum = int(arr[2])
            hostName = arr[5]
            portNum = int(arr[7])

            rfcTitleArray = arr[9:-1]
            rfcTitle = rfcTitleArray[0]
            rfcTitleArray = rfcTitleArray[1:]
            for string in rfcTitleArray:
                rfcTitle = rfcTitle + ' ' + string

            addRFC(rfcNum, rfcTitle, hostName, portNum, sock)

        elif arr[0] == 'LIST':
            listAmt = arr[1]
            hostName = arr[4]
            portNum = int(arr[6])

            responseToList(listAmt, hostName, portNum, sock)
        elif arr[0] == 'LOOKUP':
            targetRfc = arr[2]
            responseToLookUp(int(targetRfc), sock)
        elif arr[0] == 'UPVOTE':
            upvoteHostname = arr[2]
            upvotePortNum = int(arr[4])
            responseToUpvote(upvoteHostname, upvotePortNum, sock)
        elif arr[0] == 'QUIT':
            for peer in peers:
                if peer.hostname == arr[2] and int(peer.portNum) == int(arr[4]):
                    peers.remove(peer)
            sock.close()
            break


def responseToUpvote(upvoteHostname, upvotePortNum, sock):
    message = ''
    for peer in peers:
        if peer.hostname == upvoteHostname and peer.portNum == upvotePortNum:
            peer.rating = peer.rating + 1
            message = 'Upvote Successful!\r\n\r\n'
            sock.send(message.encode())
            return
    message = '404 Peer Not Found\r\n\r\n'
    sock.send(message.encode())
    return

# Add a new RFC to the list of RFCs
def addRFC(rfcNum, rfcTitle, rfcHostname, portNum, peerSocket):
    alreadyExist = False
    for peer in peers:
        if peer.hostname == rfcHostname and peer.portNum == portNum:
            peer.addPeerRFC(RFC(rfcNum, rfcTitle, rfcHostname, portNum))
            alreadyExist = True

    if not alreadyExist:
        peer = Peer(rfcHostname, portNum)
        peer.addPeerRFC(RFC(rfcNum, rfcTitle, rfcHostname, portNum))
        peers.append(peer)

    # send a message to the client. TODO: correct message formatting
    msg = f'P2P-CI/1.0 200 OK\r\nRFC {rfcNum} {rfcTitle} {rfcHostname} {portNum}\r\n'
    peerSocket.send(msg.encode())
    return

# List out all RFCs in the server
def responseToList(listAmt, hostname, portNum, sock):
    msg = ''
    if listAmt == 'ALL':
        msg = f'P2P-CI/1.0 200 OK\r\n\r\n'
        for peer in peers:
            for rfc in peer.rfcs:
                msg = msg + f'{rfc.rfcNum} {rfc.rfcTitle} {rfc.rfcHostname} {rfc.portNum} Peer Upvotes: {peer.rating}\r\n'
    else:
        msg = 'Didn\'t specify ALL'
    for peer in peers:
        for rfc in peer.rfcs:
            print(f'{rfc.rfcNum} {rfc.rfcTitle} {rfc.rfcHostname} Peer Upvotes: {peer.rating}\r\n')
    sock.send(msg.encode())




# If the peer decides to look up a certain RFC
def responseToLookUp(rfcNum, sock):
    statusCode = 200
    phrase = 'OK'
    numFound = 0
    listOfMatches = []
    listOfUpvotes = []
    for peer in peers:
        for rfc in peer.rfcs:
            if rfc.rfcNum == rfcNum:
                numFound = numFound + 1
                listOfMatches.append(rfc)
                listOfUpvotes.append(peer.rating)
    if numFound < 1:
        statusCode = 404
        phrase = 'Not Found'
        msg = f'P2P-CI/1.0 {statusCode} {phrase}\r\n\r\n'
        sock.send(msg.encode())
    else:
        msg = f'P2P-CI/1.0 {statusCode} {phrase}\r\n\r\n'
        i = 0
        for rfcFile in listOfMatches:
            msg = msg + f'{rfcFile.rfcNum} {rfcFile.rfcTitle} {rfcFile.rfcHostname} {rfcFile.portNum} Peer Upvotes: {listOfUpvotes[i]}\r\n'
            i = i + 1
        msg = msg + "\r\n"
        sock.send(msg.encode())


# Peer joins the server

def peer_joining(peer):
    while 1:
        msg = peer.recv(1024)
        print(msg)


if __name__ == '__main__':
    # Try to bind the socket
    serverSocket.bind(('', SERVER_PORT))
    print("Socket binded to %s" % (SERVER_PORT))

    # listen for new connections
    serverSocket.listen(100)
    print("The Server is ready and listening to peers....")
    while 1:
        # accept new connections
        connectionSocket, addr = serverSocket.accept()
        print('Got connection from', addr)

        # create process p to handle the peer
        p = start_new_thread(handlePeer, (connectionSocket,))


    # Closing the main server at the end
    serverSocket.close()
