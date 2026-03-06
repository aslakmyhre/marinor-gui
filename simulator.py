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


def format_gps(lat, lon):
    """Returnerer en enkel GPS-pakke du kan bygge videre på."""
    return f"GPS {lat:.6f} {lon:.6f}"


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print("GPS-simulator startet.")
    print(f"Sender til {HOST}:{PORT} hvert {SEND_INTERVAL}s\n")

    global lat, lon

    while True:
        # Generer datapakke
        msg = format_gps(lat, lon)
        encoded = msg.encode()

        # Send data til hovedprogrammet
        sock.sendto(encoded, (HOST, PORT))

        # Vis i terminal
        print(f"➡️  Sendt: {msg}")

        # Oppdater posisjon (rett linje nord-øst)
        lat += LAT_STEP
        lon += LON_STEP

        time.sleep(SEND_INTERVAL)


if __name__ == "__main__":
    main()
