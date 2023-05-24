from client import Client
from communication import startup as communication_startup
from config import Config
from input_listener import startup as input_listener_startup
from server import Server


def main():
    input_listener_startup()
    communication_startup()

    if Config().WHAT_AM_I == "server":
        Server()
    else:
        Client()

if __name__ == '__main__':
    main()



