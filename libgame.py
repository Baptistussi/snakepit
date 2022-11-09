import sys
import time
import numpy as np
import pygame
import random
from pygame.locals import *

class Ticker:
    def __init__(self, frequency):
        self.T=1./frequency
        self.t0=time.time()
        self.tLast=self.t0

    def hasTicd(self):
        now=time.time()
        if now-self.tLast>self.T:
            self.tLast=now
            return True
        else:
            return False

class Client_Game:
    windowSize = np.array((50,50))
    freq = 10
    scale = 10
    has_food = False
    snakes = dict()

    def __init__(self):
        self.clock = Ticker(self.freq)
        self.has_ended = False

    def control(self, control_msg):
        print("No command interface set.")

    def draw_snakes(self):
        for snake in self.snakes.values():
            for point in snake.snake_queue:
                pygame.draw.circle(self.SCREEN, snake.color[1], point*self.scale, 3)
    
    def draw_food(self):
        pygame.draw.circle(self.SCREEN, (255, 0, 0), self.food*self.scale, 3)
        
    def run(self):
        self.WINDOW = pygame.display.set_mode(self.windowSize*self.scale) 
        self.CAPTION = pygame.display.set_caption('Snake')
        self.SCREEN = pygame.display.get_surface()
        print("Display Initialized")
        pygame.display.update()
        pygame.init()
        print("Starting Main Loop")
        
        while not self.has_ended:
            # Event Detection
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.control('!DISCONNECT')
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
                    try:
                        self.control(event.key)
                    except:
                        pass
            if self.clock.hasTicd():
                self.SCREEN.fill((0,0,0))
                self.draw_snakes()
                self.draw_food()
                pygame.display.update()
        input('Game over. Press Enter to exit.')
        sys.exit()
        #print(f"Score: {len(self.snakes[ self.name ].snake_queue)}.")

class Server_Game:
    windowSize = np.array((50,50))
    freq = 10
    has_food = False
    game_over = False

    def __init__(self, web_interface, snakes):
        self.clock = Ticker(self.freq)
        self.end_game = False
        self.web_interface = web_interface
        self.snakes = snakes
        self.controls = { K_UP: 'up',
                            K_DOWN: 'down',
                            K_LEFT: 'left',
                            K_RIGHT: 'right'  }

    def random_place(self):
        return np.array((random.random() * self.windowSize[0] , random.random() * self.windowSize[1])).round()
    
    def update_food(self):
        if not self.has_food:
            self.food = self.random_place()
            self.has_food = True
            self.web_interface.update_food( food_data={'place':self.food} )

    def any_snakes_alive(self):
        return any([snake.alive for snake in self.snakes.values() ])

    def update_snakes(self):
        for player_name in self.snakes.keys():
            self.snakes[ player_name ].update()
            self.web_interface.update_snake(player_name, self.snakes[ player_name ].report() )
    
    def control(self, player_name, key):
        self.snakes[ player_name ].move( self.controls[key] )
    
    def loop_game(self):
        print("Starting Main Loop")

        self.web_interface.start_game_on_clients()

        while self.any_snakes_alive():
            if self.clock.hasTicd():
                self.update_snakes()
                self.update_food()
        
        self.game_over = True
        self.web_interface.end_game()