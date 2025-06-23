import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
from dataclasses import dataclass
from typing import List, Callable

# Configuração do CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

@dataclass
class Parameters:
    """Parâmetros fixos do problema, conforme Tabela 1 do PDF."""
    V0: float = 0.8      # Volume requerido (m³)
    t: float = 0.03      # Espessura (m), convertido de 3 cm
    rho: float = 8000    # Densidade (kg/m³)
    Lmax: float = 2.0    # Comprimento máximo (m)
    Dmax: float = 1.0    # Diâmetro máximo (m)
    cm: float = 4.5      # Custo do material ($/kg)
    cw: float = 20.0     # Custo da soldagem ($/m)

@dataclass
class OptimizationResult:
    """Estrutura para armazenar o resultado da otimização."""
    x_history: List[np.ndarray]
    f_history: List[float]
    gradient_norms: List[float]
    iterations: int
    function_evaluations: int
    final_x: np.ndarray
    final_f: float
    converged: bool
    method_name: str

class TankOptimizer:
    """Classe principal para a otimização do tanque."""
    
    def __init__(self, params: Parameters):
        self.params = params
        
    def objective_function(self, x: np.ndarray) -> float:
        """Função objetivo: custo total do tanque (Equação 1 do PDF)."""
        D, L = x[0], x[1]
        
        if D <= 0 or L <= 0:
            return float('inf')
            
        p = self.params
        
        # Massa do tanque (Equação 2 do PDF)
        # Volume do material da parede do cilindro
        v_cylinder_wall = L * np.pi * ((D / 2 + p.t)**2 - (D / 2)**2)
        # Volume do material das duas placas circulares nas extremidades
        v_plates = 2 * np.pi * (D / 2 + p.t)**2 * p.t
        m = p.rho * (v_cylinder_wall + v_plates)
        
        # Comprimento da solda (Equação 3 do PDF)
        # Solda interna e externa para as duas placas
        lw = 4 * np.pi * (D + p.t)
        
        # Custo total
        C = p.cm * m + p.cw * lw
        
        return C
    
    def constraints_penalty(self, x: np.ndarray, penalty_factor: float = 1e7) -> float:
        """Função de penalidade para as restrições."""
        D, L = x[0], x[1]
        penalty = 0.0
        
        # Volume interno (Equação 4 do PDF)
        V_internal = np.pi * D**2 * L / 4
        
        # Restrição de volume: 0.9*V0 <= V <= 1.1*V0 (Equação 5 do PDF)
        lower_vol_bound = 0.9 * self.params.V0
        upper_vol_bound = 1.1 * self.params.V0
        
        if V_internal < lower_vol_bound:
            penalty += penalty_factor * (lower_vol_bound - V_internal)**2
        if V_internal > upper_vol_bound:
            penalty += penalty_factor * (V_internal - upper_vol_bound)**2
            
        # Restrições de dimensão máxima
        if L > self.params.Lmax:
            penalty += penalty_factor * (L - self.params.Lmax)**2
        if D > self.params.Dmax:
            penalty += penalty_factor * (D - self.params.Dmax)**2
            
        # Restrições de positividade
        if D <= 0:
            penalty += penalty_factor * (-D + 1e-3)**2
        if L <= 0:
            penalty += penalty_factor * (-L + 1e-3)**2
            
        return penalty
    
    def penalized_objective(self, x: np.ndarray) -> float:
        """Função objetivo com penalização."""
        return self.objective_function(x) + self.constraints_penalty(x)
    
    def gradient_numerical(self, f: Callable, x: np.ndarray, h: float = 1e-6) -> np.ndarray:
        """Gradiente numérico usando diferenças finitas centrais."""
        grad = np.zeros_like(x)
        for i in range(len(x)):
            x_plus = x.copy()
            x_plus[i] += h
            x_minus = x.copy()
            x_minus[i] -= h
            grad[i] = (f(x_plus) - f(x_minus)) / (2 * h)
        return grad
    
    def hessian_numerical(self, f: Callable, x: np.ndarray, h: float = 1e-5) -> np.ndarray:
        """Hessiana numérica usando diferenças finitas."""
        n = len(x)
        hessian = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                x_pp, x_pm, x_mp, x_mm = x.copy(), x.copy(), x.copy(), x.copy()
                x_pp[i] += h; x_pp[j] += h
                x_pm[i] += h; x_pm[j] -= h
                x_mp[i] -= h; x_mp[j] += h
                x_mm[i] -= h; x_mm[j] -= h
                hessian[i, j] = (f(x_pp) - f(x_pm) - f(x_mp) + f(x_mm)) / (4 * h**2)
        return hessian
    
    def line_search_backtrack(self, f: Callable, x: np.ndarray, direction: np.ndarray, 
                              grad: np.ndarray, alpha_init: float = 1.0, c1: float = 1e-4, rho: float = 0.5) -> tuple[float, int]:
        """Busca linear com backtracking (condição de Armijo)."""
        alpha = alpha_init
        f_x = f(x)
        grad_dot_direction = np.dot(grad, direction)
        
        evals = 0
        for _ in range(50): # Limite de iterações para evitar loop infinito
            if f(x + alpha * direction) <= f_x + c1 * alpha * grad_dot_direction:
                return alpha, evals + 1
            alpha *= rho
            evals += 1
        return alpha, evals

    def steepest_descent(self, x0: np.ndarray, max_iter: int, tol: float, h_grad: float) -> OptimizationResult:
        """Método Steepest Descent."""
        x = x0.copy()
        x_history = [x.copy()]
        f_history = [self.penalized_objective(x)]
        gradient_norms = []
        func_evals = 1
        
        for i in range(max_iter):
            grad = self.gradient_numerical(self.penalized_objective, x, h_grad)
            func_evals += 2 * len(x)
            
            grad_norm = np.linalg.norm(grad)
            gradient_norms.append(grad_norm)
            
            if grad_norm < tol:
                return OptimizationResult(x_history, f_history, gradient_norms, i, func_evals, x, f_history[-1], True, "Steepest Descent")
                
            direction = -grad
            
            alpha, evals = self.line_search_backtrack(self.penalized_objective, x, direction, grad)
            func_evals += evals
            
            x = x + alpha * direction
            
            x_history.append(x.copy())
            f_history.append(self.penalized_objective(x))
            func_evals += 1
            
        return OptimizationResult(x_history, f_history, gradient_norms, max_iter, func_evals, x, f_history[-1], False, "Steepest Descent")

    def newton_method(self, x0: np.ndarray, max_iter: int, tol: float, h_grad: float) -> OptimizationResult:
        """Método de Newton com regularização."""
        x = x0.copy()
        x_history = [x.copy()]
        f_history = [self.penalized_objective(x)]
        gradient_norms = []
        func_evals = 1
        
        for i in range(max_iter):
            grad = self.gradient_numerical(self.penalized_objective, x, h_grad)
            hess = self.hessian_numerical(self.penalized_objective, x, h_grad)
            func_evals += 2 * len(x) + 4 * len(x)**2
            
            grad_norm = np.linalg.norm(grad)
            gradient_norms.append(grad_norm)
            
            if grad_norm < tol:
                return OptimizationResult(x_history, f_history, gradient_norms, i, func_evals, x, f_history[-1], True, "Newton")
            
            try:
                # Regularização de Levenberg-Marquardt para garantir que a Hessiana seja definida positiva
                reg = 1e-8
                while True:
                    try:
                        hess_reg = hess + reg * np.eye(len(x))
                        direction = np.linalg.solve(hess_reg, -grad)
                        if np.dot(direction, grad) < 0: # Verificar se é uma direção de descida
                            break
                    except np.linalg.LinAlgError:
                        pass
                    reg *= 10
                    if reg > 1e2: # Se a regularização ficar muito grande, use steepest descent
                        direction = -grad
                        break
            except Exception:
                direction = -grad
            
            alpha, evals = self.line_search_backtrack(self.penalized_objective, x, direction, grad)
            func_evals += evals
            
            x = x + alpha * direction
            x_history.append(x.copy())
            f_history.append(self.penalized_objective(x))
            func_evals += 1
            
        return OptimizationResult(x_history, f_history, gradient_norms, max_iter, func_evals, x, f_history[-1], False, "Newton")

    def dfp_method(self, x0: np.ndarray, max_iter: int, tol: float, h_grad: float) -> OptimizationResult:
        """Método Davidon-Fletcher-Powell (DFP)."""
        x = x0.copy()
        n = len(x)
        H = np.eye(n) # Aproximação da inversa da Hessiana
        
        x_history = [x.copy()]
        f_history = [self.penalized_objective(x)]
        gradient_norms = []
        func_evals = 1
        
        grad_old = self.gradient_numerical(self.penalized_objective, x, h_grad)
        func_evals += 2 * n
        
        for i in range(max_iter):
            grad_norm = np.linalg.norm(grad_old)
            gradient_norms.append(grad_norm)
            
            if grad_norm < tol:
                return OptimizationResult(x_history, f_history, gradient_norms, i, func_evals, x, f_history[-1], True, "DFP")
            
            direction = -H @ grad_old
            
            alpha, evals = self.line_search_backtrack(self.penalized_objective, x, direction, grad_old)
            func_evals += evals
            
            s = alpha * direction
            x_new = x + s
            
            grad_new = self.gradient_numerical(self.penalized_objective, x_new, h_grad)
            func_evals += 2 * n
            
            y = grad_new - grad_old
            
            # Atualização DFP da matriz H (com condição de curvatura)
            if np.dot(y, s) > 1e-12:
                Hy = H @ y
                term1 = np.outer(s, s) / np.dot(s, y)
                term2 = -np.outer(Hy, Hy) / np.dot(y, Hy)
                H = H + term1 + term2
            
            x = x_new
            grad_old = grad_new
            
            x_history.append(x.copy())
            f_history.append(self.penalized_objective(x))
            func_evals += 1
            
        return OptimizationResult(x_history, f_history, gradient_norms, max_iter, func_evals, x, f_history[-1], False, "DFP")


