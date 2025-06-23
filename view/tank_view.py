import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading

from model.tank_model import Parameters, TankOptimizer  # IMPORTANTE: precisa ajustar o path conforme seu projeto

class OptimizationGUI:
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
