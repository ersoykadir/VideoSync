import socket


def send_packet(target_ip, target_port, message, timeout=5):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((target_ip, target_port))
        sock.sendall(message)
    except Exception as e:
        print("Connection refused", e, target_ip)
