import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox
import math
import time

class TankOptimizationModel:
    def __init__(self):
        self.V0 = 0.8      # m³
        self.t = 0.03      # m (3 cm)
        self.rho = 8000    # kg/m³
        self.Lmax = 2.0    # m
        self.Dmax = 1.0    # m
        self.cm = 4.5      # $/kg
        self.cw = 20       # $/m
        
    def calculate_mass(self, D, L):
        V_cylinder = L * math.pi * (( (D/2 + self.t)**2 - (D/2)**2 ))
        V_plate = 2 * math.pi * ( (D/2 + self.t)**2 ) * self.t
        return self.rho * (V_cylinder + V_plate)
    
    def calculate_weld_length(self, D):
        return 4 * math.pi * (D + self.t)
    
    def objective_function(self, x):
        D, L = x
        mass = self.calculate_mass(D, L)
        weld_length = self.calculate_weld_length(D)
        return self.cm * mass + self.cw * weld_length
    
    def constraints(self, x):
        D, L = x
        volume = (math.pi * D**2 * L) / 4.0
        return [
            volume - 0.9*self.V0,   # >=0
            1.1*self.V0 - volume,   # >=0
            self.Lmax - L,           # >=0
            self.Dmax - D            # >=0
        ]
    
    def augmented_objective(self, x, mu=1e6):
        f = self.objective_function(x)
        g = self.constraints(x)
        penalty = sum(min(0, gi)**2 for gi in g)
        return f + mu * penalty
    
    def gradient(self, f, x, h=1e-5):
        n = len(x)
        grad = np.zeros(n)
        for i in range(n):
            x_plus = x.copy()
            x_plus[i] += h
            x_minus = x.copy()
            x_minus[i] -= h
            grad[i] = (f(x_plus) - f(x_minus)) / (2*h)
        return grad
    
    def hessian(self, f, x, h=1e-5):
        n = len(x)
        hess = np.zeros((n, n))
        fx = f(x)
        
        # Diagonal principal
        for i in range(n):
            x_pp = x.copy()
            x_pp[i] += h
            x_pm = x.copy()
            x_pm[i] -= h
            hess[i,i] = (f(x_pp) - 2*fx + f(x_pm)) / (h**2)
        
        # Elementos fora da diagonal
        for i in range(n):
            for j in range(i+1,n):
                x_pp = x.copy()
                x_pp[i] += h
                x_pp[j] += h
                
                x_pm = x.copy()
                x_pm[i] += h
                x_pm[j] -= h
                
                x_mp = x.copy()
                x_mp[i] -= h
                x_mp[j] += h
                
                hess[i,j] = (f(x_pp) - f(x_pm) - f(x_mp) + fx) / (4*h*h)
                hess[j,i] = hess[i,j]
        
        return hess
    
    def steepest_descent(self, f, x0, tol=1e-6, max_iter=100, h=1e-5, alpha0=1.0, beta=0.5, c=1e-4):
        x = np.array(x0, dtype=float)
        history = [x.copy()]
        grad_norms = []
        iterations = 0
        evaluations = 0
        
        while iterations < max_iter:
            grad = self.gradient(f, x, h)
            grad_norm = np.linalg.norm(grad)
            grad_norms.append(grad_norm)
            evaluations += 2*len(x)
            
            if grad_norm < tol:
                break
                
            d = -grad
            alpha = alpha0
            fx = f(x)
            evaluations += 1
            
            while f(x + alpha*d) > fx + c*alpha*np.dot(grad, d):
                alpha *= beta
                evaluations += 1
                if alpha < 1e-10:
                    break
            
            x = x + alpha*d
            history.append(x.copy())
            iterations += 1
        
        return x, f(x), iterations, evaluations, np.array(history), np.array(grad_norms)
    
    def newton_method(self, f, x0, tol=1e-6, max_iter=100, h=1e-5, alpha0=1.0, beta=0.5, c=1e-4):
        x = np.array(x0, dtype=float)
        history = [x.copy()]
        grad_norms = []
        iterations = 0
        evaluations = 0
        
        while iterations < max_iter:
            grad = self.gradient(f, x, h)
            grad_norm = np.linalg.norm(grad)
            grad_norms.append(grad_norm)
            evaluations += 2*len(x)
            
            if grad_norm < tol:
                break
                
            try:
                H = self.hessian(f, x, h)
                evaluations += len(x)**2 * 4  # Avaliações para Hessiana
                d = np.linalg.solve(H, -grad)
            except np.linalg.LinAlgError:
                d = -grad
            
            alpha = alpha0
            fx = f(x)
            evaluations += 1
            
            while f(x + alpha*d) > fx + c*alpha*np.dot(grad, d):
                alpha *= beta
                evaluations += 1
                if alpha < 1e-10:
                    break
            
            x = x + alpha*d
            history.append(x.copy())
            iterations += 1
        
        return x, f(x), iterations, evaluations, np.array(history), np.array(grad_norms)
    
    def dfp_method(self, f, x0, tol=1e-6, max_iter=100, h=1e-5, alpha0=1.0, beta=0.5, c=1e-4):
        x = np.array(x0, dtype=float)
        n = len(x0)
        H = np.eye(n)
        history = [x.copy()]
        grad_norms = []
        iterations = 0
        evaluations = 0
        
        grad = self.gradient(f, x, h)
        evaluations += 2*n
        
        while iterations < max_iter:
            grad_norm = np.linalg.norm(grad)
            grad_norms.append(grad_norm)
            
            if grad_norm < tol:
                break
                
            d = -H.dot(grad)
            alpha = alpha0
            fx = f(x)
            evaluations += 1
            
            while f(x + alpha*d) > fx + c*alpha*np.dot(grad, d):
                alpha *= beta
                evaluations += 1
                if alpha < 1e-10:
                    break
            
            x_new = x + alpha*d
            s = x_new - x
            g_new = self.gradient(f, x_new, h)
            y = g_new - grad
            evaluations += 2*n
            
            if np.dot(s, y) > 1e-10:
                rho = 1.0 / np.dot(s, y)
                Hy = H.dot(y)
                H = H - np.outer(Hy, Hy) / np.dot(y, Hy) + np.outer(s, s) / np.dot(s, y)
            
            x = x_new
            grad = g_new
            history.append(x.copy())
            iterations += 1
        
        return x, f(x), iterations, evaluations, np.array(history), np.array(grad_norms)

