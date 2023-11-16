# Program to control gateway between Android application
# and microcontroller through USB tty
import socketserver
import serial
import threading
import requests
import json
import logging


loggers = {
    "udp_logger": logging.getLogger("Mbit_UDP_Server"),
    "uart_logger": logging.getLogger("Mbit_UART_Server"),
    "glob_logger": logging.getLogger("Mbit_Global_Logger")
}

# Create handler
c_handler = logging.StreamHandler()  # Show logs in console
f_handler = logging.FileHandler('logs/app.log')  # Show log in files
c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.INFO)

# Set handler format
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
f_format = logging.Formatter('[%(asctime)s] - %(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

for logger in loggers.values():
    # Add handler to logger

    logger.addHandler(c_handler)
    logger.addHandler(f_handler)


with open('config.json', 'r') as conf_file:
    config = json.load(conf_file)
    loggers["glob_logger"].info("Config Loaded")

# Config section
HOST: str = config['SERIAL']['HOST']  # Host IP used for the gateway server Type
UDP_PORT: int = config['SERIAL']['PORT']  # Port used by the UDP setup
MICRO_COMMANDS: list[str] = config['SERIAL']['MICRO_COMMANDS']  # List of microbit command
APPID: int = config['SERIAL']['APP_ID']  # App ID used by the radio signal
FILENAME: str = config['SERIAL']['FILENAME']  # txt file used to register data
API_URL: str = config['API']['IP']  # Ip of the rest API used to store the data from the sensor
API_USER: str = config['API']['USER']
API_PASSWORD: str = config['API']['PASSWORD']


# Auth of the user in the API
headers = {'Content-Type': 'application/x-www-form-urlencoded'}
data = {'username': API_USER, 'password': API_PASSWORD}
response = requests.post(f"http://{API_URL}/token", headers=headers, data=data)
if response.status_code != 200:
    loggers["glob_logger"].error("Failed to authenticated in the API")
    exit(-1)
# Header used to set the context for API request

headers: dict[str] = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {response.json()["access_token"]}'
}


class ThreadedUDPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self) -> None:
        # Function that handle the message coming from the UDP server
        data_rec: str = self.request[0].strip().decode('utf-8')  # Decode data to format utf-8
        socket = self.request[1]  # Get the socket used for the communication
        current_thread = threading.current_thread()  # Go in a thread to not hinder other traffic
        loggers["udp_logger"].info(f"{current_thread.name}: client: {self.client_address}, wrote: {data_rec}") # Display message from client
        if data_rec != "":  # If we Get Data
            if data_rec in MICRO_COMMANDS:  # If value in the list MICRO_COMMANDS

                # Send message through UART

                sendUARTMessage(f'{APPID}:{data_rec}'.encode())  # Send the received message and add the APP ID via UART
                socket.sendto('{"message": "Success"}'.encode(), self.client_address)  # Send the success to client

            elif data_rec == "getValues()":  # If getValues()

                x = requests.get(f'http://{API_URL}/data/last/')  # Get the last value through the API
                loggers["udp_logger"].info(x.content)
                socket.sendto(x.content, self.client_address)  # Send the API value to the client
            else:  # If no match
                loggers["udp_logger"].warning("Unknown message: ", data_rec)  # print the message in logs


class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass


# send serial message
SERIALPORT: str = 'COM5'  # Port used to setup serial communication
BAUDRATE: int = 115200  # Baud rate used by the serial communication
ser = serial.Serial()


def initUART() -> None:

    # initialise UART communication

    ser.port = SERIALPORT
    ser.baudrate = BAUDRATE
    ser.bytesize = serial.EIGHTBITS  # number of bits per bytes
    ser.parity = serial.PARITY_NONE  # set parity check: no parity
    ser.stopbits = serial.STOPBITS_ONE  # number of stop bits
    ser.timeout = None  # block read

    ser.xonxoff = False  # disable software flow control
    ser.rtscts = False  # disable hardware (RTS/CTS) flow control
    ser.dsrdtr = False  # disable hardware (DSR/DTR) flow control
    loggers["uart_logger"].info('Starting Up Serial Monitor')

    try:
        ser.open()
    except serial.SerialException:
        loggers["uart_logger"].error(f'Serial {SERIALPORT} port not available"')
        exit(-2)


def sendUARTMessage(msg) -> None:
    ser.write(msg)  # Write msg in the serial communication
    loggers["uart_logger"].info("Message <" + msg.decode('utf-8') + "> sent to micro-controller.")


# Main program logic follows:
if __name__ == '__main__':
    initUART()
    f = open(FILENAME, "ab")  # Open the file in Append Binary mods
    loggers["glob_logger"].info(f'{FILENAME} open successfully')
    print('Press Ctrl-C to quit.')

    # Initialise the UDP server

    server = ThreadedUDPServer((HOST, UDP_PORT), ThreadedUDPRequestHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True

    try:

        server_thread.start()  # Start the UDP server
        loggers["udp_logger"].info(f"Server started at {HOST} port {UDP_PORT}")

        while ser.isOpen():  # Open serial communication

                data_str = ser.read(20)  # Read 20 bytes
                f.write(data_str)  # Write data int the files
                loggers["uart_logger"].info(str(data_str) + ' received')
                data = str(data_str).split('\\n')[0].split("b'")[1]  # Get the data from the uart
                if str(APPID) in data:  # If APP ID is present at the start of the message
                    data_send = {}
                    if "Temp" in data:  # If the Data type is Temp
                        # Format the dictionary to math tha API requirement
                        data_send = {"value": float(data.split(':')[-1])}
                        payload = json.dumps(data_send)  # Convert to JSON
                        # Send the data to the API
                        response = requests.request("POST", f'http://{API_URL}/temp/', headers=headers, data=payload)
                    if "Lux" in data:  # If the Data type is Lumi
                        # Format the dictionary to math tha API requirement
                        data_send = {"value": float(data.split(':')[-1])}
                        # Convert to JSON
                        payload = json.dumps(data_send)
                        # Send the data to the API
                        response = requests.request("POST", f'http://{API_URL}/lumi/', headers=headers, data=payload)
    except (KeyboardInterrupt, SystemExit):
        # If there is an exception or a key interruption
        # Shutdown the server and close the files
        server.shutdown()
        server.server_close()
        f.close()
        ser.close()
        loggers["uart_logger"].error("UART not started")
