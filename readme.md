# E-scooter System

This project is an IoT-based e-scooter system consisting of three main components:

1. **Scooter software**: Manages the state and operations of the scooters.
2. **Server**: Handles HTTP requests and communicates with the scooters via MQTT.
3. **User app**: A GUI-based application for users to interact with the system.


## Project Structure

```
.gitignore
readme.md
scooter/
    Display.py
    requirements.txt
    ScooterClient.py
    ScooterLogic.py
server/
    main.py
Unit 9/
    TimerCommandSender.py
    TimerManager.py
userapp/
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

2. Start venv:

```
source ./venv/bin/activate
```

3. Install dependencies:

``` 
pip install -r requirements.txt
```

4. Start the scooter client:

``` 
python ScooterClient.py
```

---

## Server

The server handles HTTP requests and communicates with the scooters via MQTT.

### Features

- Add scooters
- List available scooters
- Rent and return scooters

### Running the Server

1. Navigate to the `server/` directory.
2. Start the server:
   ```shell
   python main.py
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
2. Start the app:
   ```shell
   python userapp.py
   ```

---

## Dependencies

The project uses the following Python libraries:

- `stmpy`: For state machine modeling.
- `paho-mqtt`: For MQTT communication.
- `sense-hat`: For Raspberry Pi Sense HAT display.
- `appJar`: For creating the user app GUI.

Install all dependencies using the provided `requirements.txt` files in their respective directories.

---

## Notes

- Ensure the MQTT broker is running and accessible at `mqtt20.iik.ntnu.no`.
- Update IP addresses and ports in the code if needed.
- The server runs on `http://172.20.10.9:8080` by default.
