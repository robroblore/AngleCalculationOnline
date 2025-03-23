from matplotlib import pyplot as plt

import server
import client
import Alex
import threading
from utils import DataType


class Bridge:
    def __init__(self, isServer=True, progressCallback=None):
        self.progressCallback = progressCallback

        self.isServer = isServer

        self.data_parts = 1
        self.data_parts_received = 0
        self.fig, self.axs = plt.subplots(2, 2)

        self.xc = []
        self.yc = []
        self.xa = []
        self.ya = []
        self.t = 0
        self.xmax_lst = []
        self.ymax_lst = []
        self.tmax_lst = []
        self.angl_lst = []
        self.theta = 0

        if self.isServer:
            self.localServer = server.Server()
            thread = threading.Thread(target=self.localServer.start)
            thread.start()
        else:
            self.localClient = client.Client()
            self.localClient.calculation_callback = self.start_client_calculation

    def server_received_data(self, calculation_id, xmax_lst, ymax_lst, tmax_lst, angl_lst):
        calculation_id = int(calculation_id)
        self.xmax_lst += xmax_lst
        self.ymax_lst += ymax_lst
        self.tmax_lst += tmax_lst
        self.angl_lst += angl_lst
        self.data_parts_received += 1
        self.updateProgressbar(self.data_parts_received / self.data_parts)
        if self.data_parts_received == self.data_parts:
            self.data_parts_received = 0
            Alex.show(self.xc, self.yc, self.xa, self.ya, self.t, self.xmax_lst, self.ymax_lst, self.tmax_lst,
                      self.angl_lst, self.theta, self.axs)
            self.xc = []
            self.yc = []
            self.xa = []
            self.ya = []
            self.t = 0
            self.xmax_lst = []
            self.ymax_lst = []
            self.tmax_lst = []
            self.angl_lst = []
            self.theta = 0

    def connect_client(self, login, server_ip, port):
        self.localClient.connect_to_server(login, server_ip, port)

    def start_client_calculation(self, calculation_id, shape, terrain, D, rA, M, vi, theta, ymin, latitude, vwind, wa,
                                 dt, dtheta,
                                 theta_min, theta_max):
        xc, yc, xa, ya, t, xmax_lst, ymax_lst, tmax_lst, angl_lst, theta = Alex.go(shape, terrain, D,
                                                                                   rA, M, vi, theta,
                                                                                   ymin, latitude,
                                                                                   vwind, wa, dt,
                                                                                   dtheta, theta_min,
                                                                                   theta_max)
        if not self.isServer:
            self.localClient.send(DataType.COMMAND,
                                  f"return {calculation_id}:::{xmax_lst}:::{ymax_lst}:::{tmax_lst}:::{angl_lst}")
        else:
            self.xc = xc
            self.yc = yc
            self.xa = xa
            self.ya = ya
            self.t = t
            self.xmax_lst = xmax_lst
            self.ymax_lst = ymax_lst
            self.tmax_lst = tmax_lst
            self.angl_lst = angl_lst
            self.theta = theta
            self.server_received_data(calculation_id, [], [], [], [])

    def start_server_calculation(self, shape, terrain, D, rA, M, vi, theta, ymin, latitude, vwind, wa, dt, dtheta):
        clientsLen = len(self.localServer.CLIENTS) + 1
        angles = 90
        anglesPerClient = angles // clientsLen
        i = 1

        for conn, login in list(self.localServer.CLIENTS.items()):
            theta_min = anglesPerClient * i
            theta_max = min(anglesPerClient * (i + 1), angles)
            self.localServer.send(conn, DataType.COMMAND,
                                  f"start {i} {shape} {terrain} {D} {rA} {M} {vi} {theta} {ymin} {latitude} {vwind} {wa} {dt} {dtheta} {theta_min} {theta_max}")
            i += 1
        self.data_parts = i

        self.start_client_calculation(0, shape, terrain, D, rA, M, vi, theta, ymin, latitude, vwind, wa, dt, dtheta,
                                      0, angles - (anglesPerClient * i))
        self.data_parts_received += 1

        return self.fig

    def getIP(self):
        if self.isServer:
            return self.localServer.SERVER_IP
        else:
            return self.localClient.IP

    def getPORT(self):
        if self.isServer:
            return self.localServer.PORT
        else:
            return self.localClient.PORT

    def updateProgressbar(self, progress):
        self.progressCallback(progress)
