from views.app_view import TankOptimizerApp
import customtkinter as ctk

if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    app = TankOptimizerApp()
    app.mainloop()