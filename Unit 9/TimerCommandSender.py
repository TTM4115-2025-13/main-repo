import paho.mqtt.client as mqtt
import logging
from threading import Thread
import json
from appJar import gui

import random

MQTT_BROKER = 'mqtt20.iik.ntnu.no'
MQTT_PORT = 1883

MQTT_TOPIC_INPUT = 'ttm4115/team_13/command'
MQTT_TOPIC_OUTPUT = 'ttm4115/team_13/answer'

class Scooter:
    x = 5

    def __init__(self, id, distance, battery):
        self.id = id
        self.distance = distance
        self.battery = battery
        self.rented = False
        self.claimed = False


list_of_scooters = []

for i in range(3):
    dist = str(random.randint(100,500))+'m'
    battery = str(random.randint(0,100))+'%'
    list_of_scooters.append(Scooter(i,dist,battery))


class TimerCommandSenderComponent:
    """
    The component to send voice commands.
    """

    def on_connect(self, client, userdata, flags, rc):
        # we just log that we are connected
        self._logger.debug('MQTT connected to {}'.format(client))

    def on_message(self, client, userdata, msg):
        pass

    def __init__(self):
        # get the logger object for the component
        self._logger = logging.getLogger(__name__)
        print('logging under name {}.'.format(__name__))
        self._logger.info('Starting Component')

        # create a new MQTT client
        self._logger.debug('Connecting to MQTT broker {} at port {}'.format(MQTT_BROKER, MQTT_PORT))
        self.mqtt_client = mqtt.Client()
        # callback methods
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        # Connect to the broker
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        # start the internal loop to process MQTT messages
        self.mqtt_client.loop_start()

        self.create_gui()

    def create_gui(self):
        self.app = gui('Scooter App', '600x400')

        self.app.setBg('#EEEEEE')
        self.app.setFg('#000000')


        """
        def extract_timer_name(label):
            label = label.lower()
            if 'spaghetti' in label: return 'spaghetti'
            if 'green tea' in label: return 'green tea'
            if 'soft eggs' in label: return 'soft eggs'
            return None

        def extract_duration_seconds(label):
            label = label.lower()
            if 'spaghetti' in label: return 600
            if 'green tea' in label: return 120
            if 'soft eggs' in label: return 240
            return None
        """
        def extract_scooter_id(label):
            label = label.lower()
            scooter_id = int(label[4])
            return scooter_id

        def publish_command(command):
            payload = json.dumps(command)
            self._logger.info(command)
            self.mqtt_client.publish(MQTT_TOPIC_INPUT, payload=payload, qos=2)
        
        ### REQUEST LIST OF SCOOTERS
        self.app.startLabelFrame('List nearby scooters',0,0,1,2)
        def on_button_pressed_start():
            self.app.openLabelFrame('List nearby scooters')
            for i in range(len(list_of_scooters)):
                self.app.addLabel(
                    'l{}'.format(i),
                    'ID: {} distance : {}, battery : {}'
                        .format(list_of_scooters[i].id, list_of_scooters[i].distance, list_of_scooters[i].battery))
            self.app.openLabelFrame('Rent scooters')
            print('Creating rent list')
            for i in range(len(list_of_scooters)):
                self.app.addButton(
                    'ID: {} - Rent'
                    .format(list_of_scooters[i].id),
                    on_button_pressed_rent
                )
            self.app.openLabelFrame('Claim scooters')
            print('Creating claim list')
            for i in range(len(list_of_scooters)):
                self.app.addButton(
                    'ID: {} - Claim'
                    .format(list_of_scooters[i].id),
                    on_button_pressed_claim
                )
        self.app.addButton('List nearby scooters',on_button_pressed_start)
        self.app.stopLabelFrame()

        ### LIST OF SCOOTERS TO RENT
        self.app.startLabelFrame('Rent scooters',0,1,1)
        def on_button_pressed_rent(title):
            id = extract_scooter_id(title)
            print('rented scooter {}'.format(id))
            list_of_scooters[id].rented = True
            self.app.openLabelFrame('Active rentals')
            self.app.addButton(
                'ID: {} - Stop rental'.format(id),on_button_pressed_stop
            )

            command = {'command': 'rent_scooter', 'id' : id}
            # publish_command(command)
            
            #Commando for å sende "start rental"
        self.app.stopLabelFrame()

        ### LIST OF SCOOTERS TO CLAIM
        self.app.startLabelFrame('Claim scooters',0,2,1)
        def on_button_pressed_claim(title):
            id = extract_scooter_id(title)
            print('claimed scooter {}'.format(id))
            list_of_scooters[id].claimed = True
            self.app.openLabelFrame('Active claims')
            self.app.addButton(
                'ID: {} - Unclaim'.format(id),on_button_pressed_unclaim
            )
            #Commando for å sende "start rental"
        self.app.stopLabelFrame()

        ### LIST OF ACTIVE RENTALS
        self.app.startLabelFrame('Active rentals',1,1,1)
        def on_button_pressed_stop(title):
            id = extract_scooter_id(title)
            print('Stopped a rental of {}'.format(id))
            list_of_scooters[id].rented = False
            #Commando for å sende "stop rental"
            self.app.setButton('ID: {} - Stop rental'.format(id), '')
        self.app.stopLabelFrame()

        ### LIST OF CLAIMS
        self.app.startLabelFrame('Active claims',1,2,1)
        def on_button_pressed_unclaim(title):
            id = extract_scooter_id(title)
            print('Stopped a claim of {}'.format(id))
            list_of_scooters[id].claimed = False
            #Commando for å sende "stop claim"
            self.app.setButton('ID: {} - Unclaim'.format(id), '')
        self.app.stopLabelFrame()
        """
        self.app.startLabelFrame('Starting timers:')
        def on_button_pressed_start(title):
            name = extract_timer_name(title)
            duration = extract_duration_seconds(title)
            command = {"command": "new_timer", "name": name, "duration": duration}
            publish_command(command)
        self.app.addButton('Start Spaghetti Timer', on_button_pressed_start)
        self.app.addButton('Start Green Tea Timer', on_button_pressed_start)
        self.app.addButton('Start Soft Eggs Timer', on_button_pressed_start)
        self.app.stopLabelFrame()

        self.app.startLabelFrame('Stopping timers:')
        def on_button_pressed_stop(title):
            name = extract_timer_name(title)
            command = {"command": "cancel_timer", "name": name}
            publish_command(command)
        self.app.addButton('Cancel Spaghetti Timer', on_button_pressed_stop)
        self.app.addButton('Cancel Green Tea Timer', on_button_pressed_stop)
        self.app.addButton('Cancel Soft Eggs Timer', on_button_pressed_stop)
        self.app.stopLabelFrame()

        self.app.startLabelFrame('Asking for status:')
        def on_button_pressed_status(title):
            name = extract_timer_name(title)
            if name is None:
                command = {"command": "status_all_timers"}
            else:
                command = {"command": "status_single_timer", "name": name}
            publish_command(command)
        self.app.addButton('Get All Timers Status', on_button_pressed_status)
        self.app.addButton('Get Spaghetti Timer Status', on_button_pressed_status)
        self.app.addButton('Get Green Tea Timer Status', on_button_pressed_status)
        self.app.addButton('Get Soft Eggs Timer Status', on_button_pressed_status)
        self.app.stopLabelFrame()
        """
        self.app.go()


    def stop(self):
        """
        Stop the component.
        """
        # stop the MQTT client
        self.mqtt_client.loop_stop()


# logging.DEBUG: Most fine-grained logging, printing everything
# logging.INFO:  Only the most important informational log items
# logging.WARN:  Show only warnings and errors.
# logging.ERROR: Show only error messages.
debug_level = logging.DEBUG
logger = logging.getLogger(__name__)
logger.setLevel(debug_level)
ch = logging.StreamHandler()
ch.setLevel(debug_level)
formatter = logging.Formatter('%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

t = TimerCommandSenderComponent()