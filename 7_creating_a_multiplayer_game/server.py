#Online Multiplayer Game Server
import socket, threading, json, time

#---------------------------------------------------------------------------------------------
#Define socket constants to be used and ALTERED
HOST_IP = socket.gethostbyname(socket.gethostname())
HOST_PORT = 12345

#Define pygame constants to be used and ALTERED
ROOM_SIZE = 700
PLAYER_SIZE = 140
ROUND_TIME = 30
FPS = 15
TOTAL_PLAYERS = 4

#Room must be divisible by player size for correct gameplay, adjust as needed.
while ROOM_SIZE % PLAYER_SIZE != 0:
    PLAYER_SIZE += 1

#Maximum number of players allowed is 4!
if TOTAL_PLAYERS > 4:
    TOTAL_PLAYERS = 4
#---------------------------------------------------------------------------------------------
#Define Classes
class Connection():
    '''A socket connection class to be used as a server'''
    def __init__(self):
        '''Initailzation of the Connection class'''
        self.encoder = 'utf-8'
        self.header_length = 10

        #Create a socket, bind, and listen
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((HOST_IP, HOST_PORT))
        self.server_socket.listen()


class Player():
    '''A class to store a connected clients player information'''
    def __init__(self, number):
        '''Initialzation of the Player class'''
        self.number = number
        self.size = PLAYER_SIZE
        self.score = 0

        #Assign starting conditions that vary with player number
        if self.number == 1:
            self.starting_x = 0
            self.starting_y = 0
            self.p_color = (255, 0, 0)
            self.s_color = (150, 0, 0)
        elif self.number == 2:
            self.starting_x = ROOM_SIZE - PLAYER_SIZE
            self.starting_y = 0
            self.p_color = (0, 255, 0)
            self.s_color = (0, 150, 0)
        elif self.number == 3:
            self.starting_x = 0
            self.starting_y = ROOM_SIZE - PLAYER_SIZE
            self.p_color = (0, 0, 255)
            self.s_color = (0, 0, 150)
        elif self.number == 4:
            self.starting_x = ROOM_SIZE - PLAYER_SIZE
            self.starting_y = ROOM_SIZE - PLAYER_SIZE
            self.p_color = (255, 255, 0)
            self.s_color = (150, 150, 0)
        else:
            print("Too many players trying to join...")

        #Set the rest of the player attributes
        self.x = self.starting_x
        self.y = self.starting_y
        self.dx = 0
        self.dy = 0
        self.coord = (self.x, self.y, self.size, self.size)

        self.is_waiting = True
        self.is_ready = False
        self.is_playing = False
        self.status_message = f"Waiting for {TOTAL_PLAYERS} total players"


    def set_player_info(self, player_info):
        '''Set the player info to the given info from the client (coord and status flags)'''
        self.coord = player_info['coord']
        self.is_waiting = player_info['is_waiting']
        self.is_ready = player_info['is_ready']
        self.is_playing = player_info['is_playing']


    def reset_player(self):
        '''Reset player values for a new round on the server side'''
        self.score = 0


