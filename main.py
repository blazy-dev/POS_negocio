import tkinter as tk
from db import database as db
from ui.app import POSApp

if __name__ == "__main__":
    root = tk.Tk()
    app = POSApp(root, db)
    root.mainloop()
