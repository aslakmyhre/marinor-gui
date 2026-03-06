import socket
import time

# --------------------------
# KONFIGURASJON
# --------------------------
SEND_INTERVAL = 0.2  # sekunder mellom hver sending
HOST = "127.0.0.1"   # mottaker (din hovedapplikasjon)
PORT = 5005          # port å sende til

# Startkoordinater – Trondheim sentrum
lat = 63.4305
lon = 10.3951

# Endringer per steg i grader
# Ca. nord-øst: +lat, +lon
# Disse verdiene gir rolig bevegelse (ca 3-4 m/s)
LAT_STEP = 0.00002
LON_STEP = 0.00004

start_time=time.perf_counter()
batterypercent = 100


def format_gps(lat, lon):
    return f"GPS {lat:.6f} {lon:.6f}"

def battery():
    global start_time, batterypercent
    current_time=time.perf_counter()
    if current_time-start_time >= 1:
        batterypercent -=1
        start_time=current_time
    return f"BATTERY {batterypercent:.6f}"

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print("GPS-simulator startet.")
    print(f"Sender til {HOST}:{PORT} hvert {SEND_INTERVAL}s\n")

    global lat, lon
    global start_time, batterypercent
    
    while True:
        # Generer datapakke
        msg_gps = format_gps(lat, lon)
        encoded_gps = msg_gps.encode()

        msg_battery = battery()
        encoded_battery=msg_battery.encode()

        # Send data til hovedprogrammet
        sock.sendto(encoded_gps, (HOST, PORT))
        print(f"GPS info sendt: {msg_gps}")
        sock.sendto(encoded_battery, (HOST, PORT))
        print(f"Batteri info sendt: {msg_battery}")


        # Oppdater posisjon (rett linje nord-øst)
        lat += LAT_STEP
        lon += LON_STEP

        time.sleep(SEND_INTERVAL)


if __name__ == "__main__":
    main()
