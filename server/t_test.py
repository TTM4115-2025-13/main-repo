#Bare testing
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import time
import paho.mqtt.client as mqtt
from threading import Thread
import requests # type:ignore

hostName = 'localhost'
serverPort = 8080
scooterUnlockTimeout = 5

MQTT_BROKER = "mqtt20.iik.ntnu.no"
MQTT_PORT = 1883
mqttUnlockChannel = "ttm4115/team-13/scooter"
mqttResponseChannel = "ttm4115/team-13/scooter"


class Scooter():
    id = -1
    locked = False

    def __init__(self, id):
        self.id = id

class MQTTComponent:

    def on_connect(self, client, userdata, flags, rc):
        # we just log that we are connected
        print('MQTT connected to {}'.format(client))

    def on_message(self, client, userdata, msg):
        try:
            print("payload received at topic {}".format(msg.topic))
            payload = json.loads(msg.payload.decode("utf-8"))
        except Exception as err:
            print('Message sent to topic {} had no valid JSON. Message ignored. {}'.format(msg.topic, err))
            return
        
        command = payload.get('command')

        if command == 'scooter started':
            # expected : {"command": "scooter started", "id": int}
            id = payload.get('id')
            response = requests.get('http://'+hostName+':'+str(serverPort)+'/add_scooter?'+id)
            if response.status_code == 200:
                print('Scooter added successfully')
            pass
        elif command == 'Lock scooter':
            # ignore
            pass
        elif command == 'Unlock scooter':
            # ignore
            pass
        elif command == 'Unclaim scooter':
            # ignore
            pass
        elif command == 'Claim Scooter':
            # ignore
            pass
        else: 
            return print('Message sent to topic {} had no valid command. Message ignored'.format(msg.topic))
    def __init__(self):
        # create a new MQTT client
        print('Connecting to MQTT broker {} at port {}'.format(MQTT_BROKER, MQTT_PORT))
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        self.mqtt_client.subscribe(mqttResponseChannel)
        

        try:
            # line below should not have the () after the function!
            self.thread = Thread(target=self.mqtt_client.loop_forever)
            self.thread.start()
            print('thread started with id {}'.format(self.thread.getName()))
        except KeyboardInterrupt:
            print("Interrupted")
            self.mqtt_client.disconnect()


    def stop(self):
        """
        Stop the component.
        """
        # stop the MQTT client
        self.mqtt_client.loop_stop()
        print('stopped')
        


class myHandler(BaseHTTPRequestHandler):
    scooters = {}

    def do_GET(self):
        payload = {}

        if self.path.split('?')[0] == '/add_scooter':
            sid = self.path.split('?')[1]
            self.scooters[sid] = Scooter(sid)
            print(f'INFO: Added scooter with ID {sid}')
        if self.path.split('?')[0] == '/list_available':
            payload['scooters'] = []
            for sid, scooter in self.scooters.items():
                if not scooter.locked:
                    payload['scooters'].append(scooter.id)
        if self.path.split('?')[0] == '/rent_scooter':
            sid = self.path.split('?')[1]
            sendTime = time.time()            
            while time.time() < sendTime + scooterUnlockTimeout:
                continue
            self.scooters[sid].locked = True
            print(f'INFO: Rented scooter with ID {sid}')
        if self.path.split('?')[0] == '/unrent_scooter':
            sid = self.path.split('?')[1]
            self.scooters[sid].locked = False
            print(f'INFO: Unrented scooter with ID {sid}')

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(payload), 'utf-8'))


if __name__ == "__main__":        
    webServer = HTTPServer((hostName,serverPort),myHandler)
    print("Server started http://%s:%s" % (hostName, serverPort))
    mqttbroker = MQTTComponent()
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    webServer.server_close()
    mqttbroker.stop()
    print("Server stopped.")