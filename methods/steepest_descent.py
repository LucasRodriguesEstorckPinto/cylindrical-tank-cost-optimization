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

def steepest_descent(model, x0, options):
    x = np.array(x0, dtype=float)
    alpha = options.get("alpha", 0.01)
    tol = options.get("tol", 1e-6)
    max_iter = options.get("max_iter", 100)

    history = []
    iterations = 0

    for i in range(max_iter):
        grad = numerical_gradient(model, x)
        norm_grad = np.linalg.norm(grad)
        history.append((x.copy(), model.custo(*x), norm_grad))

        if norm_grad < tol:
            break

        # Descida do gradiente
        x = x - alpha * grad

        # Corrigir se sair das restrições
        D, L = x
        D = min(max(D, 0.01), model.D_max)
        L = min(max(L, 0.01), model.L_max)
        if not model.respeita_restricoes(D, L):
            # Volta para dentro de região viável mais próxima
            while not model.respeita_restricoes(D, L) and alpha > 1e-8:
                alpha *= 0.5
                x = x + alpha * grad  # volta atrás
            D, L = x

        x = np.array([D, L])
        iterations += 1

    return {
        "solution": x.tolist(),
        "cost": model.custo(*x),
        "iterations": iterations,
        "history": history,
    }
