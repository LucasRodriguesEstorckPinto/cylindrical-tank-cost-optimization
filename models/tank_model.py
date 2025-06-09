import numpy as np

class TankModel:
    def __init__(self):
        # Constantes do problema
        self.V0 = 0.8               # m³
        self.t = 0.03               # m (3 cm)
        self.rho = 8000            # kg/m³
        self.L_max = 2.0           # m
        self.D_max = 1.0           # m
        self.cm = 4.5              # $/kg
        self.cw = 20               # $/m

    def massa(self, D, L):
        r = D / 2
        t = self.t
        parte_cilindro = L * np.pi * ((r + t)**2 - r**2)
        parte_placas = 2 * np.pi * (r + t)**2 * t
        return self.rho * (parte_cilindro + parte_placas)

    def solda(self, D):
        return 4 * np.pi * (D + self.t)

    def custo(self, D, L):
        m = self.massa(D, L)
        lw = self.solda(D)
        return self.cm * m + self.cw * lw

    def volume_util(self, D, L):
        return (np.pi * D**2 / 4) * L

    def respeita_restricoes(self, D, L):
        V = self.volume_util(D, L)
        return (0.9 * self.V0 <= V <= 1.1 * self.V0) and (D <= self.D_max) and (L <= self.L_max)
