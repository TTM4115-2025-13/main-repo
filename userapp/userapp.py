#import paho.mqtt.client as mqtt
#from threading import Thread
#import json
from appJar import gui
import logging

import random
import requests # type: ignore #Gidder ikkje fikse
import asyncio

# Used for simulating scooters
class Scooter:
    """
    Class for scooters\\
    Need to revaluate how necessary this is, we only deal with "id"s on the frontend
    """
    def __init__(self, id, distance, battery):
        self.id = id
        self.distance = distance #Needed?
        self.battery = battery #Needed?
        self.rented = False
        self.claimed = False


list_of_scooters = []

# Create 3 random scooters
for i in range(3):
    dist = str(random.randint(100,500))+'m'
    battery = str(random.randint(0,100))+'%'
    list_of_scooters.append(Scooter(i,dist,battery))


class Command:
    """
    Class for Commands\\
    Can just use dicts, but why not?
    """
    def __init__(self,title,id=None):
        self.title = title
        self.id = id


class UserApp:
    """
    The frontend component for users to list/rent/claim/unrent scooters.
    """

    def __init__(self, scooterList, server):

        self.scooterList = scooterList
        self.server = server

        # get the logger object for the component
        self._logger = logging.getLogger(__name__)
        print('logging under name {}.'.format(__name__))
        self._logger.info('Starting Component')

        self.create_gui()
    
    def CustomGETrequest(self,command):
        server = '127.20.10.9:8080'

        #Temp solution
        return 1
        url = self.server

        if command.title == 'list':
            url += '/list-scooters'
            response = requests.get(url)
            return response.json()
        elif command.title == 'rent':
            url += '/rent_scooter/{}'.format(command.id)
            response = requests.get(url)
            return response.json()
        elif command.title == 'unrent':
            url += '/unrent_scooter/{}'.format(command.id)
            response = requests.get(url)
            return response.json()
        elif command.title == 'claim':
            url += '/claim_scooter/{}'.format(command.id)
            response = requests.get(url)
            return response.json()
        elif command.title == 'unclaim':
            url += '/unclaim_scooter/{}'.format(command.id)
            response = requests.get(url)
            return response.json()
        else:
            #some error handling
            print('error')

    def create_gui(self):
        self.app = gui('Scooter App', '600x400')

        #Set colors. Does not work for buttons :)
        self.app.setBg('#EEEEEE')
        self.app.setFg('#000000')

        #Read label to get unique object
        def extract_scooter_id(label):
            label = label.lower()
            scooter_id = int(label[4])
            return scooter_id
        

        ### REQUEST LIST OF SCOOTERS
        self.app.startLabelFrame('List nearby scooters',0,0,1,2)
        def on_button_pressed_start():
            self.app.openLabelFrame('List nearby scooters')

            command = Command('list')
            #self.scooterList = self.CustomGETrequest(command)

            for i in range(len(self.scooterList)):
                self.app.addLabel(
                    'l{}'.format(i),
                    'ID: {} distance : {}, battery : {}'
                        .format(self.scooterList[i].id, self.scooterList[i].distance, self.scooterList[i].battery))
            self.app.openLabelFrame('Rent scooters')
            print('Creating rent list')
            for i in range(len(self.scooterList)):
                self.app.addButton(
                    'ID: {} - Rent'
                    .format(self.scooterList[i].id),
                    on_button_pressed_rent
                )
            self.app.openLabelFrame('Claim scooters')
            print('Creating claim list')
            for i in range(len(self.scooterList)):
                self.app.addButton(
                    'ID: {} - Claim'
                    .format(self.scooterList[i].id),
                    on_button_pressed_claim
                )
        self.app.addButton('List nearby scooters',on_button_pressed_start)
        self.app.stopLabelFrame()

        ### LIST OF SCOOTERS TO RENT
        self.app.startLabelFrame('Rent scooters',0,1,1)
        
        def on_button_pressed_rent(title):
            id = extract_scooter_id(title)
            print('rented scooter {}'.format(id))
            self.scooterList[id].rented = True
            self.app.openLabelFrame('Active rentals')
            self.app.addButton(
                'ID: {} - Stop rental'.format(id),on_button_pressed_stop
            )

            command = Command('rent',id)
            self.CustomGETrequest(command)


        self.app.stopLabelFrame()

        ### LIST OF SCOOTERS TO CLAIM
        self.app.startLabelFrame('Claim scooters',0,2,1)
        def on_button_pressed_claim(title):
            id = extract_scooter_id(title)
            print('claimed scooter {}'.format(id))
            self.scooterList[id].claimed = True
            self.app.openLabelFrame('Active claims')
            self.app.addButton(
                'ID: {} - Unclaim'.format(id),on_button_pressed_unclaim
            )

            command = Command('claim',id)
            self.CustomGETrequest(command)

        self.app.stopLabelFrame()


        ### LIST OF ACTIVE RENTALS
        self.app.startLabelFrame('Active rentals',1,1,1)
        def on_button_pressed_stop(title):
            id = extract_scooter_id(title)
            self.scooterList[id].rented = False
            print('Stopped a rental of {}'.format(id))

            command = Command('unrent',id)
            self.CustomGETrequest(command)

            self.app.removeButton('ID: {} - Stop rental'.format(id)) #Deletes button, underlying tkinter function

        self.app.stopLabelFrame()

        ### LIST OF CLAIMS
        self.app.startLabelFrame('Active claims',1,2,1)
        def on_button_pressed_unclaim(title):
            id = extract_scooter_id(title)
            print('Stopped a claim of {}'.format(id))
            self.scooterList[id].claimed = False

            self.app.removeButton('ID: {} - Unclaim'.format(id)) #Deletes button, underlying tkinter function

            command = Command('unclaim',id)
            self.CustomGETrequest(command)


        self.app.stopLabelFrame()
        
        """
        Execute the component. 
        """
        self.app.go()


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



# Async functions to ensure app can connect to server and get list
# Might remove and just start component

async def testConnection(server):
    canConnect = False

    try:
        response = requests.get(server) #Assumed to be enabled
        if response.status_code==200:
            print('Connection successfull')
            canConnect = True
        else:
            print(f'Request failed with code: {response.status_code}')
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as err:
        print(f'Failed to establish connection: {err}')
    except Exception as e:
        print(f'Unknown error occured : {e}')
        
    return canConnect

"""
async def getScooters():
    url = 'https://jsonplaceholder.typicode.com/posts/1'

    response = requests.get(url)
    parsedResponse = response.json()
    return parsedResponse
"""
async def runApp():
    #scooterList= await getScooters()

    #TEMP solution:
    scooterList = list_of_scooters

    able_to_connect = await testConnection('https://jsonplaceholder.typicode.com/posts/1')

    if able_to_connect:
        return UserApp(scooterList,'127.20.10.9:8080')
    else:
        print('Cannot connect to server')
        
    
app=asyncio.run(runApp())

