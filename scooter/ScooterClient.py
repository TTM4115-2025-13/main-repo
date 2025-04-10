import argparse
import paho.mqtt.client as mqtt
from threading import Thread
import json
from stmpy import Driver
from ScooterLogic import ScooterLogic
import logging

class ScooterClient:
    def __init__(self, id):
        # Initialize logger
        self._logger = logging.getLogger("ScooterClient")
        self._logger.setLevel(logging.INFO)
        self._logger.info("ScooterClient initialized")

        self.client = mqtt.Client()
        self.client.id = id
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

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
        self._logger.info("Connected to MQTT broker with result code: {}".format(mqtt.connack_string(rc)))

    def on_message(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode("utf-8"))
        except Exception as err:
            self._logger.error('Message sent to topic {} had no valid JSON. Message ignored. {}'.format(message.topic, err))
            return

        self._logger.debug("Received message: {}".format(payload))
        match payload.get('command'):
            case "start":
                self._logger.info("Received 'start' command")
                self.stm_driver.send("start", "scooterMachine")
            case "claim":
                self._logger.info("Received 'claim' command")
                self.stm_driver.send("claim", "scooterMachine")
            case "unlock":
                self._logger.info("Received 'unlock' command")
                self.stm_driver.send("unlock", "scooterMachine")
            case "stop_renting":
                self._logger.info("Received 'stop_renting' command")
                self.stm_driver.send("stop_renting", "scooterMachine")
            case _:
                self._logger.warning("Unknown command received: {}".format(payload.get('command')))

    def start(self, broker, port):
        self._logger.info("Connecting to MQTT broker at {}:{}".format(broker, port))
        self.client.connect(broker, port)

        topic = f"ttm4115/team-13/scooter/{self.client.id}/command"
        self.client.subscribe(topic)
        self._logger.info("Subscribed to topic: {}".format(topic))

        try:
            thread = Thread(target=self.client.loop_forever)
            thread.start()
            self._logger.info("MQTT client loop started")
        except KeyboardInterrupt:
            self._logger.info("Interrupted by user, disconnecting MQTT client")
            self.client.disconnect()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    parser = argparse.ArgumentParser(description="Start the ScooterClient.")
    parser.add_argument(
        "--id",
        type=int,
        default=1234,
        help="The ID of the scooter (default: 1234)"
    )
    args = parser.parse_args()

    ScooterClient(args.id)
