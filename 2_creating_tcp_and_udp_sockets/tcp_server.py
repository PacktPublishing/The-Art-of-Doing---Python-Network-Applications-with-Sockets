#TCP Server Side
import socket

#Create a server side socket using IPV4 (AF_INET) and TCP (SOCK_STREAM)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#See how to get IP address dynamically
print(socket.gethostname()) #hostname
print(socket.gethostbyname(socket.gethostname())) #ip of the given hostname

#Bind our new socket to a tuple (IP Address, Port Address)
server_socket.bind((socket.gethostbyname(socket.gethostname()), 12345))

#Put the socket into listening mode to listen for any possible connections
server_socket.listen()

#Listen forever to accept ANY connection
while True:
    #Accept every single connection and store two pieces of information
    client_socket, client_address = server_socket.accept()
    #print(type(client_socket))
    #print(client_socket)
    #print(type(client_address))
    #print(client_address)

    print(f"Connected to {client_address}!\n")

    #Send a message to the client that jsut connected
    client_socket.send("You are connected!".encode("utf-8"))

    #Close the connection
    server_socket.close()
    break