import stmpy
import logging
from Display import display_text, display_status, display_battery
from ZoneLogic import try_to_stop;
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
        print("start scooter")
        display_text("Started", [0, 255, 0])
        pass

    def on_available(self):
        print("Scooter available")
        display_battery(self.battery_level)

    def claim_scooter(self):
        self._logger.debug('Claim scooter')
        self.client.publish(MQTT_TOPIC_OUTPUT, f'Claim scooter')
        print("claim scooter")
        display_text("Claimed", [0, 255, 0])
        pass

    def unclaim_scooter(self):
        self._logger.debug('Unclaim scooter')
        self.client.publish(MQTT_TOPIC_OUTPUT, f'Unclaim scooter')
        print("unclaim scooter")
        display_text("Unclaimed", [255, 0, 0])
        pass

    def unlock_scooter(self):
        self._logger.debug('Unlock scooter')
        self.client.publish(MQTT_TOPIC_OUTPUT, f'Unlock scooter')
        print("unlock scooter")
        display_status("Unlocked", [0, 255, 0])
        pass

    def lock_scooter(self):
        if self.stm.state != "rented":
            print("THE STATE IS NOT rented")
        print("Scooter try to stop")
        if (try_to_stop()):
            self._logger.debug('Lock scooter')
            self.client.publish(MQTT_TOPIC_OUTPUT, f'Lock scooter')
            print("Scooter stopped and locked")
            display_status("Locked", [0, 0, 255])
            self.stm.send("lock_scooter", "scooterMachine")
        else:
            display_text("Invalid zone", [255, 0, 0])
            print("Scooter not stopped")
        pass

    def start_battery_drain(self):
        """Starts a thread to drain the battery."""
        self.running = True
        self.battery_thread = threading.Thread(target=self.drain_battery)
        self.battery_thread.start()

    def stop_battery_drain(self):
        """Stops the battery drain thread."""
        self.running = False
        if self.battery_thread:
            self.battery_thread.join()

    def drain_battery(self):
        """Drains the battery level over time."""
        while self.running:
            if(self.battery_level>0):
                self.battery_level -= 15
            display_battery(self.battery_level)
            self._logger.debug(f'Battery level: {self.battery_level}')
            print(f'Battery level: {self.battery_level}')
            if self.battery_level <= 0:
                self._logger.debug('Battery drained')
                self.stm.send("battery_drained", "scooterMachine")
                self.running = False
                display_text("Battery empty", [255, 0, 0])
                
            time.sleep(3)
    def battery_drained(self):
        print("Battery drained")