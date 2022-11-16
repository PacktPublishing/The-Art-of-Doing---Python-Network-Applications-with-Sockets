#Pickle Server
import socket, pickle

#Lets create a regular old list
unpickled_list = ['dill', 'bread and butter', 'half-sour']
print(unpickled_list)
print(type(unpickled_list))

#Try to encode the list using .encode() DOESNT WORK!
#trial_list = unpickled_list.encode("utf-8")
#print(trial_list)
#print(type(trial_list))

#Now lets encode by pickling the list!
pickled_list = pickle.dumps(unpickled_list)
print(pickled_list)
print(type(pickled_list))

#Create a server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((socket.gethostbyname(socket.gethostname()), 12345))
server_socket.listen()

#Listen forever to accept ANY connection
while True:
    client_socket, client_address = server_socket.accept()
    print(f"Connected to {client_address}!\n")

    #Send the encoded pickeled list...THIS IS ALREADY ENCODED
    client_socket.send(pickled_list)

    #Close the socket
    server_socket.close()