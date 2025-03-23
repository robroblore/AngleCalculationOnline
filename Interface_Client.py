import random
import tkinter as tk
from tkinter import ttk
import bridge as br
class Window(tk.Tk):
    def __init__(self):
        super().__init__()
        self.padx = 20
        self.pady = 10
        self.title('Slave')
        self.state = tk.StringVar()
        self.state.set('Not Connected')

        self.bridge = br.Bridge(isServer=False, progressCallback=self.updateProgressbar)

        self.ipadresslabel = tk.Label(self, text='IP Adress', width=10, borderwidth=0, relief="solid")
        self.ipadresslabel.grid(row=0, column=0, sticky="news", padx=self.padx, pady=self.pady)
        self.ipadress = tk.Entry(self)
        self.ipadress.insert(0, self.bridge.getIP())
        self.ipadress.grid(row=1, column=0, sticky="news", padx=self.padx, pady=self.pady)

        self.portlabel = tk.Label(self, text='Port', width=10, borderwidth=0, relief="solid")
        self.portlabel.grid(row=0, column=1, sticky="news", padx=self.padx, pady=self.pady)
        self.port = tk.Entry(self)
        self.port.grid(row=1, column=1, sticky="news", padx=self.padx, pady=self.pady)
        self.port.insert(0, self.bridge.getPORT())

        self.progressvar = tk.DoubleVar()
        self.progressbar = ttk.Progressbar(self, variable=self.progressvar, maximum=1)
        self.progressbar.grid(row=2, column=0, columnspan=2, sticky="news", padx=self.padx, pady=self.pady)

        self.connect = tk.Button(self, text='Connect', bg='lawn green', command=self.Connecting)
        self.connect.grid(row=3, column=0, columnspan=2, sticky="news", padx=self.padx, pady=self.pady)

        self.statelabel = tk.Label(self, textvariable=self.state, width=10, borderwidth=0, relief="solid", fg='red')
        self.statelabel.grid(row=4, column=0, columnspan=2, sticky="news", padx=self.padx, pady=self.pady)

    def updateProgressbar(self, var):
        self.progressvar.set(var)

    def Connecting(self):
        self.ip = self.ipadress.get()
        self.po = self.port.get()
        self.bridge.connect_client(str(random.randint(1000000, 9999999)), self.ip, int(self.po))
        print(f'Connected at {self.ip} and port {self.po}')