#UDP Server side
import socket

#Create a server side socket IPV4 (AF_INET) and UDP (SOCK_DGRAM)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#Bind our new socket to a tuple (Ip address, port address)
server_socket.bind((socket.gethostbyname(socket.gethostname()), 12345))

#We are not listening or accepting connections since UDP is a conectionless protocol

message, address = server_socket.recvfrom(1024)
print(message.decode("utf-8"))
print(address)

message, address = server_socket.recvfrom(1024)
print(message.decode("utf-8"))
print(address)