class OptimizationGUI:
    """Interface gráfica para a otimização do tanque."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Otimização de Tanque Cilíndrico - Métodos Numéricos")
        self.root.geometry("1400x900")
        
        self.params = Parameters()
        self.optimizer = TankOptimizer(self.params)
        self.results = {}
        
        self.dark_mode = tk.BooleanVar(value=True)
        
        self.setup_gui()
        
    def setup_gui(self):
        """Configura a interface gráfica usando .grid para responsividade."""
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        main_frame = ctk.CTkFrame(self.root)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        # --- Top Frame for Title and Theme Button ---
        top_frame = ctk.CTkFrame(main_frame)
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        top_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(top_frame, text="Otimização de Tanque Cilíndrico", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, pady=(5,10))
        
        self.theme_button = ctk.CTkButton(top_frame, text="🌙 Tema Escuro", command=self.toggle_theme, width=150)
        self.theme_button.grid(row=0, column=1, padx=10)

        # --- Content Frame using Grid ---
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        content_frame.grid_columnconfigure(0, weight=0)  # Left panel, fixed width
        content_frame.grid_columnconfigure(1, weight=1)  # Right panel, expandable
        content_frame.grid_rowconfigure(0, weight=1)
        
        left_panel = ctk.CTkFrame(content_frame, width=380)
        left_panel.grid(row=0, column=0, sticky="ns", padx=(0, 10), pady=10)
        
        right_panel = ctk.CTkFrame(content_frame)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)
        
        self.setup_left_panel(left_panel)
        self.setup_right_panel(right_panel)
        
    def setup_left_panel(self, parent):
        """Configura o painel esquerdo com parâmetros e controles."""
        parent.grid_rowconfigure(1, weight=5) # Settings
        parent.grid_rowconfigure(3, weight=4) # Results
        
        ctk.CTkLabel(parent, text="Configurações", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, pady=(10, 5), padx=10, sticky="ew")
        
        scrollable_frame = ctk.CTkScrollableFrame(parent, label_text="Parâmetros e Controles")
        scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        self.setup_problem_parameters(scrollable_frame)
        self.setup_method_parameters(scrollable_frame)
        
        self.setup_control_buttons(parent)
        self.setup_results_area(parent)
        
    def setup_problem_parameters(self, parent):
        """Exibe os parâmetros fixos do problema."""
        problem_frame = ctk.CTkFrame(parent)
        problem_frame.pack(fill="x", pady=(0, 15), padx=5)
        
        ctk.CTkLabel(problem_frame, text="Parâmetros do Problema (Fixos)", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        
        param_configs = [
            ("Volume Requerido:", f"{self.params.V0} m³"),
            ("Espessura:", f"{self.params.t * 100} cm"),
            ("Densidade:", f"{self.params.rho} kg/m³"),
            ("Comprimento Máx.:", f"{self.params.Lmax} m"),
            ("Diâmetro Máx.:", f"{self.params.Dmax} m"),
            ("Custo Material:", f"${self.params.cm}/kg"),
            ("Custo Soldagem:", f"${self.params.cw}/m"),
        ]
        
        for label, value in param_configs:
            frame = ctk.CTkFrame(problem_frame)
            frame.pack(fill="x", padx=10, pady=3)
            ctk.CTkLabel(frame, text=label, width=150, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(frame, text=value, anchor="e").pack(side="right", padx=5)
    
    def setup_method_parameters(self, parent):
        """Configura os parâmetros editáveis dos métodos de otimização."""
        method_frame = ctk.CTkFrame(parent)
        method_frame.pack(fill="x", pady=10, padx=5)
        
        ctk.CTkLabel(method_frame, text="Configurações dos Métodos", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))

        # Helper function to create entries
        def create_entry(parent, label_text, var):
            frame = ctk.CTkFrame(parent)
            frame.pack(fill="x", padx=5, pady=3)
            ctk.CTkLabel(frame, text=label_text, width=150, anchor="w").pack(side="left", padx=5)
            ctk.CTkEntry(frame, textvariable=var, width=100).pack(side="right", padx=5)

        self.d0_var = tk.DoubleVar(value=0.5)
        self.l0_var = tk.DoubleVar(value=1.0)
        self.max_iter_var = tk.IntVar(value=100)
        self.tolerance_var = tk.DoubleVar(value=1e-6)
        self.h_grad_var = tk.DoubleVar(value=1e-6)

        create_entry(method_frame, "Diâmetro Inicial (D₀):", self.d0_var)
        create_entry(method_frame, "Comprimento Inicial (L₀):", self.l0_var)
        create_entry(method_frame, "Max. Iterações:", self.max_iter_var)
        create_entry(method_frame, "Tolerância (norma grad):", self.tolerance_var)
        create_entry(method_frame, "Passo Derivada (h):", self.h_grad_var)

    def setup_control_buttons(self, parent):
        """Configura os botões de controle."""
        button_frame = ctk.CTkFrame(parent)
        button_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        
        ctk.CTkLabel(button_frame, text="Método:").pack(side="left", padx=(10,5), pady=5)
        self.method_var = tk.StringVar(value="Todos")
        ctk.CTkOptionMenu(
            button_frame,
            variable=self.method_var,
            values=["Steepest Descent", "Newton", "DFP", "Todos"]
        ).pack(side="left", padx=5, pady=5, expand=True, fill="x")
        
        self.run_button = ctk.CTkButton(button_frame, text="Executar Otimização", command=self.run_optimization)
        self.run_button.pack(side="right", padx=(5,10), pady=5)
        
    def setup_results_area(self, parent):
        """Configura a área de resultados."""
        results_frame = ctk.CTkFrame(parent)
        results_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=(5,10))
        results_frame.grid_rowconfigure(1, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
        
        title_frame = ctk.CTkFrame(results_frame)
        title_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(5,0))
        ctk.CTkLabel(title_frame, text="Resultados", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
        
        clear_button = ctk.CTkButton(title_frame, text="Limpar", command=self.clear_results, width=60)
        clear_button.pack(side="right")

        self.results_text = ctk.CTkTextbox(results_frame, wrap="word")
        self.results_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

    def setup_right_panel(self, parent):
        """Configura o painel direito com os gráficos."""
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        self.notebook = ttk.Notebook(parent)
        self.notebook.grid(row=0, column=0, sticky="nsew")
        
        self.contour_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.contour_frame, text=" Curvas de Nível e Trajetórias ")
        
        self.convergence_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.convergence_frame, text=" Convergência do Gradiente ")
        
        self.setup_plots()

    def setup_plots(self):
        """Configura os plots do Matplotlib."""
        plt.style.use('dark_background' if self.dark_mode.get() else 'default')
        plt.rcParams['font.size'] = 10

        def configure_plot_frame(frame):
            frame.grid_rowconfigure(0, weight=1)
            frame.grid_columnconfigure(0, weight=1)

        # Gráfico de curvas de nível
        configure_plot_frame(self.contour_frame)
        self.fig_contour = Figure(figsize=(8, 6), dpi=100)
        self.ax_contour = self.fig_contour.add_subplot(111)
        self.canvas_contour = FigureCanvasTkAgg(self.fig_contour, self.contour_frame)
        self.canvas_contour.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        
        # Gráfico de convergência
        configure_plot_frame(self.convergence_frame)
        self.fig_conv = Figure(figsize=(8, 6), dpi=100)
        self.ax_conv = self.fig_conv.add_subplot(111)
        self.canvas_conv = FigureCanvasTkAgg(self.fig_conv, self.convergence_frame)
        self.canvas_conv.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        
        self.plot_initial_view()

    def run_optimization(self):
        """Inicia a otimização em uma thread separada para não bloquear a GUI."""
        self.run_button.configure(state="disabled", text="Executando...")
        
        thread = threading.Thread(target=self._run_optimization_thread)
        thread.daemon = True
        thread.start()

    def _run_optimization_thread(self):
        """Thread que executa os cálculos de otimização."""
        try:
            x0 = np.array([self.d0_var.get(), self.l0_var.get()])
            max_iter = self.max_iter_var.get()
            tolerance = self.tolerance_var.get()
            h_grad = self.h_grad_var.get()
            
            methods_to_run = {
                "Steepest Descent": self.optimizer.steepest_descent,
                "Newton": self.optimizer.newton_method,
                "DFP": self.optimizer.dfp_method
            }
            
            selected_method = self.method_var.get()
            
            self.results.clear()
            
            if selected_method == "Todos":
                methods = methods_to_run.items()
            else:
                methods = [(selected_method, methods_to_run[selected_method])]
            
            for name, method_func in methods:
                result = method_func(x0, max_iter, tolerance, h_grad)
                self.results[name] = result
            
            self.root.after(0, self._update_results)
            
        except Exception as e:
            self.root.after(0, lambda: self._show_error(str(e)))
    
    def _show_error(self, error_message):
        """Exibe uma mensagem de erro na GUI."""
        messagebox.showerror("Erro de Execução", f"Ocorreu um erro durante a otimização:\n{error_message}")
        self.run_button.configure(state="normal", text="Executar Otimização")
    
    def _update_results(self):
        """Atualiza a GUI com os resultados da otimização."""
        self.results_text.delete("1.0", "end")
        
        results_str = ""
        for name, res in self.results.items():
            results_str += f"=== {name} ===\n"
            results_str += f"Iterações: {res.iterations}\n"
            results_str += f"Avaliações da Função: {res.function_evaluations}\n"
            results_str += f"Custo Final: ${res.final_f:,.2f}\n"
            results_str += "Solução Ótima:\n"
            results_str += f"  - Diâmetro (D): {res.final_x[0]:.4f} m\n"
            results_str += f"  - Comprimento (L): {res.final_x[1]:.4f} m\n"
            
            # Verificação das restrições no ponto final
            D_final, L_final = res.final_x
            V_final = (np.pi * D_final**2 * L_final) / 4
            results_str += "Verificação de Restrições:\n"
            results_str += f"  - Volume: {V_final:.4f} m³ (Meta: {self.params.V0} m³)\n"
            results_str += f"  - Limite D: {D_final:.4f} m <= {self.params.Dmax} m\n"
            results_str += f"  - Limite L: {L_final:.4f} m <= {self.params.Lmax} m\n\n"
        
        self.results_text.insert("1.0", results_str)
        
        self.update_plots()
        self.run_button.configure(state="normal", text="Executar Otimização")

    def plot_initial_view(self):
        """Plota o estado inicial dos gráficos antes da execução."""
        self.clear_plots()
        self.plot_contour_and_constraints()
        self.ax_conv.set_title("Convergência dos Métodos")
        self.ax_conv.set_xlabel("Iteração")
        self.ax_conv.set_ylabel("Norma do Gradiente (escala log)")
        self.ax_conv.grid(True, alpha=0.3)
        
        self.fig_contour.tight_layout()
        self.fig_conv.tight_layout()
        self.canvas_contour.draw()
        self.canvas_conv.draw()
        
    def plot_contour_and_constraints(self):
        """Plota as curvas de nível e a região factível."""
        D_range = np.linspace(0.1, self.params.Dmax * 1.1, 80)
        L_range = np.linspace(0.1, self.params.Lmax * 1.1, 80)
        D_grid, L_grid = np.meshgrid(D_range, L_range)
        
        Z = np.array([self.optimizer.objective_function(np.array([d, l])) 
                      for d, l in zip(np.ravel(D_grid), np.ravel(L_grid))])
        Z = Z.reshape(D_grid.shape)
        
        self.ax_contour.contour(D_grid, L_grid, Z, levels=np.logspace(3.5, 5.0, 15), alpha=0.7)
        self.ax_contour.set_title("Função de Custo, Região Factível e Trajetórias")
        self.ax_contour.set_xlabel("Diâmetro (D) [m]")
        self.ax_contour.set_ylabel("Comprimento (L) [m]")
        
        # Plotar região factível
        D_feas = np.linspace(0.1, self.params.Dmax, 200)
        L_min = (0.9 * self.params.V0) / (np.pi * D_feas**2 / 4)
        L_max = (1.1 * self.params.V0) / (np.pi * D_feas**2 / 4)
        
        L_min = np.clip(L_min, 0, self.params.Lmax)
        L_max = np.clip(L_max, 0, self.params.Lmax)
        
        self.ax_contour.fill_between(D_feas, L_min, L_max, color='green', alpha=0.2, label='Região Factível')
        
        self.ax_contour.set_xlim(0, self.params.Dmax * 1.1)
        self.ax_contour.set_ylim(0, self.params.Lmax * 1.1)
        self.ax_contour.grid(True, alpha=0.3)
    
    def update_plots(self):
        """Atualiza os gráficos com os resultados da otimização."""
        self.clear_plots()
        self.plot_contour_and_constraints()

        colors = {'Steepest Descent': 'red', 'Newton': 'cyan', 'DFP': 'orange'}
        
        # Gráfico de Contorno e Trajetórias
        for name, res in self.results.items():
            if len(res.x_history) > 1:
                x_hist = np.array(res.x_history)
                self.ax_contour.plot(x_hist[:, 0], x_hist[:, 1], 'o-', color=colors.get(name, 'white'), 
                                     linewidth=2, markersize=3, alpha=0.9, label=name)
                self.ax_contour.plot(x_hist[0, 0], x_hist[0, 1], 's', color='yellow', markersize=8, label=f'Início')
                self.ax_contour.plot(x_hist[-1, 0], x_hist[-1, 1], '*', color='magenta', markersize=12, markeredgecolor='black', label=f'Fim ({name})')

        self.ax_contour.legend()
        self.fig_contour.tight_layout()
        self.canvas_contour.draw()
        
        # Gráfico de Convergência
        for name, res in self.results.items():
            if res.gradient_norms:
                self.ax_conv.semilogy(range(len(res.gradient_norms)), res.gradient_norms, 'o-', 
                                      label=name, color=colors.get(name, 'white'), linewidth=2, markersize=3)
        
        self.ax_conv.legend()
        self.fig_conv.tight_layout()
        self.canvas_conv.draw()

    def clear_plots(self):
        self.ax_contour.clear()
        self.ax_conv.clear()

    def clear_results(self):
        """Limpa a área de texto e os gráficos."""
        self.results = {}
        self.results_text.delete("1.0", "end")
        self.plot_initial_view()

    def toggle_theme(self):
        """Alterna entre os temas claro e escuro."""
        self.dark_mode.set(not self.dark_mode.get())
        new_mode = "dark" if self.dark_mode.get() else "light"
        ctk.set_appearance_mode(new_mode)
        self.theme_button.configure(text="🌙 Tema Escuro" if new_mode == "dark" else "☀️ Tema Claro")
        
        # Recria os gráficos com o novo tema
        self.setup_plots()
        if self.results:
            self.update_plots()
        else:
            self.plot_initial_view()

def main():
    """Função principal para iniciar a aplicação."""
    try:
        root = ctk.CTk()
        app = OptimizationGUI(root)
        root.mainloop()
    except Exception as e:
        # Fallback para uma simples caixa de mensagem em caso de falha na inicialização
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Erro Fatal", f"Não foi possível iniciar a aplicação:\n{e}")

if __name__ == "__main__":
    main()