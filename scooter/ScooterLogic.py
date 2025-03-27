import stmpy
import logging
from Display import display_text, display_status


MQTT_BROKER = 'mqtt20.iik.ntnu.no'
MQTT_PORT = 1883

MQTT_TOPIC_OUTPUT = 'ttm4115/team-13/scooter'

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
            'effect': 'claim_scooter; start_timer("t_claimed", 10000)'
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
            'entry': 'start_timer("t_pos", 10000)'
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
        self.client.publish(MQTT_TOPIC_OUTPUT, f'Claim scooter')
        print("claim scooter")
        display_text("Scooter claimed", "green")
        pass

    def unclaim_scooter(self):
        self._logger.debug('Unclaim scooter')
        self.client.publish(MQTT_TOPIC_OUTPUT, f'Unclaim scooter')
        print("unclaim scooter")
        display_text("Scooter unclaimed", "red")
        pass

    def unlock_scooter(self):
        self._logger.debug('Unlock scooter')
        self.client.publish(MQTT_TOPIC_OUTPUT, f'Unlock scooter')
        print("unlock scooter")
        display_status("unlocked", "green")
        pass

    def lock_scooter(self):
        self._logger.debug('Lock scooter')
        self.client.publish(MQTT_TOPIC_OUTPUT, f'Lock scooter')
        print("lock scooter")
        display_status("locked", "red")
        pass