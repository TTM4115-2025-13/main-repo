from sense_hat import SenseHat

sense = SenseHat()
sense.set_imu_config(True, False, False)

def try_to_stop():
    """Try to stop the scooter."""
    mag = sense.get_compass_raw()
    x = mag['x']
    y = mag['y']
    z = mag['z']

    print(f"Magnetometer data: x={x}, y={y}, z={z}")

    if abs(mag['x']) > 100 or abs(mag['y']) > 100:
        return True
    
    return False