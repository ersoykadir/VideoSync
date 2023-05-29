import json
import select
import socket
import time
from threading import Thread

from config import Config
from connection import Connection
from server import Server
from utils.send_packet import send_packet

hello_template = {"type": "hello", "myname": Config().NAME}

aleykumselam_template = {"type": "aleykumselam", "myname": Config().NAME}


def udp_broadcast():
    try:
        print("Starting up, broadcasting hello message!")
        message = json.dumps(hello_template)
        broadcast_ip = ".".join(Config().MY_IP.split(".")[0:3]) + ".255"
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("", 0))
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(message.encode("utf-8"), (broadcast_ip, Config().CONTROL_PORT))
    except Exception as e:
        print("Udp broadcast failed!", e)


def udp_listen():
    print("Listening for incoming udp messages")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("", Config().CONTROL_PORT))
    s.setblocking(0)
    while True:
        try:
            result = select.select([s], [], [])
            msg, addr = result[0][0].recvfrom(1024)
            sender_ip = addr[0]
            if not msg or sender_ip == Config().MY_IP:
                continue
            message = msg.strip().decode("utf-8")
            message = json.loads(message)
            if message["type"] != "hello":
                continue
            print(f"{message['myname']} says hello!")
            # send aleykumselam message
            aleykumselam_message = json.dumps(aleykumselam_template)
            aleykumselam_message = aleykumselam_message.encode("utf-8")
            send_packet(sender_ip, Config().CONTROL_PORT, aleykumselam_message)
            # add to addresses
            Connection().connected_ips[sender_ip] = message["myname"]
            print("Current addresses: ", Connection().connected_ips)
        except Exception as e:
            print("What the hack is this, udp?", e)


def tcp_listen():
    print("Listening for incoming tcp messages")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((Config().MY_IP, Config().CONTROL_PORT))
        s.listen()
        while True:
            try:
                conn, addr = s.accept()
                with conn:
                    line = conn.recv(1024)
                    sender_ip = addr[0]
                    if not line:
                        continue
                    message = line.strip().decode("utf-8")
                    if message[0] == '_': # send a response as soon as possibl
                        conn.sendall("_".encode())
                        continue
                    if message[0] == '#': # client has send a probe data
                        client_name = Connection().connected_ips[sender_ip]
                        _, receiver_name, delay = message.split('#')
                        Server().syncManager.update(client_name, receiver_name, delay)
                    try:
                        message = json.loads(message)
                    except:
                        print("Invalid message!")
                        continue
                    if message["type"] == "aleykumselam":
                        print(f"{message['myname']} says aleykumselam")
                        # l = conn.recv(1024)
                        # save the ip address in a dictionary
                        Connection().connected_ips[sender_ip] = message["myname"]
                    else:
                        print("Invalid message type!")
            except Exception as e:
                print("What the hack is this, tcp?", str(e))
                continue


def sync_delay():
    while True:
        try:
            for client_name in Connection().connected_ips.inv.keys():
                if client_name == 'server': continue

                ip_of_client = Connection().connected_ips.inv[client_name]
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((ip_of_client, Config().CONTROL_PORT))
                
                first_time = time.time()
                sock.sendall("_".encode()) # message does not matter
                _ = sock.recv(1024)
                second_time = time.time()
                me_to_client_delay = (second_time - first_time)*1000/2

                print(f"{client_name=} {me_to_client_delay=} in ms")

                # send to server if necessary
                if Config().NAME == 'server':
                    Server().syncManager.update('server', client_name, me_to_client_delay)
                else:
                    send_to_server(client_name, me_to_client_delay)
                    


        except Exception as e:
            continue
        time.sleep(5)

def send_to_server(me, other, delay):
    pass
def udp_broadcast_interval():
    while True:
        udp_broadcast()
        return
        time.sleep(60)

def startup():
    # Send hello message to all ips on the LAN
    tcp_thread = Thread(target=tcp_listen)
    tcp_thread.start()

    udp_thread = Thread(target=udp_listen)
    udp_thread.start()

    udp_broadcast_thread = Thread(target=udp_broadcast_interval)
    udp_broadcast_thread.start()

    sync_delay_thread = Thread(target=sync_delay)
    sync_delay_thread.start()