class Game():
    '''A class to handle all operations of gameplay'''
    def __init__(self, connection):
        '''Initialzation of the Game class'''
        self.connection = connection
        self.player_count = 0
        self.player_objects = []
        self.player_sockets = []
        self.round_time = ROUND_TIME


    def connect_players(self):
        '''Connect ANY incomming player to the game'''
        #Only accept players if the player count is less than total players
        while self.player_count < TOTAL_PLAYERS:
            #Accept incoming player socket connections
            player_socket, player_address = self.connection.server_socket.accept()

            #Send the current game configuration values over to the client
            header = str(len(str(ROOM_SIZE)))
            while len(header) < self.connection.header_length:
                header += " "  
            player_socket.send(header.encode(self.connection.encoder))
            player_socket.send(str(ROOM_SIZE).encode(self.connection.encoder))

            header = str(len(str(ROUND_TIME)))
            while len(header) < self.connection.header_length:
                header += " "  
            player_socket.send(header.encode(self.connection.encoder))
            player_socket.send(str(ROUND_TIME).encode(self.connection.encoder))

            header = str(len(str(FPS)))
            while len(header) < self.connection.header_length:
                header += " "  
            player_socket.send(header.encode(self.connection.encoder))
            player_socket.send(str(FPS).encode(self.connection.encoder))

            header = str(len(str(TOTAL_PLAYERS)))
            while len(header) < self.connection.header_length:
                header += " "  
            player_socket.send(header.encode(self.connection.encoder))
            player_socket.send(str(TOTAL_PLAYERS).encode(self.connection.encoder))

            #Create a new Player object for the connected client
            self.player_count += 1
            player = Player(self.player_count)
            self.player_objects.append(player)
            self.player_sockets.append(player_socket)
            print(f"New player joining from {player_address}...Total players: {self.player_count}")

            #Send the new player object to the connected client
            player_info_json = json.dumps(player.__dict__)
            header = str(len(player_info_json))
            while len(header) < self.connection.header_length:
                header += " "
            player_socket.send(header.encode(self.connection.encoder))
            player_socket.send(player_info_json.encode(self.connection.encoder))

            #Alert ALL players of new player joining the game
            self.broadcast()

            #Create a thread to monitor the ready status of THIS player
            ready_thread = threading.Thread(target=self.ready_game, args=(player, player_socket,))
            ready_thread.start()

        #Maximum number of players reached.  No longer accepting new players
        print(f"{TOTAL_PLAYERS} players in game.  No longer accepting new players...")


    def broadcast(self):
        '''Broadcast information to ALL players'''
        game_state = []

        #Turn each player object into a dict, then into a string with json
        for player_object in self.player_objects:
            player_json = json.dumps(player_object.__dict__)
            game_state.append(player_json)

        #Now that someone else has joined the game, send the game state to ALL players
        game_state_json = json.dumps(game_state)
        header = str(len(game_state_json))
        while len(header) < self.connection.header_length:
            header += " "
        for player_socket in self.player_sockets:
            player_socket.send(header.encode(self.connection.encoder))
            player_socket.send(game_state_json.encode(self.connection.encoder))


    def ready_game(self, player, player_socket):
        '''Ready the game to be played for a SPECIFIC player'''
        #Wait till the given player has sent info signaling they are ready to play
        self.recieve_pregame_player_info(player, player_socket)

        #Reset the game
        self.reset_game(player)

        #If THIS player is ready to play
        if player.is_ready:
            while True:
                #Check if ALL players are ready
                game_start = True
                for player_object in self.player_objects:
                    if player_object.is_ready == False:
                        game_start = False
                    
                #If ALL current players are ready to play the game
                if game_start:
                    player.is_playing = True
                    
                    #Start a clock on the server
                    self.start_time = time.time()
                    break
            
            #Send updated player flags back to THIS player
            self.send_player_info(player, player_socket)

            #Now that THIS player has started, create a thread to recieve game information
            recieve_thread = threading.Thread(target=self.recieve_game_player_info, args=(player, player_socket,))
            recieve_thread.start()
                     

    def reset_game(self, player):
        '''Restart the game and wipe information for a SPECIFIC player'''
        #Reset the game
        self.round_time = ROUND_TIME

        #Reset the player
        player.reset_player()


    def send_player_info(self, player, player_socket):
        '''Send specific information about THIS player to the given client'''
        #Create a dictionary with the status flags for THIS player
        player_info = {
            'is_waiting': player.is_waiting,
            'is_ready': player.is_ready,
            'is_playing': player.is_playing,
        }

        #Send the player info over to THIS player
        player_info_json = json.dumps(player_info)
        header = str(len(player_info_json))
        while len(header) < self.connection.header_length:
            header += " "
        player_socket.send(header.encode(self.connection.encoder))
        player_socket.send(player_info_json.encode(self.connection.encoder))
        

    def recieve_pregame_player_info(self, player, player_socket):
        '''Recieve specific info about THIS player pregame'''
        packet_size = player_socket.recv(self.connection.header_length).decode(self.connection.encoder)
        player_info_json = player_socket.recv(int(packet_size))
        player_info = json.loads(player_info_json)

        #Set the updated values for THIS player
        player.set_player_info(player_info)


    def recieve_game_player_info(self, player, player_socket):
        '''Recieve specific info about THIS player during the game'''
        while player.is_playing:
            packet_size = player_socket.recv(self.connection.header_length).decode(self.connection.encoder)
            player_info_json = player_socket.recv(int(packet_size))
            player_info = json.loads(player_info_json)

            #Set the updated values for the given player
            player.set_player_info(player_info)

            #Process the new game state to see if a player scored points
            self.process_game_state(player, player_socket)

        #Game have finished, monitor for the restart of the game.
        ready_thread = threading.Thread(target=self.ready_game, args=(player, player_socket))
        ready_thread.start()


    def process_game_state(self, player, player_socket):
        '''Process the given player info and update the games state'''
        #Update the server clock
        self.current_time = time.time()
        self.round_time = ROUND_TIME - int(self.current_time - self.start_time)

        #Process collisions for this player
        for player_object in self.player_objects:
            #Dont collide with yourself!
            if player != player_object:
                if player.coord == player_object.coord:
                    player.score += 1
                    player.x = player.starting_x
                    player.y = player.starting_y
                    player.coord = (player.x, player.y, player.size, player.size)

        #Send the updated game state back to THIS player
        self.send_game_state(player_socket)


    def send_game_state(self, player_socket):
        '''Send the current game state of ALL players to THIS given player'''
        game_state = []

        #Turn each connected player ojbect into a dict, then a string
        for player_object in self.player_objects:
            player_json = json.dumps(player_object.__dict__)
            game_state.append(player_json)

        #Send the whole game state back to THIS player
        game_state_json = json.dumps(game_state)
        header = str(len(game_state_json))
        while len(header) < self.connection.header_length:
            header += " "
        player_socket.send(header.encode(self.connection.encoder))
        player_socket.send(game_state_json.encode(self.connection.encoder))

        #Send the server time
        header = str(len(str(self.round_time)))
        while len(header) < self.connection.header_length:
            header += " "
        player_socket.send(header.encode(self.connection.encoder))
        player_socket.send(str(self.round_time).encode(self.connection.encoder))


#Start the server
my_connection = Connection()
my_game = Game(my_connection)

#Listen for incomming connections
print("Server is listening for incomming connections...\n")
my_game.connect_players()