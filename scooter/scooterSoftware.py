import paho.mqtt.client as mqtt
import stmpy
import logging
from threading import Thread
import json
from stmpy import Driver, Machine


MQTT_BROKER = 'mqtt20.iik.ntnu.no'
MQTT_PORT = 1883

MQTT_TOPIC_OUTPUT = 'ttm4115/team_13/scooter'




class ScooterLogic:
    """
    State Machine for a scooter.

    This is the support object for a state machine that models a single scooter.
    """
    def __init__(self, client):
        self._logger = logging.getLogger(__name__)
        self.client = client

        initial = {
            'source': 'initial', 
            'target': 'available'
        }

        claim = {
            'source': 'available',
            'target': 'claimed', 
            'trigger':'claim', 
            'effect': 'claim_scooter; start_timer("t_claimed")'
        }

        send_position = {
            'source': 'available',
            'target': 'available',
            'trigger': 't_pos',
            'effect': 'send_position'
        }

        unclaim = {
            'source': 'claimed', 
            'target': 'available', 
            'trigger': 't_claimed', 
            'effect': 'unclaim_scooter'
        }

        rent = {
            'source': 'claimed',
            'target': 'rented', 
            'trigger': 'unlock', 
            'effect': 'unlock_scooter'
        }

        stop_rent = {
            'source': 'rented',
            'target': 'available', 
            'trigger': 'stop_renting', 
            'effect': 'lock_scooter'
        }


        available = {
            'name': 'available',
            'entry': 'start_timer("t_pos", 3000)'
        }

        claimed = {
            'name': 'claimed',
            }

        rented = {
            'name': 'rented',
            'get_position': 'send_position()'
        }
        
        self.stm = stmpy.Machine(name="scooterMachine", transitions=[initial, send_position, claim, unclaim,  rent, stop_rent], states=[available, claimed, rented], obj=self)



    def send_position(self):
        self._logger.debug('Send position')
        #TODO Send position data
        self.client.publish(MQTT_TOPIC_OUTPUT, f'Scooter position data')
        pass

    def claim_scooter(self):
        self._logger.debug('Claim scooter')

        #TODO Stop scooter from being claimed
        self.client.mqtt_client.publish(MQTT_TOPIC_OUTPUT, f'Claim scooter')
        pass

    def unclaim_scooter(self):
        self._logger.debug('Unclaim scooter')
        self.client.mqtt_client.publish(MQTT_TOPIC_OUTPUT, f'Unclaim scooter')
        pass

    def unlock_scooter(self):
        self._logger.debug('Unlock scooter')
        self.client.mqtt_client.publish(MQTT_TOPIC_OUTPUT, f'Unlock scooter')
        pass

    def lock_scooter(self):
        self._logger.debug('Lock scooter')
        self.client.mqtt_client.publish(MQTT_TOPIC_OUTPUT, f'Lock scooter')
        pass

class MQTT_Scooter_Client:
    def __init__(self, id):
        self.id = id
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        # broker, port = 'iot.eclipse.org', 1883
        broker, port = "mqtt20.iik.ntnu.no", 1883

        scooter = ScooterLogic(self.client)
        scooter_machine = scooter.stm

        driver = Driver()
        driver.add_machine(scooter_machine)

        scooter.mqtt_client = self.client
        self.scooter = scooter
        self.stm_driver = driver

        driver.start()
        self.start(broker, port)

    def on_connect(self, client, userdata, flags, rc):
        print("on_connect(): {}".format(mqtt.connack_string(rc)))

    def on_message(self, client, userdata, msg):

        if msg.topic == "ttm4115/team-13/scooter/":
            print("Her kommer det noe")
            match msg.payload:
                case "claim":
                    self.stm_driver.send("claim", "scooterMachine")
                case "unlock":
                    self.stm_driver.send("unlock", "scooterMachine")
                case "stop_renting":
                    self.stm_driver.send("stop_renting", "scooterMachine")

    def start(self, broker, port):
        self.client.connect(broker, port)

        self.client.subscribe("ttm4115/team-13/scooter/#")

        try:
            # line below should not have the () after the function!
            thread = Thread(target=self.client.loop_forever)
            thread.start()
        except KeyboardInterrupt:
            print("Interrupted")
            self.client.disconnect()

if __name__=="__main__":
    print("Start")
    MQTT_Scooter_Client(1234)