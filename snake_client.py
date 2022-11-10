import sys
import time
import pickle
import socket
import threading

from libgame import Client_Game
from libsnake import Messages, Client_Snake

PORT = 5051
WAIT_TIME = 3

class GameAPI(Client_Game):
    def update_player_dict(self, server_player_dict):
        new_players = set(server_player_dict.keys()) - set(self.snakes.keys())
        for new_player in new_players:
            print(f"New player connected: {new_player}, color: {server_player_dict[new_player]['color']}.")
            self.snakes[ new_player ] = Client_Snake(new_player, server_player_dict[new_player]['color'])

    def drop_foe_player(self, player_name):
        self.snakes.pop(player_name)

    def start_game(self):
        thread = threading.Thread(target=self.run)
        thread.daemon = False
        thread.start()

    def update_snake(self, player_name, snake_data):
        self.snakes[player_name].update_from_server( snake_data )
    
    def update_food(self, food_data):
        self.food = food_data['place']

    def end_game(self):
        self.has_ended = True

    def set_command_callback( client_function ):
        self.control = client_function

class Client(Messages):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    DISCONNECT_MESSAGE = '!DISCONNECT'
    client_alive = True

    def __init__(self, addr):
        self.sock.connect(addr)
        self.game_api = GameAPI()
        self.game_api.control = self.publish_command

    def interpret_msg(self, msg):
        msg_dict = pickle.loads(msg)
        mtype = msg_dict['type']
        
        match mtype:
            case 'update_player_dict':
                self.game_api.update_player_dict( msg_dict['player_dict'] )
            case 'player_disconnect':
                self.game_api.drop_foe_player( msg_dict['player_name'] )
            case 'all_players_ready':
                print('Game started.')
                self.game_api.start_game()
            case 'snake_update':
                self.game_api.update_snake( msg_dict['player_name'], msg_dict['snake_data'] )
            case 'food_update':
                self.game_api.update_food( msg_dict['food_data'] )
            case 'game_over':
                self.game_api.end_game()
                self.client_alive = False         

    def publish_command(self, key):
        msg = { 'type':'command',
                'key': key }
        self.sendMsg( self.sock, pickle.dumps(msg), encode=False )
    
    def subscriber(self):
        # game loop
        while self.client_alive:
            msg = self.recvMsg(self.sock, decode=False)
            self.interpret_msg(msg)
        # end of game
        self.sendMsg(self.sock, pickle.dumps(self.DISCONNECT_MESSAGE), encode=False )
    
    def launch(self):
        # name setting loop
        has_name = False
        while not has_name:
            name = input("Enter your name: ")
            self.sendMsg(self.sock, name)
            answer = self.recvMsg(self.sock)
            if answer == 'OK':
                self.player_name = name
                has_name = True
            else:
                print("Name already taken. Try again.")

        # start subscriber thread
        thread = threading.Thread(target=self.subscriber)
        thread.start()
        # wait other players
        print("Waiting for other players")
        time.sleep(WAIT_TIME)
        # wait player ready
        input("Press ENTER when you're ready.\n")
        msg = { 'type':'player_ready' }
        self.sendMsg( self.sock, pickle.dumps(msg), encode=False )

if __name__ == "__main__":
    client = Client((sys.argv[1], PORT))
    client.launch()