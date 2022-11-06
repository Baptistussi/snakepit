import socket
import threading
import sys
import pickle

import colors
from libgame import Server_Game
from libsnake import Messages, Server_Snake

class Server(Messages):
    PORT = 5050
    HOST = '192.168.0.17' #socket.gethostbyname(socket.gethostname())
    ADDR = (HOST, PORT)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connections = []
    DISCONNECT_MESSAGE = '!DISCONNECT'

    def __init__(self):
        self.sock.settimeout(1) # important so it finishes properly
        self.sock.bind(self.ADDR)
        self.sock.listen()
        print("[STARTING] server is starting...")
        self.players = {}
        self.game = Server_Game( web_interface=self, snakes=self.players )
    
    def broadcast(self, msg):
        for conn in self.connections:
                self.sendMsg(conn, msg, encode=False)

    def new_player_connect(self, player_data):
        msg = { 'type':'new_player',
                'player_data': player_data }
        return self.broadcast( pickle.dumps(msg) )

    def player_disconnect(self, player_name):
        msg = { 'type':'player_disconnect',
                'player_name': player_name }
        return self.broadcast( pickle.dumps(msg) )

    def start_game_on_clients(self):
        msg = { 'type':'all_players_ready' }
        return self.broadcast( pickle.dumps(msg) )

    def update_snake(self, player_name, snake_data):
        msg = { 'type':'snake_update',
                    'player_name':player_name,
                    'snake_data':snake_data }
        return self.broadcast( pickle.dumps(msg) )

    def update_food(self, food_data):
        msg = { 'type':'food_update',
                    'food_data':food_data }
        return self.broadcast( pickle.dumps(msg) )

    def end_game(self, **kwargs):
        msg = { 'type':'game_over' }
        return self.broadcast( pickle.dumps(msg) )
    
    def check_all_ready(self):
        all_ready = True
        for player in self.players.values():
            if player.ready == False: all_ready = False
        if all_ready:
            self.run_game()

    def interpret_msg(self, msg, sender_name):
        mtype = msg['type']
        
        match mtype:
            case 'player_ready':
                self.players[ sender_name ].ready = True
                self.check_all_ready()
            case 'command':
                self.game.control(sender_name, msg['key'])

    def client_handler(self, conn, addr):
        "Handles connection with each client player."
        # get the player name
        has_name = False
        while not has_name:
            player_name = self.recvMsg(conn)
            if player_name not in self.players.keys():
                has_name = True
                self.sendMsg(conn, 'OK')
            else:
                self.sendMsg(conn, 'TAKEN')
        
        # decide player color
        player_color = colors.get_random_color()
        # creat new player object
        self.players[ player_name ] = Server_Snake(self.game, player_name, player_color)

        # tell players of this player
        self.new_player_connect( player_data={'name': player_name, 'color': player_color } )
        print(f"[NEW CONNECTION] {player_name} at {addr} connected.")
                
        connected = True
        while connected:
            msg = pickle.loads( self.recvMsg(conn, decode=False) )
            if not msg or msg == self.DISCONNECT_MESSAGE:
                connected = False
                self.connections.remove(conn)
                self.player_disconnect(player_name=player_name)
            else:
                self.interpret_msg(msg=msg, sender_name=player_name)
        conn.close()
    
    def run_server(self):
        print(f"[LISTENING] Server is listening on {self.HOST}.")
        while not self.game.game_over:
            try:
                conn, addr = self.sock.accept()
                client_thread = threading.Thread(target=self.client_handler, args=(conn, addr) )
                client_thread.daemon = True
                client_thread.start()
                self.connections.append(conn)
                print(f"[ACTIVE CONNECTIONS] {threading.active_count() -1 }" )
            except socket.timeout:
                pass
    
    def run_game(self):
        main_game_thread = threading.Thread(target=self.game.loop_game)
        main_game_thread.daemon = True
        main_game_thread.start()
            

if __name__ == "__main__":
    server=Server()
    server.run_server()