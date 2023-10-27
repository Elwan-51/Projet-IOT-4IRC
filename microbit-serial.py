# Program to control passerelle between Android application
# and micro-controller through USB tty
import socketserver
import serial
import threading
import requests
import json

with open('config.json', 'r') as conf_file:
    config = json.load(conf_file)

HOST = config['SERIAL']['HOST']
UDP_PORT = config['SERIAL']['PORT']
MICRO_COMMANDS = config['SERIAL']['MICRO_COMMANDS']
APPID = config['SERIAL']['APP_ID']
FILENAME = config['SERIAL']['FILENAME']
LAST_VALUE = ""
API_URL = f"{config['API']['URL']}:{config['API']['PORT']}"

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {config["API"]["TOKEN"]}'
}
class ThreadedUDPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        data = self.request[0].strip().decode('utf-8')
        socket = self.request[1]
        current_thread = threading.current_thread()
        print("{}: client: {}, wrote: {}".format(current_thread.name, self.client_address, data))
        if data != "":
            if data in MICRO_COMMANDS:  # Send message through UART
                sendUARTMessage(f'{APPID}:{data}'.encode())
                socket.sendto('{"message": "Success"}'.encode(), self.client_address)

            elif data == "getValues()":  # Sent last value received from micro-controller
                x = requests.get(f'http://{API_URL}/data/last/')
                print(x.content)
                socket.sendto(x.content, self.client_address)
                # TODO: Create last_values_received as global variable
            else:
                print("Unknown message: ", data)


class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass


# send serial message
SERIALPORT = 'COM5'
BAUDRATE = 115200
ser = serial.Serial()


def initUART():
    # ser = serial.Serial(SERIALPORT, BAUDRATE)
    ser.port = SERIALPORT
    ser.baudrate = BAUDRATE
    ser.bytesize = serial.EIGHTBITS  # number of bits per bytes
    ser.parity = serial.PARITY_NONE  # set parity check: no parity
    ser.stopbits = serial.STOPBITS_ONE  # number of stop bits
    ser.timeout = None  # block read

    # ser.timeout = 0             #non-block read
    # ser.timeout = 2              #timeout block read
    ser.xonxoff = False  # disable software flow control
    ser.rtscts = False  # disable hardware (RTS/CTS) flow control
    ser.dsrdtr = False  # disable hardware (DSR/DTR) flow control
    # ser.writeTimeout = 0     #timeout for write
    print('Starting Up Serial Monitor')
    try:
        ser.open()
    except serial.SerialException:
        print("Serial {} port not available".format(SERIALPORT))
        #exit()


def sendUARTMessage(msg):
    ser.write(msg)
    print("Message <" + msg.decode('utf-8') + "> sent to micro-controller.")


# Main program logic follows:
if __name__ == '__main__':
    initUART()
    f = open(FILENAME, "ab")
    print('Press Ctrl-C to quit.')

    server = ThreadedUDPServer((HOST, UDP_PORT), ThreadedUDPRequestHandler)

    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True

    try:
        server_thread.start()
        print("Server started at {} port {}".format(HOST, UDP_PORT))
        while ser.isOpen():
            # time.sleep(100)
                data_str = ser.read(20)
                f.write(data_str)
                LAST_VALUE = data_str
                data = str(data_str).split('\\n')[0].split("b'")[1]
                if str(APPID) in data:
                    data_send = {}
                    if "Temp" in data:
                        data_send = {"value": float(data.split(':')[-1])}
                        payload = json.dumps(data_send)
                        response = requests.request("POST", f'http://{API_URL}/temp/', headers=headers, data=payload)
                    if "Lux" in data:
                        data_send = {"value": float(data.split(':')[-1])}
                        payload = json.dumps(data_send)
                        response = requests.request("POST", f'http://{API_URL}/lumi/', headers=headers, data=payload)


    except (KeyboardInterrupt, SystemExit):
        server.shutdown()
        server.server_close()
        f.close()
        ser.close()
        print("UART not started")
