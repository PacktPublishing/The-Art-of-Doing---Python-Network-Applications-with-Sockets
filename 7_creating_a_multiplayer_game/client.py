#Online Multiplayer Game Client
import pygame, socket, threading, json

#-----------------------------------------------------------------------------------------
#Define socket constants to be used and ALTERED
#DEST_IP should be of the form '192.168.1.*' or other addresses
DEST_IP = socket.gethostbyname(socket.gethostname())
DEST_PORT = 12345
#-----------------------------------------------------------------------------------------
#Define Classes
class Connection():
    '''A socket connection class for players to connect to a server'''
    def __init__(self):
        '''Initialzation for the Connection class'''
        self.encoder = "utf-8"
        self.header_length = 10

        #Create a socket and connect
        self.player_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.player_socket.connect((DEST_IP, DEST_PORT))


class Player():
    '''A player class the client can control'''
    def __init__(self, connection):
        '''Initialization of the Player class'''
        #Recieve the player information from the server
        packet_size = connection.player_socket.recv(connection.header_length).decode(connection.encoder)
        player_info_json = connection.player_socket.recv(int(packet_size))
        player_info = json.loads(player_info_json)

        #Set the player values on the client side
        self.number = player_info['number']
        self.size = player_info['size']

        self.starting_x = player_info['starting_x']
        self.starting_y = player_info['starting_y']
        self.p_color = player_info['p_color']
        self.s_color = player_info['s_color']

        self.x = player_info['x']
        self.y = player_info['y']
        self.dx = player_info['dx']
        self.dy = player_info['dy']
        self.coord = player_info['coord']

        self.is_waiting = player_info['is_waiting']
        self.is_ready = player_info['is_ready']
        self.is_playing = player_info['is_playing']
        self.status_message = player_info['status_message']


    def set_player_info(self, player_info):
        '''Set the player info to the given information from the server'''
        self.is_waiting = player_info['is_waiting']
        self.is_ready = player_info['is_ready']
        self.is_playing = player_info['is_playing']


    def update(self):
        '''Update the player by changing their coordinates in the game'''
        #Check to see what keys are being pressed
        keys = pygame.key.get_pressed()

        #Create a rect to chart player movement
        player_rect = pygame.draw.rect(display_surface, self.p_color, self.coord)

        #Only move the player if the player is playing the game
        if self.is_playing:
            if keys[pygame.K_UP] and player_rect.top > 0:
                self.dx = 0
                self.dy = -1*self.size
            elif keys[pygame.K_DOWN] and player_rect.bottom < WINDOW_HEIGHT:
                self.dx = 0
                self.dy = 1*self.size
            elif keys[pygame.K_LEFT] and player_rect.left > 0:
                self.dx = -1*self.size
                self.dy = 0
            elif keys[pygame.K_RIGHT] and player_rect.right < WINDOW_WIDTH:
                self.dx = 1*self.size
                self.dy = 0
            else:
                self.dx = 0
                self.dy = 0

            #Update the players current coordinates
            self.x += self.dx
            self.y += self.dy
            self.coord = (self.x, self.y, self.size, self.size)


    def reset_player(self):
        '''Reset player values for a new round on the client side'''
        self.x = self.starting_x
        self.y = self.starting_y
        self.coord = (self.x, self.y, self.size, self.size)

        self.is_waiting = False
        self.is_ready = True
        self.is_playing = False
        self.status_message = "Ready...waiting for other players"


