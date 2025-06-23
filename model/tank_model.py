import numpy as np
from dataclasses import dataclass
from typing import List, Callable

@dataclass
class Parameters:
    V0: float = 0.8
    t: float = 0.03
    rho: float = 8000
    Lmax: float = 2.0
    Dmax: float = 1.0
    cm: float = 4.5
    cw: float = 20.0

@dataclass
class OptimizationResult:
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
    def __init__(self, params: Parameters):
        self.params = params

    def objective_function(self, x):  # função original
        D, L = x[0], x[1]
        if D <= 0 or L <= 0:
            return float('inf')
        p = self.params
        v_cylinder_wall = L * np.pi * ((D / 2 + p.t)**2 - (D / 2)**2)
        v_plates = 2 * np.pi * (D / 2 + p.t)**2 * p.t
        m = p.rho * (v_cylinder_wall + v_plates)
        lw = 4 * np.pi * (D + p.t)
        C = p.cm * m + p.cw * lw
        return C

    def constraints_penalty(self, x, penalty_factor=1e7):
        D, L = x[0], x[1]
        penalty = 0.0
        V_internal = np.pi * D**2 * L / 4
        lower_vol_bound = 0.9 * self.params.V0
        upper_vol_bound = 1.1 * self.params.V0
        if V_internal < lower_vol_bound:
            penalty += penalty_factor * (lower_vol_bound - V_internal)**2
        if V_internal > upper_vol_bound:
            penalty += penalty_factor * (V_internal - upper_vol_bound)**2
        if L > self.params.Lmax:
            penalty += penalty_factor * (L - self.params.Lmax)**2
        if D > self.params.Dmax:
            penalty += penalty_factor * (D - self.params.Dmax)**2
        if D <= 0:
            penalty += penalty_factor * (-D + 1e-3)**2
        if L <= 0:
            penalty += penalty_factor * (-L + 1e-3)**2
        return penalty

    def penalized_objective(self, x):
        return self.objective_function(x) + self.constraints_penalty(x)

    def gradient_numerical(self, f: Callable, x, h=1e-6):
        grad = np.zeros_like(x)
        for i in range(len(x)):
            x_plus = x.copy()
            x_plus[i] += h
            x_minus = x.copy()
            x_minus[i] -= h
            grad[i] = (f(x_plus) - f(x_minus)) / (2 * h)
        return grad

    def hessian_numerical(self, f: Callable, x, h=1e-5):
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

    def line_search_backtrack(self, f: Callable, x, direction, grad, alpha_init=1.0, c1=1e-4, rho=0.5):
        alpha = alpha_init
        f_x = f(x)
        grad_dot_direction = np.dot(grad, direction)
        evals = 0
        for _ in range(50):
            if f(x + alpha * direction) <= f_x + c1 * alpha * grad_dot_direction:
                return alpha, evals + 1
            alpha *= rho
            evals += 1
        return alpha, evals

    def steepest_descent(self, x0, max_iter, tol, h_grad):
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

    def newton_method(self, x0, max_iter, tol, h_grad):
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
                reg = 1e-8
                while True:
                    try:
                        hess_reg = hess + reg * np.eye(len(x))
                        direction = np.linalg.solve(hess_reg, -grad)
                        if np.dot(direction, grad) < 0:
                            break
                    except np.linalg.LinAlgError:
                        pass
                    reg *= 10
                    if reg > 1e2:
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

    def dfp_method(self, x0, max_iter, tol, h_grad):
        x = x0.copy()
        n = len(x)
        H = np.eye(n)
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
