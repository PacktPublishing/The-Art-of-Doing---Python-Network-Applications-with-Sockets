#Pygame tutorial
import pygame

#Initialize pygame
pygame.init()

#Set game constants
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
ROUND_TIME = 25

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PLAYER_COLOR = (125, 55, 200)

FPS = 30
clock = pygame.time.Clock()
font = pygame.font.SysFont('gabriola', 28)

#Create a game window
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("~~Pygame Tutorial~~")

#Create classes
class Player():
    '''A player class the user can control'''
    def __init__(self, x, y, size, color):
        '''Initialization of the Player class'''
        #Set the player values from passed arguments
        self.x = x
        self.y = y
        self.size = size
        self.color = color

        #Intialize player values
        self.dx = 0
        self.dy = 0
        self.coord = (self.x, self.y, self.size, self.size)


    def update(self):
        '''Update the player by changing their coordiantes in the game window'''
        #Check to see if a key is being held down
        keys = pygame.key.get_pressed()

        #Create a rect to chart player movement
        player_rect = pygame.draw.rect(display_surface, self.color, self.coord)

        #Move the player
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


class Game():
    '''A class to control gameplay'''
    def __init__(self, player):
        '''Initialzation for the Game class'''
        self.player = player

        #Create variables to hold the state of the current game
        self.frame_count = 0 #help determine how long 1 second is
        self.round_time = ROUND_TIME #currnet round time

    
    def update(self):
        '''Update the game, advance the clock, update the player'''
        #Advance the in game timer
        self.frame_count += 1
        if self.frame_count % FPS == 0:
            self.round_time -= 1
            self.frame_count = 0

        #Update the player
        self.player.update()


    def draw(self):
        '''Draw the game and game assets to the game window'''
        #Draw the player 
        pygame.draw.rect(display_surface, self.player.color, self.player.coord)

        #Create the round time text and draw
        time_text = font.render(f"Time: {self.round_time}", True, WHITE)
        time_rect = time_text.get_rect()
        time_rect.center = (WINDOW_WIDTH//2, 15)
        display_surface.blit(time_text, time_rect)


#Create a Player and Game class
my_player = Player(0,0,25,PLAYER_COLOR)
my_game = Game(my_player)

#The main game loop
running = True
while running:
    #Check to see if the user wants to quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #Fill the surface
    display_surface.fill(BLACK)

    #Update and draw classes
    my_game.update()
    my_game.draw()

    #Update the display and tick the clock
    pygame.display.update()
    clock.tick(FPS)
