#An intro to using fixed lenght headers client
import socket, time

#Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((socket.gethostbyname(socket.gethostname()), 12345))

#Let's recive two messages with a small byte size of 8...will not work!
'''message = client_socket.recv(8)
print(message.decode('utf-8'))
message = client_socket.recv(8)
print(message.decode('utf-8'))'''

#Let's recive two messages with a large byte size of 1024...this will work...for now!
'''message = client_socket.recv(1024)
print(message.decode('utf-8'))
message = client_socket.recv(1024)
print(message.decode('utf-8'))'''

#What happens if we add some 'delay' time in between the client connecting and trying to recieve messages
'''time.sleep(2)
message = client_socket.recv(1024)
print(message.decode('utf-8'))
message = client_socket.recv(1024)
print(message.decode('utf-8'))
print("Why isn't this printing?!?!?!?!")'''

#WE might not know the maximum bytesize of the data being sent, it may be more or less than 1024.
#Two issues moving forward.
#1) if we are too small with our bytesize, we'll have issues not getting the full data packet being sent.
#2) If we are too large with our bytesize, and there is a time delay between sending and recieving we might get more
#than one data packet being sent in a single .recv() call.

#WE can fix this by first recieving a HEADER of fixed lenght that will give the size of the incoming message packet.
time.sleep(2)
header = client_socket.recv(10)
print(header)
print(len(header))
message = client_socket.recv(int(header))
print(message.decode('utf-8'))

time.sleep(2)
header = client_socket.recv(10)
print(header)
print(len(header))
message = client_socket.recv(int(header))
print(message.decode('utf-8'))

print("Now this should print!")