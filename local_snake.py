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

class Snake:
    last_direction = 'up'

    def __init__(self,env):
        self.env = env
        self.birth_place = env.windowSize / 2
        self.snake_queue = [self.birth_place]
        self.color = (255, 255, 255)
        self.alive = True
    
    def move(self, direction):
        if (self.last_direction == 'up' and direction == 'down') or \
            (self.last_direction == 'down' and direction == 'up') or \
            (self.last_direction == 'right' and direction == 'left') or \
            (self.last_direction == 'left' and direction == 'right'):
                pass
        else:
            self.last_direction = direction

    def check_death(self, head):
        # if the head is in the same place as some part of the body
        if np.array( [ (head == part).all() for part in self.snake_queue ] ).sum() > 1 or \
            any(head < 0) or any(head > self.env.windowSize): # if the head is anywhere outside the window boundaries
            self.alive = False
            return False
        return True

    def update(self):
        head = self.snake_queue[-1]
        match self.last_direction:
            case 'up':
                next_head = head + (0,-1)
            case 'down':
                next_head = head + (0,1)
            case 'left':
                next_head = head + (-1,0)
            case 'right':
                next_head = head + (1,0)
        self.snake_queue.append(next_head)
        
        # update environment food
        if self.env.has_food:
            if (self.env.food == next_head).all():
                self.env.has_food = False
            else:
                self.snake_queue.pop(0)

        # check if the snake is dead and return the result
        return self.check_death(head)

    def draw(self):
        for point in self.snake_queue:
            pygame.draw.circle(self.env.SCREEN, self.color, point*self.env.scale, 3)

class Game:
    windowSize = np.array((50,50))
    freq = 10
    scale = 10
    has_food = False

    def __init__(self):
        self.WINDOW = pygame.display.set_mode(self.windowSize*self.scale) 
        self.CAPTION = pygame.display.set_caption('Snake')
        self.SCREEN = pygame.display.get_surface()
        print("Display Initialized")
        pygame.display.update()
        self.snake = Snake(self)
        self.clock = Ticker(self.freq)
        self.controls = { K_UP: [self.snake.move, 'up' ],
                            K_DOWN: [self.snake.move, 'down' ],
                            K_LEFT: [self.snake.move, 'left' ],
                            K_RIGHT: [self.snake.move, 'right' ]   }

    def command(self, key):
        self.controls[key][0]( self.controls[key][1] )
    
    def drop_food(self):
        if not self.has_food:
            self.food = np.array((random.random() * self.windowSize[0] , random.random() * self.windowSize[1])).round()
            self.has_food = True
        pygame.draw.circle(self.SCREEN, (255, 0, 0), self.food*self.scale, 3)
        
    def loopGame(self):
        print("Starting Main Loop")
        
        while self.snake.alive:
            # Event Detection
            for event in pygame.event.get():
                if event.type == QUIT: 
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
                    try:
                        self.command(event.key)
                    except:
                        pass
            if self.clock.hasTicd():
                self.SCREEN.fill((0,0,0))
                self.snake.update()
                self.snake.draw()
                self.drop_food()
                pygame.display.update()
        print(f"Score: {len(self.snake.snake_queue)}.")

if __name__ == "__main__":
    pygame.init()
    game=Game()
    game.loopGame()
    input('Game over. Press Enter to exit.')
    sys.exit()