class Game():
    '''A Game class to handle all operations of gameplay'''
    def __init__(self, connection, player, total_players):
        '''Initialzation of the Game class'''
        self.connection = connection
        self.player = player
        self.total_players = total_players
        self.is_active = False

        #Set the player count to player number - 1, we haven't recieved any game state data yet
        self.player_count = self.player.number - 1

        #Create a list to hold the current state of the game (from the server)
        self.game_state = []

        #Create variables to hold the state of the current game locally
        self.round_time = ROUND_TIME
        self.high_score = 0
        self.winning_player = 0

        #Wait till all players have joined and are ready.
        waiting_thread = threading.Thread(target=self.recieve_pregame_state)
        waiting_thread.start()


    def ready_game(self):
        '''Ready the game to be played'''
        #Update status flags for player
        self.player.is_waiting = False
        self.player.is_ready = True
        self.player.status_message = "Ready...Waiting for other players"

        #Send updated status to the server
        self.send_player_info()

        #Monitor for the start of the game from the server
        start_thread = threading.Thread(target=self.start_game)
        start_thread.start()


    def start_game(self):
        '''Start the game'''
        while True:
            #Wait to recieve information from the server that the game has started
            self.recieve_player_info()
            if self.player.is_playing:
                self.is_active = True
                self.player.is_ready = False
                self.player.status_message = "Play!"
                break


    def reset_game(self):
        '''Reset the game'''
        #Reset the game
        self.round_time = ROUND_TIME
        self.winning_player = 0
        self.high_score = 0

        #Reset the player
        self.player.reset_player()

        #Send updated status to the server
        self.send_player_info()

        #Monitor for the start of the game from the server
        start_thread = threading.Thread(target=self.start_game)
        start_thread.start()


    def send_player_info(self):
        '''Send specific info about this player to the server'''
        #Create a dictionary with items to send
        player_info = {
            'coord': self.player.coord,
            'is_waiting': self.player.is_waiting,
            'is_ready': self.player.is_ready,
            'is_playing': self.player.is_playing,
        }

        #Send the dictionary to the server
        player_info_json = json.dumps(player_info)
        header = str(len(player_info_json))
        while len(header) < self.connection.header_length:
            header += " "
        self.connection.player_socket.send(header.encode(self.connection.encoder))
        self.connection.player_socket.send(player_info_json.encode(self.connection.encoder))


    def recieve_player_info(self):
        '''Recieve specific info about this player from the server'''
        packet_size = self.connection.player_socket.recv(self.connection.header_length).decode(self.connection.encoder)
        player_info_json = self.connection.player_socket.recv(int(packet_size))
        player_info = json.loads(player_info_json)

        #Set the updated flags for the player
        self.player.set_player_info(player_info)


    def recieve_pregame_state(self):   
        '''Recieve ALL information about ALL players from the server before the game starts'''
        while self.player_count < self.total_players:
            #Wait for a new player to join and recieve their information
            packet_size = self.connection.player_socket.recv(self.connection.header_length).decode(self.connection.encoder)
            game_state_json = self.connection.player_socket.recv(int(packet_size))
            game_state = json.loads(game_state_json)
            self.game_state = game_state

            #Increase this games player count
            self.player_count += 1
        
        #All players have joined 
        self.player.status_message = "Press Enter to play!"


    def recieve_game_state(self):
        '''Recieve All information about ALL players from the server during the game'''
        #Recieve the game state
        packet_size = self.connection.player_socket.recv(self.connection.header_length).decode(self.connection.encoder)
        game_state_json = self.connection.player_socket.recv(int(packet_size))
        game_state = json.loads(game_state_json)

        #Update the clients game state
        self.game_state = game_state

        #Recieve the server time
        packet_size = self.connection.player_socket.recv(self.connection.header_length).decode(self.connection.encoder)
        self.round_time = self.connection.player_socket.recv(int(packet_size)).decode(self.connection.encoder)

        #Process the game state information
        self.process_game_state()


    def process_game_state(self):
        '''Process the game state to update scores, winning player, and time, etc...'''
        current_scores = []

        #Update THIS players coordinates in response to a collision
        for player in self.game_state:
            player = json.loads(player) #player is now a dict
            if player['number'] == self.player.number:
                self.player.coord = player['coord']
                self.player.x = self.player.coord[0]
                self.player.y = self.player.coord[1]
            
            #Determine who is currently winning
            if player['score'] > self.high_score:
                self.winning_player = player['number']
                self.high_score = player['score']
            #Add the score to our current score list to process for a tie
            current_scores.append(player['score'])
        
        #Check for a tie
        count = 0
        for score in current_scores:
            if score == self.high_score:
                count += 1
        #There is a tie for first place
        if count > 1:
            self.winning_player = 0


    def update(self):
        '''Update the game'''
        #Only update the game, if the player is playing
        if self.player.is_playing:
            #Update the player
            self.player.update()

            #Update the game
            if int(self.round_time) == 0:
                self.player.is_playing = False
                self.player.is_ready = False
                self.player.is_waiting = True
                self.player.status_message = "Game Over! Enter to play again"

            #Send the players current info to the server and recieve an updated game state
            self.send_player_info()
            self.recieve_game_state()


    def draw(self):
        '''Draw the game and all game assets to the window'''
        #Fill the display to the secondary color of the current winning player
        for player in self.game_state:
            player = json.loads(player)
            if player['number'] == self.winning_player:
                display_surface.fill(player['s_color'])
        
        #Creat a list to hold all scores
        current_scores = []

        #Loop through each players current state in the game_state
        for player in self.game_state:
            #Turn each string player back into a dict
            player = json.loads(player)

            #Prepare the score to be drawn later
            score = "P" + str(player['number']) + ": " + str(player['score'])
            score_text = font.render(score, True, WHITE)
            score_rect = score_text.get_rect()
            if player['number'] == 1:
                score_rect.topleft = (player['starting_x'], player['starting_y'])
            elif player['number'] == 2:
                score_rect.topright = (player['starting_x'], player['starting_y'])
            elif player['number'] == 3:
                score_rect.bottomleft = (player['starting_x'], player['starting_y'])
            else:
                score_rect.bottomright = (player['starting_x'], player['starting_y'])
            current_scores.append((score_text, score_rect))

            #Draw the given player
            pygame.draw.rect(display_surface, player['p_color'], player['coord'])
        
        #Draw a magenta outline around THIS player to highlight
        pygame.draw.rect(display_surface, self.player.p_color, self.player.coord)
        pygame.draw.rect(display_surface, MAGENTA, self.player.coord, int(self.player.size/10))

        #Draw all scores last so they are always on top
        for score in current_scores:
            display_surface.blit(score[0], score[1])

        #Create a round time text and draw
        time_text = font.render("Round Time: " + str(self.round_time), True, WHITE)
        time_rect = time_text.get_rect()
        time_rect.center = (WINDOW_WIDTH//2, 15)
        display_surface.blit(time_text, time_rect)

        #Create the player status
        status_text = font.render(self.player.status_message, True, WHITE)
        status_rect = status_text.get_rect()
        status_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2)
        display_surface.blit(status_text, status_rect)


