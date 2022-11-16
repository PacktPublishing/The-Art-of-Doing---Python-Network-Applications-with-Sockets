#Client Side Json
import socket, json

#Create a client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((socket.gethostbyname(socket.gethostname()), 12345))

#Recieve the encoded json object (string) from the server...o we have to decode????
message_json = client_socket.recv(1024)
#We can decode but we don't have to with json...
#message_json = client_socket.recv(1024).decode('utf-8')
print(message_json)
print(type(message_json))

#Turn the string object back into a dict using json
message_packet = json.loads(message_json)
print(message_packet)
print(type(message_packet))

#Our new object is in fact a dict
print(message_packet["message"])
for (key, value) in message_packet.items():
    print(f"{key}:{value}")

#Close the socket
client_socket.close()