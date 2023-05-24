from config import Config
from input_listener import startup as input_listener_startup
from communication import startup as communication_startup

def main():
    input_listener_startup()
    communication_startup()

    if Config().WHAT_AM_I == "server":
        from server import Server
        Server()
    else:
        from client import Client
        Client()

if __name__ == '__main__':
    main()