#Create a connection and get game window information from the server.
my_connection = Connection()
packet_size = my_connection.player_socket.recv(my_connection.header_length).decode(my_connection.encoder)
room_size = int(my_connection.player_socket.recv(int(packet_size)).decode(my_connection.encoder))
packet_size = my_connection.player_socket.recv(my_connection.header_length).decode(my_connection.encoder)
round_time = int(my_connection.player_socket.recv(int(packet_size)).decode(my_connection.encoder))
packet_size = my_connection.player_socket.recv(my_connection.header_length).decode(my_connection.encoder)
fps = int(my_connection.player_socket.recv(int(packet_size)).decode(my_connection.encoder))
packet_size = my_connection.player_socket.recv(my_connection.header_length).decode(my_connection.encoder)
total_players = int(my_connection.player_socket.recv(int(packet_size)).decode(my_connection.encoder))

#Initialize pygame
pygame.init()

#Set game constants
WINDOW_WIDTH = room_size
WINDOW_HEIGHT = room_size
ROUND_TIME = round_time
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
MAGENTA = (155, 0, 155)
FPS = fps
clock = pygame.time.Clock()
font = pygame.font.SysFont('gabriola', 28)

#Create a game window
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("~~Color Collide~~")

#Create player and game objects
my_player = Player(my_connection)
my_game = Game(my_connection, my_player, total_players)

#The main game loop
running = True
while running:
    #Check to see if the user wants to quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                #Trigger a reset
                if my_player.is_waiting and my_game.is_active:
                    my_game.reset_game()
                #If the game has not yet started and ALL players are in the game.
                if my_player.is_waiting and my_game.player_count == my_game.total_players:
                    my_game.ready_game()
    
    #Fill the surface
    display_surface.fill(BLACK)

    #Update and draw classes
    my_game.update()
    my_game.draw()

    #Update the display and tick the clock
    pygame.display.update()
    clock.tick(FPS)