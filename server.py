import socket
import selectors
import types
import utils
from utils import receive_data, send_data, DataType


class Server:
    def __init__(self):
        self.FORMAT = utils.DEFAULT_FORMAT
        self.HEADERLEN = utils.DEFAULT_HEADERLEN
        self.PORT = utils.DEFAULT_PORT

        self.SERVER_IP = socket.gethostbyname(socket.gethostname())

        self.CLIENTS = dict()
        self.selector = selectors.DefaultSelector()

    def handle_client(self, key: selectors.SelectorKey, mask: int):
        conn: socket.socket = key.fileobj

        if mask & selectors.EVENT_READ:
            data_type = int(receive_data(conn, 1).decode(self.FORMAT))

            match data_type:
                case DataType.DISCONNECT:
                    self.close_client(conn)

                case DataType.DEBUG:
                    # Debug message
                    data_length = int(receive_data(conn, self.HEADERLEN).decode(self.FORMAT))
                    if data_length:
                        debug_message = receive_data(conn, data_length).decode(self.FORMAT)
                        print(f"[DEBUG] {debug_message}")

                case DataType.COMMAND:
                    # Command
                    data_length = int(receive_data(conn, self.HEADERLEN).decode(self.FORMAT))
                    if data_length:
                        command = receive_data(conn, data_length).decode(self.FORMAT)
                        print(f"[COMMAND] {command}")

    def start(self):
        """
        Starts the server and listens for incoming connections.
        """

        print(f"Starting server on {self.SERVER_IP}:{self.PORT}")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener_socket:
            listener_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener_socket.bind((self.SERVER_IP, self.PORT))
            listener_socket.listen()
            print(f"Listening on {self.SERVER_IP}:{self.PORT}")
            self.selector.register(listener_socket, selectors.EVENT_READ)

            while True:
                events = self.selector.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        self.accept_connection(key.fileobj)
                    else:
                        try:
                            self.handle_client(key, mask)
                        except ConnectionResetError:
                            self.close_client(key.fileobj)

    def accept_connection(self, listener_socket: socket.socket) -> None:
        """
        Accepts a new connection from a client.
        """

        conn, addr = listener_socket.accept()
        data = types.SimpleNamespace(addr=addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.selector.register(conn, events, data=data)

        # Get client name
        login = receive_data(conn, 64).decode(self.FORMAT).strip(' ')
        if login in self.CLIENTS.values():
            print(f"{login} is already connected to the server")
            send_data(conn, b'0', 1)
            conn.close()
            return
        send_data(conn, b'1', 1)
        self.CLIENTS[conn] = login
        print(f"{login} has connected to the server from {conn.getpeername()}")

    def close_client(self, sock: socket.socket) -> None:
        """
        Closes and unregisters a client socket.
        """

        self.selector.unregister(sock)
        sock.close()
        for conn, login in list(self.CLIENTS.items()):
            if conn == sock:
                print(f"{login} has disconnected from the server")
                del self.CLIENTS[login]
