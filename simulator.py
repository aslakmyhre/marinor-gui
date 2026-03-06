import socket
import time
import math


#Copilot-simulator

HOST = "127.0.0.1"
PORT = 5000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

lat0 = 63.43074
lon0 = 10.40401

t = 0.0
while True:
    lat = lat0 + 0.001 * math.sin(t)
    lon = lon0 + 0.001 * math.cos(t)
    msg = f"{lat:.6f},{lon:.6f}\n".encode()
    sock.sendto(msg, (HOST, PORT))
    t += 0.1
    time.sleep(0.1)