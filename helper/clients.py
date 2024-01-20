import time


# clients
class Client:
    def __init__(self):
        self.clients = {}

    def add_client(self, ip, port, chanel_watch):
        self.clients[f"{ip}:{port}"] = {
            "url": chanel_watch,
            "time_create": int(time.time()),
        }

    def get_client(self, ip, port):
        # check if client is in the list
        print(self.clients)
        if f"{ip}:{port}" not in self.clients:
            return False
        # update time_create
        self.clients[f"{ip}:{port}"]["time_create"] = int(time.time())
        return self.clients[f"{ip}:{port}"]["url"]

    def remove_client(self):
        current_time = int(time.time())
        for client in list(self.clients):
            if current_time - self.clients[client]["time_create"] > 15:
                del self.clients[client]
