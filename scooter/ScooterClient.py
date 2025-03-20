import paho.mqtt.client as mqtt
from threading import Thread
import json
from stmpy import Driver
from ScooterLogic import ScooterLogic
import logging

class ScooterClient:
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
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except Exception as err:
            self._logger.error('Message sent to topic {} had no valid JSON. Message ignored. {}'.format(msg.topic, err))
            return

        match payload.get('msg'):
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

    debug_level = logging.DEBUG
    logger = logging.getLogger(__name__)
    logger.setLevel(debug_level)
    ch = logging.StreamHandler()
    ch.setLevel(debug_level)
    formatter = logging.Formatter('%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


    ScooterClient(1234)
