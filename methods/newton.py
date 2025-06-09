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

def numerical_hessian(model, x, h=1e-5):
    n = len(x)
    hess = np.zeros((n, n))
    fx = model.custo(*x)
    
    for i in range(n):
        for j in range(n):
            x_ij1 = np.copy(x)
            x_ij2 = np.copy(x)
            x_ij3 = np.copy(x)
            x_ij4 = np.copy(x)

            x_ij1[i] += h
            x_ij1[j] += h

            x_ij2[i] += h
            x_ij2[j] -= h

            x_ij3[i] -= h
            x_ij3[j] += h

            x_ij4[i] -= h
            x_ij4[j] -= h

            f1 = model.custo(*x_ij1)
            f2 = model.custo(*x_ij2)
            f3 = model.custo(*x_ij3)
            f4 = model.custo(*x_ij4)

            hess[i, j] = (f1 - f2 - f3 + f4) / (4 * h**2)

    return hess

def newton_method(model, x0, options):
    x = np.array(x0, dtype=float)
    tol = options.get("tol", 1e-6)
    max_iter = options.get("max_iter", 100)

    history = []
    for i in range(max_iter):
        grad = numerical_gradient(model, x)
        hess = numerical_hessian(model, x)
        norm_grad = np.linalg.norm(grad)

        history.append((x.copy(), model.custo(*x), norm_grad))

        if norm_grad < tol:
            break

        try:
            dx = -np.linalg.solve(hess, grad)
        except np.linalg.LinAlgError:
            break  # Hessiana singular

        x += dx

        # Corrigir e projetar para dentro das restrições
        D, L = x
        D = min(max(D, 0.01), model.D_max)
        L = min(max(L, 0.01), model.L_max)
        x = np.array([D, L])

        if not model.respeita_restricoes(D, L):
            break

    return {
        "solution": x.tolist(),
        "cost": model.custo(*x),
        "iterations": len(history),
        "history": history
    }
