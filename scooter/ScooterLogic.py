import stmpy
import logging
from Display import display_text, display_status, display_battery
from ZoneLogic import try_to_stop;
from BatteryLogic import drain_battery
import time
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
        self._logger = logging.getLogger(__name__)
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
            'trigger': 'lock_scooter', 
            'effect': 'stop_battery_drain'
        }

        # States

        off = {
            'name': 'off',
        }

        available = {
            'name': 'available',
            'entry': 'on_available',
        }

        claimed = {
            'name': 'claimed',
            'entry': 'claim_scooter'
        }

        rented = {
            'name': 'rented',
            'entry': 'stop_timer("t_claimed"); start_battery_drain',
            'stop_renting': 'lock_scooter()',
        }
        
        self.stm = stmpy.Machine(name="scooterMachine", transitions=[initial, start, claim, unclaim,  rent, stop_rent, battery_drained], states=[available, off, claimed, rented], obj=self)

    def start_scooter(self):
        self._logger.debug('Start scooter')
        self.client.publish(MQTT_TOPIC_OUTPUT, f'Scooter started')
        self._logger.info("Scooter started")
        display_text("Started", [0, 255, 0])
        pass

    def on_available(self):
        self._logger.info("Scooter available")
        display_battery(self.battery_level)

    def claim_scooter(self):
        self._logger.debug('Claim scooter')
        self.client.publish(MQTT_TOPIC_OUTPUT, f'Claim scooter')
        self._logger.info("Scooter claimed")
        display_text("Claimed", [0, 255, 0])
        pass

    def unclaim_scooter(self):
        self._logger.debug('Unclaim scooter')
        self.client.publish(MQTT_TOPIC_OUTPUT, f'Unclaim scooter')
        self._logger.info("Scooter unclaimed")
        display_text("Unclaimed", [255, 0, 0])
        pass

    def unlock_scooter(self):
        self._logger.debug('Unlock scooter')
        self.client.publish(MQTT_TOPIC_OUTPUT, f'Unlock scooter')
        self._logger.info("Scooter unlocked")
        display_status("Unlocked", [0, 255, 0])
        pass

    def lock_scooter(self):
        if self.stm.state != "rented":
            self._logger.warning("The state is not 'rented'")
        self._logger.info("Scooter attempting to stop")
        if try_to_stop():
            self._logger.debug('Lock scooter')
            self.client.publish(MQTT_TOPIC_OUTPUT, f'Lock scooter')
            self._logger.info("Scooter stopped and locked")
            display_status("Locked", [0, 0, 255])
            self.stm.send("lock_scooter", "scooterMachine")
        else:
            self._logger.warning("Scooter not stopped: Invalid zone")
            display_text("Invalid zone", [255, 0, 0])
        pass

    def start_battery_drain(self):
        """Starts a thread to drain the battery."""
        self.running = True
        self.battery_thread = threading.Thread(target=drain_battery(self))
        self.battery_thread.start()
        self._logger.info("Battery drain started")

    def stop_battery_drain(self):
        """Stops the battery drain thread."""
        self.running = False
        if self.battery_thread:
            self.battery_thread.join()
        self._logger.info("Battery drain stopped")

    def battery_drained(self):
        self._logger.warning("Battery drained")