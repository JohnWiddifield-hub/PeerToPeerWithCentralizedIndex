# csc401-final-p2p


1.Running Environment
OS: Microsoft Windows 
IDE: Pycharm 

2.How to run the program?
Precondition of executing the program: 
The server program should always run and listen to the client request on the well known port number until the client program ends the connection

3.Flow of the running  program
The server program will ask for the client port number after you run the client program 

We prompt the user to choose 1-6 which corresponds to 1.ADD 2.LIST 3.LOOKUP 4.GET 5.UPVOTE 6.QUIT

When you choose 1:
you will be asked for RFC number, RFC title. If the input RFC number is not correct you will be prompted to put another RFC number until you put the correct RFC number
RFC title will be also asked after the RFC number
After putting the RFC title, the request from the client program and the response for the request from the server will be displayed 

When you choose 2:
a list of RFC file in the server will be displayed 

When you choose 3:
 you will be asked for specific RFC number and title and corresponding RFC file and the number in the server will be displayed 

When you choose 4:
you will be asked for RFC title and the name of peer, and port number of peer. RFC file will be downloaded from the server

when you choose 5:
you will be asked for host port number and then the result of upvote will be displayed as a result 

When you choose 6:
 the client will terminate the connection with the server and the client will be removed from the peer list on the server. The other peer won’t be able to claim the file downloaded by the client 



4.HOW IT WORKS

Initially, the server should be running.  It is listening for peers to connect to it.  When a peer requests a connection the server opens up a new thread and handles all of the requests which the peer makes.  While the peer is connected, the server will maintain a client object which specifies all relevant information for that use such as rfc’s and upvote count.  When the peer disconnects from the server, the server removes all of that peer's information.  

When the client launches his program it will do two things.  First it will open a connection to the server.  Second, it will begin a server process in which it will begin listening for requests from other peers for rfc files which have been advertised on the server.
