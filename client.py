import socket
import utils
from utils import receive_data, send_data, DataType
import threading


# Inherit from QObject to be able to use signals
class Client:
    def __init__(self):
        super().__init__()
        self.FORMAT = utils.DEFAULT_FORMAT
        self.HEADERLEN = utils.DEFAULT_HEADERLEN
        self.PORT = utils.DEFAULT_PORT

        self.SERVER = None
        self.LOGIN = None

        self.IP = socket.gethostbyname(socket.gethostname())

        self.isConnected = False

        # Create a socket object (AF_INET = IPv4, SOCK_STREAM = TCP)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.calculationCallback = None

        self.listener = None

    def connect_to_server(self, login, server_ip, port):
        self.SERVER = server_ip
        self.LOGIN = login
        self.PORT = port

        try:
            # Connect to the server
            self.client.connect((self.SERVER, self.PORT))
            print(f"Connected to {self.SERVER} on port {self.PORT}")
            self.isConnected = True
        except Exception as err:
            print("Connection failed")
            print(f"Unexpected {err=}, {type(err)=}")
            return False

        send_data(self.client, self.LOGIN.encode(self.FORMAT), 64)
        result = receive_data(self.client, 1)

        if not result:
            print("Connection closed")
            self.isConnected = False
            self.client.close()
            return False

        # Listen for messages from the server and be able to send messages to the server at the same time using
        # threading
        self.listener = threading.Thread(target=self.listen, daemon=True)
        self.listener.start()
        return True

    def send(self, data_type: int, data: str = ""):
        """
        Sent data to the server
        """

        if not self.isConnected:
            print("Not connected to the server")
            return

        send_data(self.client, str(data_type).encode(self.FORMAT), len(str(data_type)))

        match data_type:
            case DataType.DEBUG:
                # Debug message
                data = data.encode(self.FORMAT)
                data_size = str(len(data)).encode(self.FORMAT)

                send_data(self.client, data_size, self.HEADERLEN)
                send_data(self.client, data, len(data))

            case DataType.COMMAND:
                # Command
                data = data.encode(self.FORMAT)
                data_size = str(len(data)).encode(self.FORMAT)

                send_data(self.client, data_size, self.HEADERLEN)
                send_data(self.client, data, len(data))

            case DataType.DISCONNECT:
                # Disconnect
                self.isConnected = False
                self.client.close()

            case _:
                # Invalid data type
                print("Invalid data type")
                return

    def receive(self):
        """
        Receive data from the server
        """

        data_received = receive_data(self.client, 1)
        if not data_received:
            print("Connection closed")
            self.isConnected = False
            self.client.close()
            return
        data_type = int(data_received.decode(self.FORMAT))

        match data_type:
            case DataType.DEBUG:
                # Debug message
                data_length = int(receive_data(self.client, self.HEADERLEN).decode(self.FORMAT))
                if data_length:
                    debug_message = receive_data(self.client, data_length).decode(self.FORMAT)
                    print(f"[DEBUG] {debug_message}")

            case DataType.COMMAND:
                # Command
                data_length = int(receive_data(self.client, self.HEADERLEN).decode(self.FORMAT))
                if data_length:
                    command = receive_data(self.client, data_length).decode(self.FORMAT)
                    print(f"[COMMAND] {command}")

                    command = command.split()
                    if command[0] == "start":
                        calculation_id = command[1]
                        shape = command[2]
                        terrain = command[3]
                        D = float(command[4])
                        rA = float(command[5])
                        M = float(command[6])
                        vi = float(command[7])
                        theta = float(command[8])
                        ymin = float(command[9])
                        latitude = float(command[10])
                        vwind = float(command[11])
                        wa = float(command[12])
                        dt = float(command[13])
                        dtheta = float(command[14])
                        theta_min = float(command[15])
                        theta_max = float(command[16])
                        if self.calculationCallback:
                            self.calculationCallback(calculation_id, shape, terrain, D, rA, M, vi, theta, ymin, latitude, vwind, wa, dt, dtheta, theta_min, theta_max)

            case DataType.DISCONNECT:
                # Disconnect
                self.isConnected = False
                self.client.close()
                quit()

            case _:
                # Invalid data type
                print("Invalid data type")
                return

    def listen(self):
        """
        Continuously listen for messages from the server
        """
        while self.isConnected:
            self.receive()
