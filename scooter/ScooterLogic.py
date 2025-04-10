import stmpy
import logging
from Display import display_text, display_status, display_battery
from ZoneLogic import try_to_stop;
from BatteryLogic import drain_battery
import json
import threading


MQTT_BROKER = 'mqtt20.iik.ntnu.no'
MQTT_PORT = 1883

MQTT_TOPIC_OUTPUT = 'ttm4115/team-13/scooter'

class ScooterLogic:
    """
    State Machine for a scooter.

    This is the support object for a state machine that models a single scooter.
    """
    def __init__(self, client):

        self._logger = logging.getLogger("ScooterLogic")
        self._logger.setLevel(logging.INFO)
        self._logger.info("Starting ScooterClient")
        self.client = client
        self.battery_level = 100

        # Transitions

        initial = {
            'source': 'initial', 
            'target': 'off'
        }

        start = {
            'source': 'off', 
            'target': 'available', 
            'trigger': 'start', 
            'effect': 'start_scooter'
        }

        claim = {
            'source': 'available',
            'target': 'claimed', 
            'trigger':'claim', 
            'effect': 'start_timer("t_claimed", 10000)'
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

        battery_drained = {
            'source': 'rented',
            'target': 'off',
            'trigger': 'battery_drained',
            'effect': 'stop_battery_drain; battery_drained' 
        }

        stop_rent = {
            'source': 'rented',
            'target': 'available', 
            'trigger': 'stop_renting', 
            'effect': 'stop_battery_drain'
        }


        # States
        off = {
            'name': 'off',
            'entry': 'off_state'
        }

        available = {
            'name': 'available',
            'entry': 'available_state',
        }

        claimed = {
            'name': 'claimed',
            'entry': 'claimed_state'
        }

        rented = {
            'name': 'rented',
            'entry': 'rented_state; stop_timer("t_claimed"); start_battery_drain',
        }
        
        self.stm = stmpy.Machine(name="scooterMachine", transitions=[initial, start, claim, unclaim,  rent, stop_rent, battery_drained], states=[available, off, claimed, rented], obj=self)


    # State methods
    def off_state(self):
        self._logger.info("Scooter off")

    def available_state(self):
        self._logger.info("Scooter available")
        display_battery(self.battery_level)

    def claimed_state(self):
        self._logger.info("Scooter claimed")
        payload = {
            'id': f'{self.client.id}',
            'command': 'scooter_claimed',
        }
        self.client.publish(MQTT_TOPIC_OUTPUT, json.dumps(payload))
        display_text("Claimed", [0, 255, 0])
        pass

    def rented_state(self):
        self._logger.info("Scooter rented")
        payload = {
            'id': f'{self.client.id}',
            'command': 'scooter_unlocked'
        }
        self.client.publish(MQTT_TOPIC_OUTPUT, json.dumps(payload))


    # Transition methods
    def start_scooter(self):
        self._logger.debug('Start scooter')
        payload = {
            'id': f'{self.client.id}',
            'command': 'scooter_started'
        }
        self.client.publish(MQTT_TOPIC_OUTPUT, json.dumps(payload))
        display_text("Started", [0, 255, 0])
        pass

    def unclaim_scooter(self):
        self._logger.debug('Unclaim scooter')
        payload = {
            'id': f'{self.client.id}',
            'command': 'scooter_unclaimed'
        }
        self.client.publish(MQTT_TOPIC_OUTPUT, json.dumps(payload))
        display_text("Unclaimed", [255, 0, 0])
        pass

    def unlock_scooter(self):
        display_status("Unlocked", [0, 255, 0])
        pass

    def lock_scooter(self):
        if self.stm.state != "rented":
            self._logger.warning("The state is not 'rented'")
        self._logger.info("Scooter attempting to stop")
        if try_to_stop():
            self._logger.debug('Lock scooter')
            payload = {
                'id': f'{self.client.id}',
                'command': 'scooter_locked'
            }
            self.client.publish(MQTT_TOPIC_OUTPUT, json.dumps(payload))
            self._logger.info("Scooter stopped and locked")
            self.stm.send("lock_scooter", "scooterMachine")
            display_status("Locked", [0, 0, 255])
        else:
            self._logger.warning("Scooter not stopped: Invalid zone")
            display_text("Invalid zone", [255, 0, 0])
        pass
    

    # Battery draining
    def start_battery_drain(self):
        """Starts a thread to drain the battery."""
        self._logger.debug("Battery drain started")
        self.running = True
        self.battery_thread = threading.Thread(target=drain_battery(self))
        self.battery_thread.start()

    def stop_battery_drain(self):
        """Stops the battery drain thread."""
        print("STOP BATTERY DRAIN")
        self._logger.info("Battery drain stopped")
        self.running = False
        if self.battery_thread:
            self.battery_thread.join()

    def battery_drained(self):
        self._logger.info("Battery drained")