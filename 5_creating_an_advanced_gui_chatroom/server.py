#Server side Advanced GUI chat room (admin)
import tkinter, socket, threading, json
from tkinter import DISABLED, VERTICAL, END, NORMAL

#Define window
root = tkinter.Tk()
root.title("Chat Server")
root.iconbitmap("message_icon.ico")
root.geometry('600x600')
root.resizable(0,0)

#Define fonts and colors
my_font = ('SimSun', 14)
black = "#010101"
light_green = "#1fc742"
root.config(bg=black)

#Create a Connection class to hold our server socket
class Connection():
    '''A class to store a connection - a server socket and pertinent information'''
    def __init__(self):
        self.host_ip = socket.gethostbyname(socket.gethostname())
        self.encoder = 'utf-8'
        self.bytesize = 1024

        self.client_sockets = []
        self.client_ips = []
        self.banned_ips = []


#Define Functions
def start_server(connection):
    '''Start the server on a given port number'''
    #Get the port number to run the serrver and attach to the connection object
    connection.port = int(port_entry.get())

    #Create server socket
    connection.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.server_socket.bind((connection.host_ip, connection.port))
    connection.server_socket.listen()

    #Update GUI
    history_listbox.delete(0, END)
    history_listbox.insert(0, f"Server started on port {connection.port}.")
    end_button.config(state=NORMAL)
    self_broadcast_button.config(state=NORMAL)
    message_button.config(state=NORMAL)
    kick_button.config(state=NORMAL)
    ban_button.config(state=NORMAL)
    start_button.config(state=DISABLED)

    #Create a thread to continously listen for connections
    connect_thread = threading.Thread(target=connect_client, args=(connection,))
    connect_thread.start()


def end_server(connection):
    '''Begin the process of ending the server'''
    #Alert all users that the server is closing
    message_packet = create_message("DISCONNECT", "Admin (broadcast)", "Server is closing...", light_green)
    message_json = json.dumps(message_packet)
    broadcast_message(connection, message_json.encode(connection.encoder))

    #Update GUI
    history_listbox.insert(0, f"Server closing on port {connection.port}.")
    end_button.config(state=DISABLED)
    self_broadcast_button.config(state=DISABLED)
    message_button.config(state=DISABLED)
    kick_button.config(state=DISABLED)
    ban_button.config(state=DISABLED)
    start_button.config(state=NORMAL)

    #Close server socket
    connection.server_socket.close()


def connect_client(connection):
    '''Connect an incoming client to the server'''
    while True:
        try:
            client_socket, client_address = connection.server_socket.accept()
            #Check to see if the IP of the client is banned.
            if client_address[0] in connection.banned_ips:
                message_packet = create_message("DISCONNECT", "Admin (private)", "You have been banned...goodbye", light_green)
                message_json = json.dumps(message_packet)
                client_socket.send(message_json.encode(connection.encoder))

                #Clost the client socket
                client_socket.close()
            else:
                #Send a message pakcet to recieve client info
                message_packet = create_message("INFO", "Admin (private)", "Please send your name", light_green)
                message_json = json.dumps(message_packet)
                client_socket.send(message_json.encode(connection.encoder))

                #Wait for confimration message to be sent verifiying the connection
                message_json = client_socket.recv(connection.bytesize)
                process_message(connection, message_json, client_socket, client_address)
        except:
            break


def create_message(flag, name, message, color):
    '''Return a message packet to be sent'''
    message_packet = {
        "flag": flag,
        "name": name,
        "message": message,
        "color": color,
    }

    return message_packet


def process_message(connection, message_json, client_socket, client_address=(0,0)):
    '''Update server information based on a message packet flag'''
    message_packet = json.loads(message_json) #decode and turn to dict in one step!
    flag = message_packet["flag"]
    name = message_packet["name"]
    message = message_packet["message"]
    color = message_packet["color"]

    if flag == "INFO":
        #Add the new client information to the appropriate lists
        connection.client_sockets.append(client_socket)
        connection.client_ips.append(client_address[0])

        #Broadcast the new client joining and update GUI
        message_packet = create_message("MESSAGE", "Admin (broadcast)", f"{name} has joined the server!!!", light_green)
        message_json = json.dumps(message_packet)
        broadcast_message(connection, message_json.encode(connection.encoder))

        #Update server UI
        client_listbox.insert(END, f"Name: {name}        IP Addr: {client_address[0]}")

        #Now that a client has been established, start a thread to recieve messages
        recieve_thread = threading.Thread(target=recieve_message, args=(connection, client_socket,))
        recieve_thread.start()
    
    elif flag == "MESSAGE":
        #Broadcast the given message
        broadcast_message(connection, message_json)

        #Update the server UI
        history_listbox.insert(0, f"{name}: {message}")
        history_listbox.itemconfig(0, fg=color)

    elif flag == "DISCONNECT":
        #Close/remove client socket
        index = connection.client_sockets.index(client_socket)
        connection.client_sockets.remove(client_socket)
        connection.client_ips.pop(index)
        client_listbox.delete(index)
        client_socket.close()
 
        #Alert all users that the client has left the chat
        message_packet = create_message("MESSAGE", "Admin (broadcast)", f"{name} has left the server...", light_green)
        message_json = json.dumps(message_packet)
        broadcast_message(connection, message_json.encode(connection.encoder))

        #Update the server UI
        history_listbox.insert(0, f"Admin (broadcast): {name} has left the server...")

    else:
        #Catch for errors...
        history_listbox.insert(0, "Error processing message...")


def broadcast_message(connection, message_json):
    '''Send a message to all client sockets connected to the server...ALL JSON ARE ENCODED'''
    for client_socket in connection.client_sockets:
        client_socket.send(message_json)


