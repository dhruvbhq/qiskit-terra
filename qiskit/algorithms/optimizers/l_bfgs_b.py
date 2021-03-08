# This code is part of Qiskit.
#
# (C) Copyright IBM 2018, 2020.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""Limited-memory BFGS Bound optimizer."""

from scipy import optimize as sciopt
from .optimizer import Optimizer, OptimizerSupportLevel


class L_BFGS_B(Optimizer):  # pylint: disable=invalid-name
    """
    Limited-memory BFGS Bound optimizer.

    The target goal of Limited-memory Broyden-Fletcher-Goldfarb-Shanno Bound (L-BFGS-B)
    is to minimize the value of a differentiable scalar function :math:`f`.
    This optimizer is a quasi-Newton method, meaning that, in contrast to Newtons's method,
    it does not require :math:`f`'s Hessian (the matrix of :math:`f`'s second derivatives)
    when attempting to compute :math:`f`'s minimum value.

    Like BFGS, L-BFGS is an iterative method for solving unconstrained, non-linear optimization
    problems, but approximates BFGS using a limited amount of computer memory.
    L-BFGS starts with an initial estimate of the optimal value, and proceeds iteratively
    to refine that estimate with a sequence of better estimates.

    The derivatives of :math:`f` are used to identify the direction of steepest descent,
    and also to form an estimate of the Hessian matrix (second derivative) of :math:`f`.
    L-BFGS-B extends L-BFGS to handle simple, per-variable bound constraints.

    Uses scipy.optimize.fmin_l_bfgs_b.
    For further detail, please refer to
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.fmin_l_bfgs_b.html
    """

    _OPTIONS = ['maxfun', 'maxiter', 'factr', 'iprint', 'epsilon']

    # pylint: disable=unused-argument
    def __init__(self,
                 maxfun: int = 1000,
                 maxiter: int = 15000,
                 factr: float = 10,
                 iprint: int = -1,
                 epsilon: float = 1e-08) -> None:
        r"""
        Args:
            maxfun: Maximum number of function evaluations.
            maxiter: Maximum number of iterations.
            factr: The iteration stops when (f\^k - f\^{k+1})/max{\|f\^k\|,
                \|f\^{k+1}\|,1} <= factr * eps, where eps is the machine precision,
                which is automatically generated by the code. Typical values for
                factr are: 1e12 for low accuracy; 1e7 for moderate accuracy;
                10.0 for extremely high accuracy. See Notes for relationship to ftol,
                which is exposed (instead of factr) by the scipy.optimize.minimize
                interface to L-BFGS-B.
            iprint: Controls the frequency of output. iprint < 0 means no output;
                iprint = 0 print only one line at the last iteration; 0 < iprint < 99
                print also f and \|proj g\| every iprint iterations; iprint = 99 print
                details of every iteration except n-vectors; iprint = 100 print also the
                changes of active set and final x; iprint > 100 print details of
                every iteration including x and g.
            epsilon: Step size used when approx_grad is True, for numerically
                calculating the gradient
        """
        super().__init__()
        for k, v in list(locals().items()):
            if k in self._OPTIONS:
                self._options[k] = v

    def get_support_level(self):
        """ Return support level dictionary """
        return {
            'gradient': OptimizerSupportLevel.supported,
            'bounds': OptimizerSupportLevel.supported,
            'initial_point': OptimizerSupportLevel.required
        }

    def optimize(self, num_vars, objective_function, gradient_function=None,
                 variable_bounds=None, initial_point=None):
        super().optimize(num_vars, objective_function, gradient_function,
                         variable_bounds, initial_point)

        if gradient_function is None and self._max_evals_grouped > 1:
            epsilon = self._options['epsilon']
            gradient_function = Optimizer.wrap_function(Optimizer.gradient_num_diff,
                                                        (objective_function,
                                                         epsilon, self._max_evals_grouped))

        approx_grad = bool(gradient_function is None)
        sol, opt, info = sciopt.fmin_l_bfgs_b(objective_function,
                                              initial_point, bounds=variable_bounds,
                                              fprime=gradient_function,
                                              approx_grad=approx_grad, **self._options)

        return sol, opt, info['funcalls']