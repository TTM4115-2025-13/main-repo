from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import time
import paho.mqtt.client as mqtt
from threading import Thread
import sys

hostName = sys.argv[1]
serverPort = int(sys.argv[2])

scooterUnlockTimeout = 5

MQTT_BROKER = "mqtt20.iik.ntnu.no"
MQTT_PORT = 1883
mqttUnlockChannel = "ttm4115/team-13/scooter"
mqttResponseChannel = "ttm4115/team-13/scooter"


class Scooter():
    id = -1
    rented = False
    claimed = False
    battery = 100
    parked = True
    invalidParking = False

    def __init__(self, id):
        self.id = id



class MQTTComponent:

    def on_connect(self, client, userdata, flags, rc):
        # we just log that we are connected
        print('MQTT connected to {}'.format(client))

    def on_message(self, client, userdata, msg):
        try:
            #print("payload received at topic {}".format(msg.topic))
            payload = json.loads(msg.payload.decode("utf-8"))
        except Exception as err:
            print('Message sent to topic {} had no valid JSON. Message ignored. {}'.format(msg.topic, err))
            return
        
        # Always expects "command" and "id"
        command = payload.get('command')
        sid = payload.get('id')

        if command == 'scooter_started':
            self.httpserver.scooters[sid] = Scooter(sid)
            print(f'INFO: Scooter connected to network with ID {sid}')
        elif command == 'scooter_unlocked':
            self.httpserver.scooters[sid].rented = True
            self.httpserver.scooters[sid].parked = False
            # ignore
            pass
        elif command == 'scooter_locked':
            self.httpserver.scooters[sid].rented = False
            self.httpserver.scooters[sid].invalidParking = False
            self.httpserver.scooters[sid].parked = True
            # ignore
            pass
        elif command == 'scooter_claimed':
            self.httpserver.scooters[sid].claimed = True
            # ignore
            pass
        elif command == 'scooter_unclaimed':
            self.httpserver.scooters[sid].claimed = False
            # ignore
            pass
        elif command == 'unable_to_lock':
            self.httpserver.scooters[sid].invalidParking = True
        else: 
            return print('Message sent to topic {} had no valid command. Message ignored'.format(msg.topic))
        
    def __init__(self, httpserver):
        # create a new MQTT client
        print('Connecting to MQTT broker {} at port {}'.format(MQTT_BROKER, MQTT_PORT))
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        self.mqtt_client.subscribe(mqttResponseChannel)

        # Save reference to http server
        self.httpserver = httpserver
        self.httpserver.mqtt_client = self.mqtt_client
        

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
    mqtt_client: mqtt.Client = None

    def do_GET(self):
        payload = {}

        # if self.path.split('?')[0] == '/add_scooter':
        #     sid = self.path.split('?')[1]
        #     self.scooters[sid] = Scooter(sid)
        #     print(f'INFO: Added scooter with ID {sid}')

        if self.path.split('?')[0] == '/list_available':
            payload['scooters'] = []
            for sid, scooter in self.scooters.items():
                if not (scooter.rented or scooter.claimed):
                    payload['scooters'].append(scooter.id)

        if self.path.split('?')[0] == '/rent_scooter':
            sid = self.path.split('?')[1]
            self.mqtt_client.publish(mqttUnlockChannel+'/1234/command', json.dumps({"id":sid,"command":"unlock"}))
            sendTime = time.time()
            payload['status'] = 'failure'   
            while time.time() < sendTime + scooterUnlockTimeout:
                if self.scooters[sid].rented:
                    payload['status'] = 'success'
                    break
            if payload['status'] == 'success':
                print(f'INFO: Rented scooter with ID {sid}')
            else:
                print(f'WARNING: Failed to rent scooter with ID {sid}. No response from scooter')

        if self.path.split('?')[0] == '/unrent_scooter':
            #TODO: Check that message comes from the scooter owner
            sid = self.path.split('?')[1]
            self.mqtt_client.publish(mqttUnlockChannel+'/1234/command', json.dumps({"id":sid,"command":"stop_renting"}))
            sendTime = time.time()
            status = 'failure'
            while time.time() < sendTime + scooterUnlockTimeout:
                if self.scooters[sid].rented == False:
                    status = 'success'
                    break
            if status == 'success':
                print(f'INFO: Unrented scooter with ID {sid}')
            elif self.scooters[sid].invalidParking:
                print(f'INFO: Scooter with ID {sid} has invalid parking')
                status = 'failure'
                payload['errormessage'] = 'invalid_parking'
            else:
                print(f'WARNING: Failed to unrent scooter with ID {sid}. No response from scooter')
                self.scooters[sid].rented = False

            # User should be able to stop paying even if the scooter to server connection fails
            #TODO: Mark scooter as broken or some shit
            
            payload['status'] = status


        if self.path.split('?')[0] == '/claim_scooter':
            sid = self.path.split('?')[1]
            self.mqtt_client.publish(mqttUnlockChannel+'/1234/command', json.dumps({"id":sid,"command":"claim"}))
            sendTime = time.time()            
            payload['status'] = 'failure'
            while time.time() < sendTime + scooterUnlockTimeout:
                if self.scooters[sid].claimed:
                    payload['status'] = 'success'
                    break
            if payload['status'] == 'success':
                print(f'INFO: Claimed scooter with ID {sid}')
            else:
                print(f'WARNING: Failed to claim scooter with ID {sid}. No response from scooter')

        if self.path.split('?')[0] == '/unclaim_scooter':
            #TODO: Check that the client has claimed the scooter
            sid = self.path.split('?')[1]
            self.mqtt_client.publish(mqttUnlockChannel+'/1234/command', json.dumps({"id":sid,"command":"unclaim"}))
            sendTime = time.time()
            status = 'failure'
            while time.time() < sendTime + scooterUnlockTimeout:
                if self.scooters[sid].claimed == False:
                    status = 'success'
                    break
            if status == 'success':
                print(f'INFO: Unclaimed scooter with ID {sid}')
            else:
                print(f'WARNING: Failed to unclaim scooter with ID {sid}. No response from scooter')
            # User should be able to stop paying even if the scooter to server connection fails
            #TODO: Mark scooter as broken or some shit
            payload['status'] = 'success'
            self.scooters[sid].claimed = False


        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(payload), 'utf-8'))


if __name__ == "__main__":
    mqttbroker = MQTTComponent(myHandler)
    webServer = HTTPServer((hostName,serverPort),myHandler)
    print("Server started http://%s:%s" % (hostName, serverPort))
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    webServer.server_close()
    mqttbroker.stop()
    print("Server stopped.")