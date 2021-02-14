from typing import Optional, Sequence, Tuple

import numpy
from arbol import aprint
from scipy.optimize import minimize

from dexp.processing.backends.backend import Backend


def linsolve(a, y, x0=None,
             maxiter: int = 1e12,
             maxfun: int = 1e12,
             tolerance: float = 1e-6,
             order_error: float = 1,
             order_reg: float = 1,
             alpha_reg: float = 1e-1,
             l2_init: bool = True,
             bounds: Optional[Sequence[Tuple[float, float]]] = None,
             limited: bool = True,
             verbose: bool = False):
    xp = Backend.get_xp_module()
    sp = Backend.get_sp_module()

    a = Backend.to_backend(a)
    y = Backend.to_backend(y)

    if x0 is None:
        if l2_init:
            # x0, _, _, _ = numpy.linalg.lstsq(a, y)
            x0 = linsolve(a, y, x0=x0,
                          maxiter=maxiter,
                          tolerance=tolerance,
                          order_error=2,
                          alpha_reg=0,
                          l2_init=False)
        else:
            x0 = numpy.zeros(a.shape[1])

    def fun(x):
        x = Backend.to_backend(x)
        if alpha_reg == 0:
            objective = float(xp.linalg.norm(a @ x - y, ord=order_error))
        else:
            objective = float(xp.linalg.norm(a @ x - y, ord=order_error) + alpha_reg * xp.linalg.norm(x, ord=order_reg))
        return objective

    result = minimize(fun,
                      x0,
                      method='L-BFGS-B' if limited else 'BFGS',
                      tol=tolerance,
                      bounds=bounds if limited else None,
                      options={'disp': verbose,
                               'maxiter': maxiter,
                               'maxfun': maxfun,
                               'gtol': tolerance},
                      )
    if result.nit == 0:
        aprint(f"Warning: optimisation finished after {result.nit} iterations!")

    if not result.success:
        raise RuntimeWarning(f"Convergence failed: '{result.message}' after {result.nit} iterations and {result.nfev} function evaluations.")

    return result.x