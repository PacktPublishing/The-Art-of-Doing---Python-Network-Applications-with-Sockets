#Pickle Client
import socket, pickle

#Create a client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((socket.gethostbyname(socket.gethostname()), 12345))

#Recive the pickled list from the server
pickled_list = client_socket.recv(1024)
print(pickled_list)
print(type(pickled_list))

#You cannot decode a list using .decode(), we'll use pickle!
unpickled_list = pickle.loads(pickled_list)
print(unpickled_list)
print(type(unpickled_list))

#For our new list, we have all the list methods
print(unpickled_list[0])
unpickled_list.append('gherkin')
for pick in unpickled_list:
    print(pick)

#Close the socket
client_socket.close()