import paho.mqtt.client as mqtt
import stmpy
import logging
from threading import Thread
import json

MQTT_BROKER = 'mqtt20.iik.ntnu.no'
MQTT_PORT = 1883

MQTT_TOPIC_INPUT = 'ttm4115/team_13/command'
MQTT_TOPIC_OUTPUT = 'ttm4115/team_13/answer'


class ScooterLogic:
    """
    State Machine for a scooter.

    This is the support object for a state machine that models a single scooter.
    """
    def __init__(self, name, duration, component):
        self._logger = logging.getLogger(__name__)
        self.name = name
        self.duration = duration
        self.component = component

        initial = {
            'source': 'initial', 
            'target': 'available'
        }

        claim = {
            'source': 'available',
            'target': 'claimed', 'trigger':'claim', 
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
            'trigger' 't_claimed' 
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
        
        self.stm = stmpy.Machine(name=name, transitions=[initial, send_position, claim, unclaim,  rent, stop_rent], states=[available, claimed, rented], obj=self)



    def send_position(self):
        self._logger.debug('{} timer completed'.format(self.name))
        self.component.mqtt_client.publish(MQTT_TOPIC_OUTPUT, f'Your {self.name} timer is ready!')
        pass

    def claim_scooter(self):
        self._logger.debug('Reporting status of timer {}'.format(self.name))
        self.component.mqtt_client.publish(MQTT_TOPIC_OUTPUT, f'You have {self.stm.get_timer("t")/1000} s left of the {self.name} timer.')
        pass

    def unclaim_scooter(self):
        self._logger.debug('Reporting status of timer {}'.format(self.name))
        self.component.mqtt_client.publish(MQTT_TOPIC_OUTPUT, f'You have {self.stm.get_timer("t")/1000} s left of the {self.name} timer.')
        pass

    def unlock_scooter(self):
        self._logger.debug('Reporting status of timer {}'.format(self.name))
        self.component.mqtt_client.publish(MQTT_TOPIC_OUTPUT, f'You have {self.stm.get_timer("t")/1000} s left of the {self.name} timer.')
        pass

    def lock_scooter(self):
        self._logger.debug('Reporting status of timer {}'.format(self.name))
        self.component.mqtt_client.publish(MQTT_TOPIC_OUTPUT, f'You have {self.stm.get_timer("t")/1000} s left of the {self.name} timer.')
        pass