def recieve_message(connection, client_socket):
    '''Recive an incoming message from a client'''
    while True:
        #Get a message_json from a client
        try:
            message_json = client_socket.recv(connection.bytesize)
            process_message(connection, message_json, client_socket)
        except:
            break


def self_broadcast(connection):
    '''Broadcast a special admin message to all clients'''
    #Create a message packet
    message_packet = create_message("MESSAGE", "Admin (broadcast)", input_entry.get(), light_green)
    message_json = json.dumps(message_packet)
    broadcast_message(connection, message_json.encode(connection.encoder))

    #Clear the input entry
    input_entry.delete(0, END)


def private_message(connection):
    '''Send a private message to a single client'''
    #Select the client from the client lixbox and access their client socket
    index = client_listbox.curselection()[0]
    client_socket = connection.client_sockets[index]

    #Create a message packet and send
    message_packet = create_message("MESSAGE", "Admin (private)", input_entry.get(), light_green)
    message_json = json.dumps(message_packet)
    client_socket.send(message_json.encode(connection.encoder))

    #Clear the input entry
    input_entry.delete(0, END)


def kick_client(connection):
    '''Kick a given client off the server'''
    #Select a client from the listbox
    index = client_listbox.curselection()[0]
    client_socket = connection.client_sockets[index]

    #Create the message packet
    message_packet = create_message("DISCONNECT", "Admin (private)", "You have been kicked...", light_green)
    message_json = json.dumps(message_packet)
    client_socket.send(message_json.encode(connection.encoder))


def ban_client(connection):
    '''Ban a given client based on their IP address'''
    #Select a client from the listbox
    index = client_listbox.curselection()[0]
    client_socket = connection.client_sockets[index]

    #Create the message packet
    message_packet = create_message("DISCONNECT", "Admin (private)", "You have been banned...", light_green)
    message_json = json.dumps(message_packet)
    client_socket.send(message_json.encode(connection.encoder))

    #Ban the IP address of the client
    connection.banned_ips.append(connection.client_ips[index])


#Define GUI Layout
#Create Frames
connection_frame = tkinter.Frame(root, bg=black)
history_frame = tkinter.Frame(root, bg=black)
client_frame = tkinter.Frame(root, bg=black)
message_frame = tkinter.Frame(root, bg=black)
admin_frame = tkinter.Frame(root, bg=black)

connection_frame.pack(pady=5)
history_frame.pack()
client_frame.pack(pady=5)
message_frame.pack()
admin_frame.pack()

#Connection Frame Layout
port_label = tkinter.Label(connection_frame, text="Port Number:", font=my_font, bg=black, fg=light_green)
port_entry = tkinter.Entry(connection_frame, width=10, borderwidth=3, font=my_font)
start_button = tkinter.Button(connection_frame, text="Start Server", borderwidth=5, width=15, font=my_font, bg=light_green, command=lambda:start_server(my_connection))
end_button = tkinter.Button(connection_frame, text="End Server", borderwidth=5, width=15, font=my_font, bg=light_green, state=DISABLED, command=lambda:end_server(my_connection))

port_label.grid(row=0, column=0, padx=2, pady=10)
port_entry.grid(row=0, column=1, padx=2, pady=10)
start_button.grid(row=0, column=2, padx=5, pady=10)
end_button.grid(row=0, column=3, padx=5, pady=10)

#History Frame Layout
history_scrollbar = tkinter.Scrollbar(history_frame, orient=VERTICAL)
history_listbox = tkinter.Listbox(history_frame, height=10, width=55, borderwidth=3, font=my_font, bg=black, fg=light_green, yscrollcommand=history_scrollbar.set)
history_scrollbar.config(command=history_listbox.yview)

history_listbox.grid(row=0, column=0)
history_scrollbar.grid(row=0, column=1, sticky="NS")

#Client Frame Layout
client_scrollbar = tkinter.Scrollbar(client_frame, orient=VERTICAL)
client_listbox = tkinter.Listbox(client_frame, height=10, width=55, borderwidth=3, font=my_font, bg=black, fg=light_green, yscrollcommand=client_scrollbar.set)
client_scrollbar.config(command=client_listbox.yview)

client_listbox.grid(row=0, column=0)
client_scrollbar.grid(row=0, column=1, sticky="NS")

#Message Frame Layout
input_entry = tkinter.Entry(message_frame, width=40, borderwidth=3, font=my_font)
self_broadcast_button = tkinter.Button(message_frame, text="Broadcast", width=13, borderwidth=5, font=my_font, bg=light_green, state=DISABLED, command=lambda:self_broadcast(my_connection))

input_entry.grid(row=0, column=0, padx=5, pady=5)
self_broadcast_button.grid(row=0, column=1, padx=5, pady=5)

#Admin Frame Layout
message_button = tkinter.Button(admin_frame, text="PM", borderwidth=5, width=15, font=my_font, bg=light_green, state=DISABLED, command=lambda:private_message(my_connection))
kick_button = tkinter.Button(admin_frame, text="Kick", borderwidth=5, width=15, font=my_font, bg=light_green, state=DISABLED, command=lambda:kick_client(my_connection))
ban_button = tkinter.Button(admin_frame, text="Ban", borderwidth=5, width=15, font=my_font, bg=light_green, state=DISABLED, command=lambda:ban_client(my_connection))

message_button.grid(row=0, column=0, padx=5, pady=5)
kick_button.grid(row=0, column=1, padx=5, pady=5)
ban_button.grid(row=0, column=2, padx=5, pady=5)

#Create a Connection object and run the root window's mainloop()
my_connection = Connection()
root.mainloop()