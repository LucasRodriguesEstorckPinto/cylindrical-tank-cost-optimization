import numpy as np
import matplotlib.pyplot as plt

def plot_contours_with_trajectory(model, history):
    fig, ax = plt.subplots(figsize=(5, 4))
    D_vals = np.linspace(0.1, 1, 100)
    L_vals = np.linspace(0.1, 2, 100)
    D_grid, L_grid = np.meshgrid(D_vals, L_vals)
    C_grid = np.vectorize(lambda D, L: model.custo(D, L))(D_grid, L_grid)

    ax.contour(D_grid, L_grid, C_grid, levels=30)
    path = np.array([x for x, _, _ in history])
    ax.plot(path[:, 0], path[:, 1], 'ro-', linewidth=2)
    ax.set_xlabel("D")
    ax.set_ylabel("L")
    ax.set_title("Curvas de Nível + Trajetória")
    return fig

def plot_error_convergence(history):
    fig, ax = plt.subplots(figsize=(5, 4))
    errors = [err for _, _, err in history]
    ax.plot(errors, marker='o')
    ax.set_yscale('log')
    ax.set_title("Erro vs Iterações")
    ax.set_xlabel("Iterações")
    ax.set_ylabel("Erro (norma do gradiente)")
    return fig
