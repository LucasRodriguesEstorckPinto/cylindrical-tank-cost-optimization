import customtkinter as ctk
from controllers.optimizer_controller import OptimizerController
from utils.plot_utils import plot_contours_with_trajectory, plot_error_convergence
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class TankOptimizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Otimização de Tanque Cilíndrico")
        self.geometry("1000x700")

        self.controller = OptimizerController()
        self.result = None

        self.create_tabs()

    def create_tabs(self):
        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(fill="both", expand=True, padx=20, pady=20)

        self.tab_config = self.tabs.add("Configuração")
        self.tab_result = self.tabs.add("Resultado")
        self.tab_graficos = self.tabs.add("Gráficos")
        self.tab_info = self.tabs.add("Visualização do Problema")

        self.build_tab_config()
        self.build_tab_result()
        self.build_tab_graficos()
        self.build_tab_info()

    def build_tab_config(self):
        ctk.CTkLabel(self.tab_config, text="Método de Otimização", font=("Arial", 16)).pack(pady=10)
        self.method_var = ctk.StringVar(value="Steepest Descent")
        ctk.CTkOptionMenu(self.tab_config, values=["Steepest Descent", "Newton", "DFP"], variable=self.method_var).pack()

        def create_entry(label, default):
            ctk.CTkLabel(self.tab_config, text=label).pack()
            entry = ctk.CTkEntry(self.tab_config, placeholder_text=default)
            entry.pack()
            return entry

        self.x0_entry = create_entry("Estimativa Inicial (D, L)", "0.5, 1.0")
        self.alpha_entry = create_entry("Passo (alpha)", "0.01")
        self.tol_entry = create_entry("Tolerância", "1e-6")

        ctk.CTkButton(self.tab_config, text="Executar", command=self.run_optimization).pack(pady=15)

    def build_tab_result(self):
        self.result_label = ctk.CTkLabel(self.tab_result, text="", font=("Arial", 14))
        self.result_label.pack(pady=10)

        self.table = ctk.CTkTextbox(self.tab_result, width=800, height=400)
        self.table.pack(pady=10)
    def run_optimization(self):
        try:
            method = self.method_var.get()
            x0 = [float(v.strip()) for v in self.x0_entry.get().split(",")]
            alpha = float(self.alpha_entry.get())
            tol = float(self.tol_entry.get())

            options = {"alpha": alpha, "tol": tol, "max_iter": 100}
            self.result = self.controller.run(method, x0, options)

            sol = self.result["solution"]
            custo = self.result["cost"]
            iters = self.result["iterations"]
            historico = self.result["history"]

            self.result_label.configure(
                text=f"Solução: D={sol[0]:.4f}, L={sol[1]:.4f}\n"
                     f"Custo = ${custo:.2f} | Iterações: {iters} | Avaliações: {len(historico)}"
            )

            self.table.delete("0.0", "end")
            header = f"{'Iter':<6}{'D':<12}{'L':<12}{'Custo':<14}{'Erro':<12}\n"
            self.table.insert("end", header)
            self.table.insert("end", "-" * len(header) + "\n")

            for i, (x, fval, err) in enumerate(historico):
                line = f"{i:<6}{x[0]:<12.4f}{x[1]:<12.4f}{fval:<14.2f}{err:<12.2e}\n"
                self.table.insert("end", line)
            

            self.plot_graphs()

        except Exception as e:
            self.result_label.configure(text=f"Erro: {str(e)}")

    def build_tab_graficos(self):
        self.canvas_contour = None
        self.canvas_error = None

    def plot_graphs(self):
        if self.canvas_contour:
            self.canvas_contour.get_tk_widget().destroy()
        if self.canvas_error:
            self.canvas_error.get_tk_widget().destroy()

        fig1 = plot_contours_with_trajectory(self.controller.model, self.result["history"])
        fig2 = plot_error_convergence(self.result["history"])

        self.canvas_contour = FigureCanvasTkAgg(fig1, master=self.tab_graficos)
        self.canvas_contour.get_tk_widget().pack()
        self.canvas_contour.draw()

        self.canvas_error = FigureCanvasTkAgg(fig2, master=self.tab_graficos)
        self.canvas_error.get_tk_widget().pack()
        self.canvas_error.draw()

    def build_tab_info(self):
        text = (
            "Este projeto resolve a otimização do custo de um tanque cilíndrico com restrições.\n\n"
            "Função objetivo:\n"
            "C(D, L) = 4.5 * m(D, L) + 20 * ℓw(D)\n\n"
            "Restrições:\n"
            "0.9*V0 ≤ (π D² / 4) L ≤ 1.1*V0\n"
            "D ≤ 1,  L ≤ 2\n\n"
            "Onde:\n"
            "- m(D, L): massa do tanque\n"
            "- ℓw(D): comprimento da solda\n"
        )
        label = ctk.CTkLabel(self.tab_info, text=text, justify="left")
        label.pack(pady=20, padx=20)


