import socket
import _thread
import time
import struct
import threading
import random

bufferSize = 1024
clients_array = []
all_members = 1
end_time = 10 + time.time()
count = 0
Players = {}
result1 = []
result2 = []
connections = []
addresses = []
num1 = random.randrange(1,4)
num2 = random.randrange(1,5)
answer = num1 + num2

def search_clients():
    global count
    locking_count = threading.RLock()

    try:
        # Create TCP socket, listening in port 2054
        TCP_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        TCP_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        TCP_socket.bind(("", 2054))
        TCP_socket.listen(1)
        # While the number of clients is less than 2, wait for more clients
        while  count < 2:
            print("hey")
            # Accept the next client
            client_socket, addr = TCP_socket.accept()
            print("im here")
            # Send the client to "add_new_client" function
            new_client = threading.Thread(target=add_new_client, args=(client_socket, addr))
            new_client.start()
            #with locking_count:
            #    count += 1  # count the clients
        return

    except:
        print("Wrong type of message received")


# The server adds the new client details to it's data structures
def add_new_client(client_socket, addr):
    global clients_array
    global Players
    global all_members
    global connections
    global addresses
    global count
    locking1 = threading.RLock()
    locking2 = threading.RLock()
    # Add the connection and address of the client to lists
    connections.append(client_socket)
    addresses.append(addr)
    print("new client here")
    try:
        # Save the name of the client
        name = client_socket.recv(1024).decode()
        if name:
            with locking1:
                clients_array.append(name)
            # While the server waiting for more clients
            while len(clients_array) < 2: 
                time.sleep(1)
            
            # Assign the player to the players dictionary 
            with locking2:
                print(name)
                if all_members == 1:
                    Players[name] = (client_socket,1)
                    all_members += 1
                else:
                    Players[name] = (client_socket,2)

            print("added players")
        # After the player added successfuly, increase the count
        count += 1
        return
    except:
        print("error occurred")


def start_game():
    # Creating welcoming message
    welcome_game = "Welcome to Quick Maths.\n" \
                       "Player 1:\n==\n" + list(Players.keys())[0]\
                       +"Player 2:\n==\n" + list(Players.keys())[1] +\
                       "\nPlease answer the following question as fast as you can:\n How much is " +str(num1) + " + " +str(num2)
    print("created welcoming message")
    # For each connection, send the welcoming message and send the player to the relevant function
    options = [Player1,Player2]
    for i in range(len(connections)):
        connections[i].send(welcome_game.encode())
        _thread.start_new_thread(options[i], (connections[i], addresses[i]))


# Player1's game ddd
def Player1(client,add):
    global result1
    locking = threading.RLock()
    # Give the client 10 seconds to answer
    time_after_10_sec = 10 + time.time()
    while time.time() < time_after_10_sec: 
        try:
            # Receive the answer from the client
            key = client.recv(bufferSize)
            player_ans = key.decode()
            # Create the result list: the time the answer received, the answer of the player, and the number of the player
            if player_ans:
                with locking:
                    result1 = [time.time(),player_ans,1]
                    return
        except:
            continue
    return 


# Player1's game
def Player2(client,add):
    global result2
    locking = threading.RLock()
    # Give the client 10 seconds to answer
    time_after_10_sec = 10 + time.time()
    while time.time() < time_after_10_sec:  
        try:
            # Receive the answer from the client
            key = client.recv(bufferSize)
            player_ans = key.decode()
            # Create the result list: the time the answer received, the answer of the player, and the number of the player
            if player_ans:
               with locking:
                    result2 = [time.time(),player_ans,2]
                    return
        except:
            continue
    return 



def check_results():
    print(result1)
    print(result2)
    # If nobody sent an answer (on time) - it's a draw
    if result1 == [] and result2 == []:
        finish_message = "Game over! Its a draw"
    
    # If only player 1 sent an answer or that player 1 sent answer before player 2
    elif result2 == [] or (result2!=[] and result1[0] < result2[0]):
        if int(result1[1]) == answer:
            finish_message = "\nGame over!\nThe correct answer was " + str(answer) + "!\n\n" \
                        + "Congratulations to the winners:\n==\n" + "" + list(Players.keys())[0]
        else:
            finish_message =  "\nGame over!\nThe correct answer was " + str(answer) + "!\n\n" \
                        + "Congratulations to the winners:\n==\n" + "" + list(Players.keys())[1]
    
    # If only player 2 sent an answer or that player 2 sent answer before player 1
    elif result1 == [] or (result1!=[] and result1[0] > result2[0]) :
        if int(result2[1]) == answer:
            finish_message = "\nGame over!\nThe correct answer was " + str(answer) + "!\n\n" \
                        + "Congratulations to the winners:\n==\n" + "" + list(Players.keys())[1]
        else:
            finish_message = "\nGame over!\nThe correct answer was " + str(answer) + "!\n\n" \
                        + "Congratulations to the winners:\n==\n" + "" + list(Players.keys())[0]
    print(finish_message)
    finish_message = u"\u001B[36m" + finish_message
    # Sent the results of the game to the players
    for i in range(len(connections)):
        connections[i].send(finish_message.encode())

def close_connections():
    global connections
    # For each connection we will close the connection
    for i in range(len(connections)):
        connections[i].close()
    connections = []
    addresses = []

def main():
    # Create UDP socket, listening in port 2054
    UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    UDP_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    UDP_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    UDP_socket.bind(('', 2054))
    print(u"\u001B[32mServer started' listening on IP address 172.1.0.22\u001B[32m")
    # Search for new clients
    thread = threading.Thread(target=search_clients, args=())
    thread.start()

    while time.time() < end_time and count<2:

        try:
            # Send broadcast message to all clients
            MSG = struct.pack('<3Q', 0xabcddcba, 0x2, 0xA)
            UDP_socket.sendto(MSG, ('<broadcast>', 13117))
            time.sleep(1)

        except:
            time.sleep(1)
    # If the number of clients is 2 - we can start the game
    if count == 2:
        start_game()
        time.sleep(10)
        check_results()
        close_connections()

    while time.time() < end_time:
        time.sleep(1)

    time.sleep(100)

    # The server closes
    print("Game over, sending out offer requests...")
    while True:
        # send
        MSG = struct.pack('<3Q', 0xabcddcba, 0x2, 0xA)
        UDP_socket.sendto(MSG, ('<broadcast>', 13117))
        time.sleep(1)

if __name__ == '__main__':
    main()