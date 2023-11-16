# Projet-IOT-4IRC

## Member

- **Elea MACHILLOT**
- **Adrien JAUFRE**
- **Romanin CHARDARD**
- **Elwan LEFEVRE**

## Project Architecture

The project is composed of 5 core element and an optional one :

- **Microbit capteur** : Is used as a sensor to gather data and send them trough radio frequency
- **Microbit passerel** : Is used as an antenna to receive data and send message to the sensor
- [**microbit-serial**](microbit-serial.py) : Is used as a gateway from the Microbit, the computer and the Android App 
- **App/** : Contain the Python API
- **appliAndroid** : Contain the Android App
- [**discord_bot_iot.py**](discord_bot_iot.py) : Is used as a third service tool to set up the database and test the APi

All the project is based on the following schema : 

![Archi V1](images/archi-v1.png)