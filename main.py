import Interface
import Interface_Client

if __name__ == "__main__":
    choice = input("Server(1) or Client(2)? ")
    if choice == "1":
        window = Interface.Window()
    else:
        window = Interface_Client.Window()
    window.mainloop()
