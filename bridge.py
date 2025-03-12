import server
import client
import Alex
from utils import DataType


class Bridge:
    def __init__(self, isServer=True, progressCallback=None, getServerCallback=None):
        self.progressCallback = progressCallback
        self.getServerCallback = getServerCallback
        if isServer:
            self.localServer = server.Server()
            self.localServer.start()
        else:
            self.localClient = client.Client()
            login, server_ip, port = self.getServerCallback()
            self.localClient.connect_to_server(login, server_ip, port)

    def startCalculation(self):
        clientsLen = len(self.localServer.CLIENTS)
        angles = 90
        anglesPerClient = angles // clientsLen
        for conn, login in self.localServer.CLIENTS:
            self.localServer.send(conn, DataType.COMMAND, f"start {min(anglesPerClient, angles)}")
            angles -= anglesPerClient

    def updateProgressbar(self):
        self.progressCallback()
