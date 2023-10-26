import numpy.typing as npt
import numpy as np
import pygsl
from pygsl import monte
from typing import Callable, Tuple


class Region:
    ranges: npt.ArrayLike = None
    N: int = None

    def __init__(self, ranges: npt.ArrayLike) -> None:
        # make sure ranges is a 2xN array, and is numeric data
        ranges = np.array(ranges)
        assert ranges.shape[0] == 2, "ranges must be a 2xN array"
        assert np.issubdtype(ranges.dtype, np.number), "ranges must be numeric"
        self.ranges = ranges
        self.N = ranges.shape[1]

    def integrate(
        self, func: Callable = None, args=None, n_calls: int = None
    ) -> Tuple[float, float]:
        """
        Integrate func over the region specified by self.ranges.

        Args:
            func (callable, optional):
                Function to integrate, none calculates hypervolume.
                Func should be of form func(x, args), where x is an N vector, and args
                is a single object.
                Defaults to None.
            args (tuple, optional):
                Arguments to pass to func.
                Defaults to None.
            n_calls (int, optional):
                Number of function calls to use in integration.
                If none is given, uses 10*N.
                Defaults to None.

        Returns:
            float: integral of func over the region
            float: error estimate of the integral
        """

        # use monte to integrate func over the region using vegas
        vegas = monte.vegas(self.N)
        xl = self.ranges[:, 0]
        xu = self.ranges[:, 1]
        n_calls = n_calls or 10 * self.N
        func = monte.gsl_monte_function(func or (lambda x, args: 1), args, self.N)
        r = pygsl.rng.ran0()

        val, abserr = vegas.integrate(func, xl, xu, n_calls, r)

        return val, abserr
