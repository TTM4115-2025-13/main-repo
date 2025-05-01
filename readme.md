# E-scooter System

![Supported Python version](https://img.shields.io/badge/python-3.12-blue)

This project is an IoT-based e-scooter system consisting of three main components:

1. **Scooter software**: Manages the state and operations of the scooters.
2. **Server**: Handles HTTP requests and communicates with the scooters via MQTT.
3. **User app**: A GUI-based application for users to interact with the system.


## Project Structure

```
.gitignore
readme.md
scooter/
    requirements.txt
    Display.py
    ScooterClient.py
    ScooterLogic.py
    ZoneLogic.py
server/
    requirements.txt
    serverapp.py
userapp/
    requirements.txt
    userapp.py
```

---

## Scooter software
The scooter software runs on a Raspberry Pi and uses the Sense HAT for display and MQTT for communication.

### Setup
1. Transfer files to raspberry pi:

```shell
scp -r  .\scooter\ gruppe13@raspberrypi13:~/
```

2. Connect to raspberry pi

```shell
ssh gruppe13@raspberrypi13:~/scooter
```

3. Setup a [python venv](https://docs.python.org/3/library/venv.html) and start it:

```
source ./venv/bin/activate
```

4. Install dependencies:

``` 
pip install -r requirements.txt
```

1. Start the scooter client:

``` 
python ScooterClient.py
```

### If problems with RTIMU:
- Clone RTIMULib:
`git clone https://github.com/RPi-Distro/RTIMULib/ RTIMU`
`cd RTIMU/Linux/python`
- Follow instruction in RTIMULib/Linux/python:
`sudo apt install python3-dev`
`python setup.py build`
`python setup.py install`
- Install libopenjp2-7:
`sudo apt install libopenjp2-7`
- Install sense-hat:
`sudo apt install sense-hat`
---

## Server

The server handles HTTP requests and communicates with the scooters via MQTT.

### Features

- Add scooters
- List available scooters
- Rent and return scooters

### Running the Server

1. Navigate to the `server/` directory.
2. Start the server with arguments: source IP for server and source port:
   ```shell
   python serverapp.py SOURCE PORT
   ```
    * Example:
    ```
    python serverapp.py 10.52.195.76 8080
    ```

---

## User App

The user app provides a GUI for users to interact with the system.

### Features

- List nearby scooters
- Rent and return scooters
- Claim and unclaim scooters

### Running the User App

1. Navigate to the `userapp/` directory.
2. Start the userapp with arguments: source IP for server and source port:
   ```shell
   python userapp.py SOURCE PORT
   ```
    * Example:
    ```
    python userapp.py 10.52.195.76 8080
    ```

---

## Dependencies

The project uses the following Python libraries:

- `stmpy`: For state machine modeling.
- `paho-mqtt`: For MQTT communication.
- `sense-hat`: For Raspberry Pi Sense HAT display.
- `appJar`: For creating the user app GUI.
- `Requests`: For promises in Python
Install all dependencies using the provided `requirements.txt` files in their respective directories.

---

## Notes
- Current implemtation does not work with the latest version of python (3.13)
    - Python 3.12 has been tested and works, older versions may work
- Ensure the MQTT broker is running and accessible at `mqtt20.iik.ntnu.no`.
- Ensure the same IP/PORT combination is used for both server and userapp