class OptimizationView(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Otimização de Tanque Cilíndrico")
        self.geometry("1200x800")
        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame de controle
        control_frame = ttk.LabelFrame(main_frame, text="Parâmetros de Controle", width=300)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Método de otimização
        ttk.Label(control_frame, text="Método:").pack(anchor='w', pady=(5,0))
        self.method_var = tk.StringVar(value="Steepest Descent")
        methods = ["Steepest Descent", "Newton", "DFP"]
        method_menu = ttk.Combobox(control_frame, textvariable=self.method_var, values=methods, state='readonly')
        method_menu.pack(fill=tk.X, padx=5, pady=(0,10))
        
        # Parâmetros
        params_frame = ttk.LabelFrame(control_frame, text="Parâmetros")
        params_frame.pack(fill=tk.X, padx=5, pady=5)
        
        params = [
            ("D inicial (m):", "D0_var", 0.5),
            ("L inicial (m):", "L0_var", 1.0),
            ("Alpha:", "alpha_var", 1.0),
            ("Tolerância:", "tol_var", 1e-6)
        ]
        
        for text, name, default in params:
            frame = ttk.Frame(params_frame)
            frame.pack(fill=tk.X, padx=5, pady=2)
            ttk.Label(frame, text=text, width=12).pack(side=tk.LEFT)
            var = tk.DoubleVar(value=default)
            setattr(self, name, var)
            ttk.Entry(frame, textvariable=var).pack(side=tk.RIGHT, expand=True, fill=tk.X)
        
        # Botão de execução
        ttk.Button(control_frame, text="Executar Otimização", command=self.run_optimization).pack(pady=10)
        
        # Frame de resultados
        result_frame = ttk.LabelFrame(main_frame, text="Resultados", width=300)
        result_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        
        # Resultados numéricos
        results = [
            ("Iterações:", "iter_var"),
            ("Avaliações:", "eval_var"),
            ("Solução D (m):", "sol_D_var"),
            ("Solução L (m):", "sol_L_var"),
            ("Custo ($):", "cost_var"),
            ("Tempo (s):", "time_var")
        ]
        
        for text, name in results:
            frame = ttk.Frame(result_frame)
            frame.pack(fill=tk.X, padx=5, pady=2)
            ttk.Label(frame, text=text, width=14).pack(side=tk.LEFT)
            var = tk.StringVar(value="")
            setattr(self, name, var)
            ttk.Label(frame, textvariable=var, relief='sunken', width=15).pack(side=tk.RIGHT)
        
        # Gráficos
        graph_frame = ttk.Frame(main_frame)
        graph_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.fig = plt.Figure(figsize=(10, 8))
        self.ax1 = self.fig.add_subplot(211)
        self.ax2 = self.fig.add_subplot(212)
        self.canvas = FigureCanvasTkAgg(self.fig, graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def run_optimization(self):
        try:
            # Limpar resultados anteriores
            for var in ["iter_var", "eval_var", "sol_D_var", "sol_L_var", "cost_var", "time_var"]:
                getattr(self, var).set("Calculando...")
            
            self.update()
            
            # Executar otimização
            self.controller.run_optimization()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro na otimização:\n{str(e)}")
        
    def on_close(self):
        plt.close('all')
        self.destroy()
        
    def update_results(self, result):
        if result is None:
            return
            
        x_opt, f_opt, iters, evals, time_elapsed = result
        
        # Atualizar interface
        self.iter_var.set(str(iters))
        self.eval_var.set(str(evals))
        self.sol_D_var.set(f"{x_opt[0]:.6f}")
        self.sol_L_var.set(f"{x_opt[1]:.6f}")
        self.cost_var.set(f"{f_opt:.2f}")
        self.time_var.set(f"{time_elapsed:.4f}")
        
        # Forçar atualização da interface
        self.update()
        
    def plot_results(self, history, grad_norms):
        # Limpar gráficos
        self.ax1.clear()
        self.ax2.clear()
        
        # Curvas de nível
        D = np.linspace(0.1, 1.0, 50)
        L = np.linspace(0.1, 2.0, 50)
        D, L = np.meshgrid(D, L)
        Z = np.zeros_like(D)
        
        for i in range(D.shape[0]):
            for j in range(D.shape[1]):
                Z[i,j] = self.controller.model.augmented_objective([D[i,j], L[i,j]])
        
        CS = self.ax1.contour(D, L, Z, 20, cmap='viridis')
        self.ax1.clabel(CS, inline=True, fontsize=10)
        self.ax1.plot(history[:,0], history[:,1], 'ro-', markersize=4, linewidth=1)
        self.ax1.set_xlabel('Diâmetro (m)')
        self.ax1.set_ylabel('Comprimento (m)')
        self.ax1.set_title('Trajetória de Otimização')
        self.ax1.grid(True)
        
        # Convergência
        if len(grad_norms) > 0:
            self.ax2.semilogy(range(len(grad_norms)), grad_norms, 'b-o')
            self.ax2.set_xlabel('Iteração')
            self.ax2.set_ylabel('Norma do Gradiente')
            self.ax2.set_title('Convergência do Método')
            self.ax2.grid(True)
        
        self.fig.tight_layout()
        self.canvas.draw()

class OptimizationController:
    def __init__(self, root):
        self.model = TankOptimizationModel()
        self.view = OptimizationView(self)
        self.root = root
        
    def run_optimization(self):
        try:
            method = self.view.method_var.get()
            D0 = self.view.D0_var.get()
            L0 = self.view.L0_var.get()
            alpha = self.view.alpha_var.get()
            tol = self.view.tol_var.get()
            
            def f(x):
                return self.model.augmented_objective(x)
            
            start_time = time.time()
            
            if method == "Steepest Descent":
                result = self.model.steepest_descent(f, [D0, L0], tol, 100, 1e-5, alpha, 0.5, 1e-4)
            elif method == "Newton":
                result = self.model.newton_method(f, [D0, L0], tol, 100, 1e-5, alpha, 0.5, 1e-4)
            elif method == "DFP":
                result = self.model.dfp_method(f, [D0, L0], tol, 100, 1e-5, alpha, 0.5, 1e-4)
            else:
                raise ValueError("Método desconhecido")
            
            x_opt, f_opt, iters, evals, history, grad_norms = result
            time_elapsed = time.time() - start_time
            
            self.view.update_results((x_opt, f_opt, iters, evals, time_elapsed))
            self.view.plot_results(history, grad_norms)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro na otimização:\n{str(e)}")
            self.view.update_results(None)

if __name__ == "__main__":
    root = tk.Tk()
    app = OptimizationController(root)
    root.mainloop()