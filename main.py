from controller.controller import OptimizationController
import tkinter as tk
from tkinter import messagebox

def main():
    try:
        app = OptimizationController()
        app.run()
    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Erro Fatal", f"Não foi possível iniciar a aplicação:\n{e}")

if __name__ == "__main__":
    main()
