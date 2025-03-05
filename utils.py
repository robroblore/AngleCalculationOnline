from enum import IntEnum

# FORMAT = The format (encryption) of the message to be received
DEFAULT_FORMAT = "utf-8"

# HEADERLEN = Information about the message to be received (in this case,
# the length of the message)
DEFAULT_HEADERLEN = 64
DEFAULT_PORT = 6969  # Default port number for the server


class DataType(IntEnum):
    DEBUG = 0
    COMMAND = 1
    DISCONNECT = 2


def receive_data(socket, data_len):
    data = b""
    while len(data) < data_len:
        packet = socket.recv(data_len - len(data))
        if not packet:
            return None
        data += packet
    return data


def send_data(socket, data, data_len):
    if len(data) < data_len:
        data += b' ' * (data_len - len(data))
    elif len(data) > data_len:
        data = data[:data_len]

    data_sent = 0
    while data_sent < data_len:
        data_sent += socket.send(data[data_sent:])
