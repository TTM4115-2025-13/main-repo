from Display import display_battery, display_text
import logging
import time

def drain_battery(scooter):
    """Drains the battery level over time."""
    while scooter.running:
        if(scooter.battery_level>0):
            scooter.battery_level -= 15
        display_battery(scooter.battery_level)
        scooter._logger.info(f'Battery level: {scooter.battery_level}')
        if scooter.battery_level <= 0:
            scooter._logger.debug('Battery drained')
            scooter.stm.send("battery_drained", "scooterMachine")
            scooter.running = False
            display_text("Battery empty", [255, 0, 0])
            
        time.sleep(3)