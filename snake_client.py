import sys
import time
import pickle
import socket
import threading

from libgame import Client_Game
from libsnake import Messages, Client_Snake

PORT = 5050

class GameAPI(Client_Game):
    def initialize_snake(self, player_data):
        print(f"New player connected: {player_data['name']}")
        self.snakes[ player_data['name'] ] = Client_Snake(player_data['name'], player_data['color'])

    def drop_foe_player(self, player_name):
        self.snakes.pop(player_name)

    def start_game(self):
        thread = threading.Thread(target=self.run)
        thread.daemon = True
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
            case 'new_player':
                self.game_api.initialize_snake( msg_dict['player_data'] )
                print(f"{msg_dict['player_data']['name']}'s color is {msg_dict['player_data']['color'][0]}")
            case 'player_disconnect':
                self.game_api.drop_foe_player( msg_dict['player_name'] )
            case 'all_players_ready':
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
    
    def run(self):
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

        # wait other players
        print("Waiting for other players")
        time.sleep(5)
        # wait player ready
        input("Press ENTER when you're ready.")
        msg = { 'type':'player_ready' }
        self.sendMsg( self.sock, pickle.dumps(msg), encode=False ) 

        # game loop
        while self.client_alive:
            msg = self.recvMsg(self.sock, decode=False)
            self.interpret_msg(msg)
        # end of game
        self.sendMsg(self.sock, pickle.dumps(self.DISCONNECT_MESSAGE), encode=False )

if __name__ == "__main__":
    client = Client((sys.argv[1], PORT))
    client.run()
    input('Game over. Press Enter to exit.')
    sys.exit()