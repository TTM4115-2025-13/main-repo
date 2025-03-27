import paho.mqtt.client as mqtt
import logging
from threading import Thread
import json
from appJar import gui

import random
import requests
import asyncio


MQTT_BROKER = 'mqtt20.iik.ntnu.no'
MQTT_PORT = 1883

MQTT_TOPIC_INPUT = 'ttm4115/team_13/command'
MQTT_TOPIC_OUTPUT = 'ttm4115/team_13/answer'

# Used for simulating scooters
class Scooter:
    """
    Temp class for parsing JSON data
    """
    def __init__(self, id, distance, battery):
        self.id = id
        self.distance = distance
        self.battery = battery
        self.rented = False
        self.claimed = False


list_of_scooters = []

# Create 3 random scooters
for i in range(3):
    dist = str(random.randint(100,500))+'m'
    battery = str(random.randint(0,100))+'%'
    list_of_scooters.append(Scooter(i,dist,battery))


class TimerCommandSenderComponent:
    """
    The component to send voice commands.
    """

    ### MQTT-greier, slett?
    def on_connect(self, client, userdata, flags, rc):
        # we just log that we are connected
        self._logger.debug('MQTT connected to {}'.format(client))
    ### MQTT-greier, slett?
    def on_message(self, client, userdata, msg):
        pass

    def __init__(self, scooterList):

        self.scooterList = scooterList

        ### MQTT-greier, slett?

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

        #Set colors, could be changed 
        self.app.setBg('#EEEEEE') #Background color
        self.app.setFg('#000000') #Foreground color

        #Read label to get unique object
        def extract_scooter_id(label):
            label = label.lower()
            scooter_id = int(label[4])
            return scooter_id

        ### MQTT-greier, slett?
        def publish_command(command):
            payload = json.dumps(command)
            self._logger.info(command)
            self.mqtt_client.publish(MQTT_TOPIC_INPUT, payload=payload, qos=2)
        
        ### REQUEST LIST OF SCOOTERS
        self.app.startLabelFrame('List nearby scooters',0,0,1,2)
        def on_button_pressed_start():
            self.app.openLabelFrame('List nearby scooters')

            #Commando for å liste scootere? Alt. HTTP GET 

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

            command = {'command': 'start_rental', 'id' : id}
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
            #Commando for å sende "start claim"
            command = {'command': 'start_claim', 'id' : id}
            # publish_command(command)

        self.app.stopLabelFrame()

        ### LIST OF ACTIVE RENTALS
        self.app.startLabelFrame('Active rentals',1,1,1)
        def on_button_pressed_stop(title):
            id = extract_scooter_id(title)
            print('Stopped a rental of {}'.format(id))
            list_of_scooters[id].rented = False
            #Commando for å sende "stop rental"

            self.app.setButton('ID: {} - Stop rental'.format(id), '') #Null peiling på kossen man sletter knapper

            command = {'command': 'stop_rental', 'id' : id}
            # publish_command(command)

        self.app.stopLabelFrame()

        ### LIST OF CLAIMS
        self.app.startLabelFrame('Active claims',1,2,1)
        def on_button_pressed_unclaim(title):
            id = extract_scooter_id(title)
            print('Stopped a claim of {}'.format(id))
            list_of_scooters[id].claimed = False
            self.app.setButton('ID: {} - Unclaim'.format(id), '') #Null peiling på kossen man sletter knapper

            #Commando for å sende "stop claim"
            command = {'command': 'unclaim_scooter', 'id' : id}
            # publish_command(command)

        self.app.stopLabelFrame()
        



        """
        Execute the component. 
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

"""

debug_level = logging.DEBUG
logger = logging.getLogger(__name__)
logger.setLevel(debug_level)
ch = logging.StreamHandler()
ch.setLevel(debug_level)
formatter = logging.Formatter('%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

"""


# Async functions to ensure app can connect to server
async def getScooters():
    url = 'https://jsonplaceholder.typicode.com/posts/1'

    response = requests.get(url)
    parsedResponse = response.json()
    print(parsedResponse['title'])
    return parsedResponse

async def runApp():
    scooterList= await getScooters()
    return TimerCommandSenderComponent(scooterList)
    



t=asyncio.run(runApp())


#t = TimerCommandSenderComponent()