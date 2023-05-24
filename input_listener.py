from threading import Thread
from communication import udp_broadcast
from server import Server

def input_listener():
    while True:
        data = input()
        # special commands
        try:
            if data == "list":
                udp_broadcast()
                print("Current addresses: ", Server.connected_ips)
            else:
                print("Invalid command!")
        except Exception as e:
            print("Invalid command!", e)

def startup():
    Thread(target=input_listener).start()
