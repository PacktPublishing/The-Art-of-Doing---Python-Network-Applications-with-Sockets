#Server Side Json
import socket, json

#Create a dict to represent a message packet holding all message information
message_packet = {
    "flag": "MESSAGE",
    "name": "Mike",
    "message": "This is my message coming through!",
    "color": "#00ff3f",
}

#Lets look at the original dict
print(message_packet)
print(type(message_packet))

#You can't encode a dict with .encode!
#print(message_packet.encode('utf-8'))

#Turn the dict into a string using json
message_json = json.dumps(message_packet)
print(message_json)
print(type(message_json))

#Now we can encode the string representation of the dict!
print(message_json.encode('utf-8'))
print(type(message_json.encode('utf-8')))

#Create a server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((socket.gethostbyname(socket.gethostname()), 12345))
server_socket.listen()

#Listen for all incoming connections
while True:
    client_socket, client_address = server_socket.accept()
    print(f"Connected to {client_address}!\n")

    #Send the json object...which is just a STRING, BUT WE HAVE TO ENCODE THIS FIRST!
    client_socket.send(message_json.encode('utf-8'))

    #Close the socket
    server_socket.close()
    break