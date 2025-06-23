import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

from view.tank_view import OptimizationGUI

class OptimizationController:
    def __init__(self):
        self.root = ctk.CTk()
        self.app = OptimizationGUI(self.root)

    def run(self):
        self.root.mainloop()
