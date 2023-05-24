import json
import select
import socket
import time
from threading import Thread

from config import Config
from connection import Connection
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
                    try:
                        message = json.loads(message)
                    except:
                        print("Invalid message!")
                        continue
                    if message["type"] == "aleykumselam":
                        print(f"{message['myname']} says aleykumselam")
                        # save the ip address in a dictionary
                        Connection().connected_ips[sender_ip] = message["myname"]
                    else:
                        print("Invalid message type!")
            except Exception as e:
                print("What the hack is this, tcp?", str(e))
                continue


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
