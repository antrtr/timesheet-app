import tkinter as tk
from database import init_db
from gui import TimesheetApp

if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = TimesheetApp(root)
    root.mainloop()
