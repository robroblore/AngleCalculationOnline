import tkinter as tk
import maths
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

class Window(tk.Tk):
    def __init__(self):
        super().__init__()
        self.fontsize = 15
        self.config(bg="gray18")
        self.title('Trajectory Calculator')
        self.padx = 10
        self.pady = 20
        for i in range(42):
            self.columnconfigure(i, weight=1)
        for i in range(10):
            self.rowconfigure(i, weight=1)

        self.calculate = tk.Button(self, text='Calculate', command=self.calcul, font=('Calibri', int(self.fontsize*1.2)), bg='lawn green')
        self.calculate.grid(row=2, column=0, columnspan=42, pady=(self.pady, 0), padx=self.padx, sticky='news')

        self.ClientsList = tk.Listbox(self, width=50, height=6, selectbackground="red", exportselection=False, font=('Calibri', int(self.fontsize*0.8)), bg='lawn green')
        self.ClientsList.bind('<<ListboxSelect>>', self.print_Client)
        self.ClientsList.config(bg='papayawhip', fg='black')
        self.ClientsList.focus_set()

        self.ClientsListScrollbar = tk.Scrollbar(self, command=self.ClientsList.yview, width=5)
        self.ClientsList.grid(row=3, column=0, columnspan=20, pady=self.pady, sticky="news")
        self.ClientsList.config(yscrollcommand=self.ClientsListScrollbar.set)
        self.ClientsList.selection_set(0)
        self.ClientsListScrollbar.grid(row=3, column=20, pady=self.pady, padx=self.padx, sticky="news")

        for _ in range(10):
            self.add_Client()

        self.option_add("*TCombobox*Listbox.Font", ('Calibri', 13))

        self.shapelabel = tk.Label(self, text='Shape', borderwidth=0, relief="solid", font=('Calibri', self.fontsize), bg='ivory2')
        self.shapelabel.grid(row=4, column=0, columnspan=10, sticky="news", padx=self.padx)
        self.shape = ttk.Combobox(self, font=('Calibri', int(self.fontsize*0.8)))
        self.shape.grid(row=5, column=0, columnspan=10, sticky="news", padx=self.padx)
        self.shape['values'] = ['blunt', 'conic']
        self.shape.set('blunt')

        self.terrainlabel = tk.Label(self, text='Terrain', borderwidth=0, relief="solid", font=('Calibri', self.fontsize), bg='ivory2')
        self.terrainlabel.grid(row=4, column=10, columnspan=10, sticky="news", padx=self.padx)
        self.terrain = ttk.Combobox(self, font=('Calibri', int(self.fontsize*0.8)))
        self.terrain.grid(row=5, column=10, columnspan=10, sticky="news", padx=self.padx)
        self.terrain['values'] = ['rough', 'flat']
        self.terrain.set('rough')

        self.diameterlabel = tk.Label(self, text='Diameter [m]', borderwidth=0, relief="solid", font=('Calibri', self.fontsize), bg='ivory2')
        self.diameterlabel.grid(row=4, column=21, columnspan=10, sticky="news", padx=self.padx)
        self.diameter= ttk.Combobox(self, font=('Calibri', int(self.fontsize*0.8)))
        self.diameter.grid(row=5, column=21, columnspan=10, sticky="news", padx=self.padx)
        self.diameter['values'] = []
        diametervalues = []
        for diameter in range(1, 100):
            diametervalues.append(diameter/10)
        self.diameter['values'] = diametervalues
        self.diameter.set(0.1)

        self.rAlabel = tk.Label(self, text='Reference Area [m²]', borderwidth=0, relief="solid", font=('Calibri', self.fontsize), bg='ivory2')
        self.rAlabel.grid(row=4, column=31, columnspan=10, sticky="news", padx=self.padx)
        self.rA = ttk.Combobox(self, font=('Calibri', int(self.fontsize*0.8)))
        self.rA.grid(row=5, column=31, columnspan=10, sticky="news", padx=self.padx)
        self.rA['values'] = []
        rAvalues = []
        for rA in range(1, 100):
            rAvalues.append(rA / 100)
        self.rA['values'] = rAvalues
        self.rA.set(0.0134)

        self.masslabel = tk.Label(self, text='Mass [kg]', borderwidth=0, relief="solid", font=('Calibri', self.fontsize), bg='ivory2')
        self.masslabel.grid(row=6, column=0, columnspan=10, pady=(self.pady, 0), sticky="news", padx=self.padx)
        self.mass = ttk.Combobox(self, font=('Calibri', int(self.fontsize*0.8)))
        self.mass.grid(row=7, column=0, columnspan=10, sticky="news", padx=self.padx)
        self.mass['values'] = []
        massvalues = []
        for mass in range(1, 10):
            massvalues.append(mass)
            massvalues.append(mass*10)
            massvalues.append(mass*100)
            massvalues.append(mass*1000)
        massvalues.sort()
        self.mass['values'] = massvalues
        self.mass.set(30)

        self.initialspeedlabel = tk.Label(self, text='Initial Speed [m/s]', borderwidth=0, relief="solid", font=('Calibri', self.fontsize), bg='ivory2')
        self.initialspeedlabel.grid(row=6, column=10, columnspan=10, pady=(self.pady, 0), sticky="news", padx=self.padx)
        self.initialspeed = ttk.Combobox(self, font=('Calibri', int(self.fontsize*0.8)))
        self.initialspeed.grid(row=7, column=10, columnspan=10, sticky="news", padx=self.padx)
        self.initialspeed['values'] = []
        initialspeedvalues = []
        for initialspeed in range(10, 100, 10):
            initialspeedvalues.append(initialspeed)
            initialspeedvalues.append(initialspeed * 10)
            initialspeedvalues.append(initialspeed * 100)
            initialspeedvalues.append(initialspeed * 1000)
        initialspeedvalues.sort()
        self.initialspeed['values'] = initialspeedvalues
        self.initialspeed.set(930)

        self.thetalabel = tk.Label(self, text='Initial Angle [°] (0-90)', borderwidth=0, relief="solid", font=('Calibri', self.fontsize), bg='ivory2')
        self.thetalabel.grid(row=6, column=21, columnspan=10, pady=(self.pady, 0), sticky="news", padx=self.padx)
        self.theta = ttk.Combobox(self, font=('Calibri', int(self.fontsize*0.8)))
        self.theta.grid(row=7, column=21, columnspan=10, sticky="news", padx=self.padx)
        self.theta['values'] = []
        thetavalues = []
        for theta in range(91):
            thetavalues.append(theta)
        thetavalues.sort()
        self.theta['values'] = thetavalues
        self.theta.set(30)

        self.yminlabel = tk.Label(self, text='Initial Height [m]', borderwidth=0, relief="solid", font=('Calibri', self.fontsize), bg='ivory2')
        self.yminlabel.grid(row=6, column=31, columnspan=10, pady=(self.pady, 0), sticky="news", padx=self.padx)
        self.ymin = ttk.Combobox(self, font=('Calibri', int(self.fontsize*0.8)))
        self.ymin.grid(row=7, column=31, columnspan=10, sticky="news", padx=self.padx)
        self.ymin['values'] = []
        yminvalues = []
        for ymin in range(10):
            yminvalues.append(ymin * 1000)
        yminvalues.sort()
        self.ymin['values'] = yminvalues
        self.ymin.set(0)

        self.latitudelabel = tk.Label(self, text='Latitude [°] (0-90)', borderwidth=0, relief="solid", font=('Calibri', self.fontsize), bg='ivory2')
        self.latitudelabel.grid(row=8, column=0, columnspan=10, pady=(self.pady, 0), sticky="news", padx=self.padx)
        self.latitude = ttk.Combobox(self, font=('Calibri', int(self.fontsize*0.8)))
        self.latitude.grid(row=9, column=0, columnspan=10, sticky="news", padx=self.padx, pady=(0, self.pady))
        self.latitude['values'] = []
        latitudevalues = []
        for latitude in range(91):
            latitudevalues.append(latitude)
        latitudevalues.sort()
        self.latitude['values'] = latitudevalues
        self.latitude.set(0)

        self.wspeedlabel = tk.Label(self, text='Wind Speed [m/s]', borderwidth=0, relief="solid", font=('Calibri', self.fontsize), bg='ivory2')
        self.wspeedlabel.grid(row=8, column=10, columnspan=10, pady=(self.pady, 0), sticky="news", padx=self.padx)
        self.wspeed = ttk.Combobox(self, font=('Calibri', int(self.fontsize*0.8)))
        self.wspeed.grid(row=9, column=10, columnspan=10, sticky="news", padx=self.padx, pady=(0, self.pady))
        self.wspeed['values'] = []
        wspeedvalues = []
        for wspeed in range(10):
            wspeedvalues.append(wspeed * 100)
        wspeedvalues.sort()
        self.wspeed['values'] = wspeedvalues
        self.wspeed.set(0)

        self.walabel = tk.Label(self, text='Wind Angle [°] (0-360)', borderwidth=0, relief="solid", font=('Calibri', self.fontsize), bg='ivory2')
        self.walabel.grid(row=8, column=21, columnspan=10, pady=(self.pady, 0), sticky="news", padx=self.padx)
        self.wa = ttk.Combobox(self, font=('Calibri', int(self.fontsize*0.8)))
        self.wa.grid(row=9, column=21, columnspan=10, sticky="news", padx=self.padx, pady=(0, self.pady))
        self.wa['values'] = []
        wavalues = []
        for wa in range(36):
            wavalues.append(wa*10)
        wavalues.sort()
        self.wa['values'] = wavalues
        self.wa.set(0)

        self.Precisionlabel = tk.Label(self, text='Precision (≥ 1)', borderwidth=0, relief="solid", font=('Calibri', self.fontsize), bg='ivory2')
        self.Precisionlabel.grid(row=8, column=31, columnspan=10, pady=(self.pady, 0), sticky="news", padx=self.padx)
        self.Precision = ttk.Combobox(self, font=('Calibri', int(self.fontsize*0.8)))
        self.Precision['height'] = 19
        self.Precision.grid(row=9, column=31, columnspan=10, sticky="news", padx=self.padx, pady=(0, self.pady))
        self.Precision['values'] = []
        Precisionvalues = []
        for Precision in range(1, 10):
            Precisionvalues.append(Precision)
            Precisionvalues.append(Precision * 10)
            Precisionvalues.append(Precision * 100)
            Precisionvalues.append(Precision * 1000)
        Precisionvalues.sort()
        self.Precision['values'] = Precisionvalues
        self.Precision.set(10)

        self.progressvar = tk.DoubleVar()
        self.progressbar = ttk.Progressbar(self, variable=self.progressvar, maximum=1)
        self.progressbar.grid(row=10, column=0, columnspan=42, sticky="news", padx=self.padx)

        self.calcul()
        self.progressvar.set(0)

    def charger_graph(self):

        self.fig.set_size_inches(8, 4)
        canvas = FigureCanvasTkAgg(self.fig, master=self)
        canvas.get_tk_widget().grid(row=1, column=0, columnspan=42, sticky="news")

        toolbar_frame = tk.Frame(self)
        toolbar_frame.grid(row=0, column=0, columnspan=42, sticky="new")

        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
        toolbar.update()

        canvas.draw()

    def calcul(self):
        shape = self.shape.get()
        terrain = self.terrain.get()
        D = float(self.diameter.get())
        rA = float(self.rA.get())
        M = float(self.mass.get())
        vi = float(self.initialspeed.get())
        theta = float(self.theta.get())
        ymin = float(self.ymin.get())
        latitude = float(self.latitude.get())
        vwind = float(self.wspeed.get())
        wa = float(self.wa.get())
        dt = 1/float(self.Precision.get())
        dtheta = 1
        self.fig = maths.go(shape, terrain, D, rA, M, vi, theta, ymin, latitude, vwind, wa, dt, dtheta, self.progressvar, self)
        self.charger_graph()

    def add_Client(self):
        self.ClientsList.insert(tk.END, f'client{self.ClientsList.size()+1}')
        # print(self.ClientsList.get(tk.END, tk.END))
    def print_Client(self, client):
        print(f"Le client '{self.ClientsList.get(self.ClientsList.curselection()[0])}' a été sélectionné")

