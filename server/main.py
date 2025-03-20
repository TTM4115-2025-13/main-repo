# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
import json


hostName = "172.20.10.9"
serverPort = 8080


class Scooter():
    id = -1
    locked = False

    def __init__(self, id):
        self.id = id


class Server(BaseHTTPRequestHandler):
    scooters = {}

    def do_GET(self):
        payload = {}
        if self.path.split('?')[0] == '/add_scooter':
            sid = self.path.split('?')[1]
            #TODO: Sjekk at ikke allerede finnes med denne sid
            #TODO: Gjør noe dersom de ikke kommer med egen sid?
            self.scooters[sid] = Scooter(sid)
            print(f'INFO: Added scooter with ID {sid}')

        if self.path.split('?')[0] == '/list_available':
            payload['scooters'] = []
            for sid, scooter in self.scooters.items():
                if not scooter.locked:
                    payload['scooters'].append(scooter.id)

        if self.path.split('?')[0] == '/rent_scooter':
            sid = self.path.split('?')[1]
            #TODO: Hva om den allerede var låst?
            self.scooters[sid].locked = True

        if self.path.split('?')[0] == '/unrent_scooter':
            sid = self.path.split('?')[1]
            #TODO: Hva om den allerede var ulåst?
            self.scooters[sid].locked = False

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(payload), 'utf-8'))


if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), Server)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
