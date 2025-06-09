import numpy as np

def numerical_gradient(model, x, h=1e-6):
    grad = np.zeros_like(x)
    for i in range(len(x)):
        x_forward = np.copy(x)
        x_backward = np.copy(x)
        x_forward[i] += h
        x_backward[i] -= h

        f_forward = model.custo(*x_forward)
        f_backward = model.custo(*x_backward)

        grad[i] = (f_forward - f_backward) / (2 * h)
    return grad

def dfp_method(model, x0, options):
    x = np.array(x0, dtype=float)
    tol = options.get("tol", 1e-6)
    max_iter = options.get("max_iter", 100)

    n = len(x)
    H = np.eye(n)
    grad = numerical_gradient(model, x)
    history = []

    for i in range(max_iter):
        norm_grad = np.linalg.norm(grad)
        history.append((x.copy(), model.custo(*x), norm_grad))

        if norm_grad < tol:
            break

        d = -np.dot(H, grad)
        alpha = 1.0

        x_new = x + alpha * d
        D, L = x_new
        D = min(max(D, 0.01), model.D_max)
        L = min(max(L, 0.01), model.L_max)
        x_new = np.array([D, L])

        if not model.respeita_restricoes(D, L):
            break

        grad_new = numerical_gradient(model, x_new)
        delta_x = x_new - x
        delta_g = grad_new - grad

        dx = delta_x.reshape((n, 1))
        dg = delta_g.reshape((n, 1))

        H = H + (dx @ dx.T) / (dx.T @ dg) - (H @ dg @ dg.T @ H) / (dg.T @ H @ dg)

        x = x_new
        grad = grad_new

    return {
        "solution": x.tolist(),
        "cost": model.custo(*x),
        "iterations": len(history),
        "history": history
    }
