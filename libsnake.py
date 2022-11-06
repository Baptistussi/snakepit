import numpy as np
import pickle

class Messages:
    HEADER = 64
    FORMAT = 'utf-8'
    
    def sendMsg(self, conn, msg, encode=True):
        if encode: msg = msg.encode(self.FORMAT)
        msg_length = len(msg)
        send_length = str(msg_length).encode(self.FORMAT)
        send_length += b' ' * (self.HEADER - len(send_length))
        conn.send(send_length)
        conn.send(msg)
    
    def recvMsg(self, conn, decode=True):
        msg_length = conn.recv(self.HEADER).decode(self.FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            if decode: msg = conn.recv(msg_length).decode(self.FORMAT)
            else: msg = conn.recv(msg_length)
            return msg
        else:
            return False

class Client_Snake:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.alive = True
        self.snake_queue = []

    def update_from_server(self, snake_data):
        self.alive = snake_data.get('alive')
        self.snake_queue = []
        for pos in snake_data.get('snake_queue'):
            self.snake_queue.append( np.array(pos) )

class Server_Snake:
    last_direction = 'up'

    def __init__(self, env, name, color):
        self.env = env
        self.name = name
        self.color = color
        self.birth_place = env.windowSize / 2
        self.snake_queue = [self.birth_place]
        self.ready = False
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
        self.alive = self.check_death(head)
    
    def report(self):
        snake_data = { 'alive': self.alive,
                    'snake_queue' : self.snake_queue}
        return snake_data