
class HandleInput:
    def __init__(self, gui):
        self.gui = gui
    def start_udp_receiver(self):
        import socket, threading
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("0.0.0.0", 5005))

        def receiver():
            while True:
                data, _ = sock.recvfrom(1024)
                msg = data.decode().strip()
                parts = msg.split()
                if len(parts) == 3 and parts[0] == "GPS":
                    try:
                        lat = float(parts[1]); lon = float(parts[2])
                    except ValueError:
                        continue
                    self.gui.window.after(0,self.gui.map_controller.update_boat_marker,lat, lon, None, None)
                elif len(parts) == 2 and parts[0] == "BATTERY":
                    try:
                        battery = int(parts[1])
                        self.gui.window.after(0, self.gui.battery_bar.configure(value=battery))
                    except ValueError:
                        continue

        threading.Thread(target=receiver, daemon=True).start()