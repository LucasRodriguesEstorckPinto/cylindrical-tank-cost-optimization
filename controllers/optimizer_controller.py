from models.tank_model import TankModel
from methods.steepest_descent import steepest_descent
from methods.newton import newton_method
from methods.dfp import dfp_method

class OptimizerController:
    def __init__(self):
        self.model = TankModel()

    def run(self, method_name, x0, options):
        if method_name == "Steepest Descent":
            return steepest_descent(self.model, x0, options)
        elif method_name == "Newton":
            return newton_method(self.model, x0, options)
        elif method_name == "DFP":
            return dfp_method(self.model, x0, options)
        else:
            raise ValueError("Método desconhecido")
