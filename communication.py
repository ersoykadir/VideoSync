import json
import select
import socket
import time
from threading import Thread
import os
from config import Config
from connection import Connection
from server import Server
from utils.send_packet import send_packet

hello_template = {"type": "hello", "myname": Config().NAME}

aleykumselam_template = {"type": "aleykumselam", "myname": Config().NAME}


def udp_broadcast():
    for i in range(5):
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
                        if Config().NAME != 'server': 
                            print('Go away!')
                            continue
                        client_name = Connection().connected_ips[sender_ip]
                        _, receiver_name, delay = message.split('#')
                        Server().syncManager.update(client_name, receiver_name, delay)
                        continue
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

def send_probe(ip_of_client):
    s = 0
    probe_count = 3
    for i in range(probe_count):
        first_time = time.perf_counter()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip_of_client, Config().CONTROL_PORT))
        sock.sendall("_".encode()) # message does not matter
        _ = sock.recv(1024)
        second_time = time.perf_counter()
        s += second_time - first_time
        time.sleep(0.1)
    return s/probe_count


def sync_delay():
    c = 0
    while True:
        c+=1
        try:
            for client_name in Connection().connected_ips.inv.keys():
                if client_name == 'server': continue # everybody sends everbody except no one probes the server

                ip_of_client = Connection().connected_ips.inv[client_name]
                avg = send_probe(ip_of_client)
                me_to_client_delay = (avg)*1000/2
                # print(f"{client_name=} {me_to_client_delay=} in ms")

                # send to server if necessary
                if Config().NAME == 'server':
                    Server().syncManager.update('server', client_name, me_to_client_delay)
                else:
                    send_to_server(client_name, me_to_client_delay)
        except Exception as e:
            print('sync_delay error', e)
        if c % 5 == 0 and Config().NAME == 'server':
            Server().syncManager.solve()
        time.sleep(1)        

def send_to_server(other, delay):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if 'server' not in Connection().connected_ips.inv.keys():
        raise Exception('Server is not connected!')
    sock.connect((Connection().connected_ips.inv['server'], Config().CONTROL_PORT))
    sock.sendall(f"#{other}#{delay}".encode()) # message does not matter

def udp_broadcast_interval():
    while True:
        udp_broadcast()
        return
        time.sleep(60)

def cleaner():
    while True:
        t = time.time()
        files = os.listdir('temp')
        for file in files:
            if file[-4:] != Config().FILE_EXTENSION: continue
            file_time = file.split(Config().FILE_EXTENSION)[0]
            if  t - float(file_time) > 60:
                os.remove(f'temp/{file}')
        time.sleep(60) # every minute


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

    cleaner_thread = Thread(target=cleaner)
    cleaner_thread.start()

