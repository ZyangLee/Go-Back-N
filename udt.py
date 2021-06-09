# udt.py - Unreliable data transfer using UDP
import random

DROP_PROB = 50


# Send a packet across the unreliable channel
# Packet may be lost
def send(packet, sock, addr):
    if random.randint(0, DROP_PROB) > 0:
        if random.randint(0, DROP_PROB) == 0:  # 1/50概率出现错帧
            packet += b'\xff'
        sock.sendto(packet, addr)

    return


# Receive a packet from the unreliable channel
def recv(sock):
    packet, addr = sock.recvfrom(4096)
    return packet, addr
