from typing import Callable, Tuple

import numpy.typing as npt
import numpy as np

from .region import Region


class HomogeneousPoisson:
    region: Region = None
    intensity: float = None

    def __init__(self, region: Region, intesity: float = 1.0) -> None:
        assert isinstance(region, Region), "region must be a Region object"
        assert isinstance(intesity, float), "intensity must be a float"

        self.region = region
        self.intensity = intesity

    def simulate_process(self, n_points: int = None) -> npt.ArrayLike:
        region_volume, err = self.region.integrate()
        n_points = 0
        while n_points == 0:
            n_points = n_points or np.random.poisson(region_volume * self.intensity)

        points = np.random.uniform(
            low=self.region.ranges[:, 0],
            high=self.region.ranges[:, 1],
            size=(n_points, self.region.N),
        )

        return points


class InhomogeneousPoisson:
    region: Region = None
    intensity: Callable = None
    args: Tuple = None
    intensity_maximum_estimate: float = None
    intensity_maximum_estimate_history = None

    def __init__(
        self,
        region: Region,
        intensity: Callable,
        args: Tuple = None,
        intensity_maximum_estimate: float = 1.0,
    ) -> None:
        assert isinstance(region, Region), "region must be a Region object"
        assert callable(intensity), "intensity must be a callable"

        self.region = region
        self.intensity = intensity
        self.args = args
        self.intensity_maximum_estimate = intensity_maximum_estimate
        self.intensity_maximum_estimate_history = [intensity_maximum_estimate]

    def simulate_process(self, n_points: int = None) -> Tuple[npt.ArrayLike, int, int]:
        """
        Simulate a Poisson process with intensity function intensity over the region
        specified by self.region.

        Simulation is done by thinning, and the intensity function maximum is changed
        if a new maximum is found. If that happens the simulation is restarted.

        Args:
            n_points (int, optional):
            Specify if specific number of points is wanted. Defaults to None.

        Returns:
            Tuple[npt.ArrayLike, int, int]:
                npt.ArrayLike: array of points in the region
                int: number of points simulated
                int: number of points discarded
        """
        intensity_measure, err = self.region.integrate(self.intensity)
        _n_points = 0
        while _n_points == 0:
            _n_points = n_points or np.random.poisson(intensity_measure)

        n_simulated_points = 0
        n_discarded_points = 0
        points = list()

        while n_simulated_points < _n_points:
            point = np.random.uniform(
                low=self.region.ranges[:, 0], high=self.region.ranges[:, 1]
            )

            # calculate intensity at point, and check if new max is found
            intensity = self.intensity(point, self.args)
            if intensity <= self.intensity_maximum_estimate:
                r_u = np.random.uniform(0, self.intensity_maximum_estimate)
                if r_u > intensity:
                    n_discarded_points += 1
                else:
                    points.append(point)
                    n_simulated_points += 1

                continue

            print(f"New intensity maximum found: {intensity}")
            print(f"Will change old maximum {self.intensity_maximum_estimate}")
            print("Restarting simulation")
            print()

            self.intensity_maximum_estimate_history.append(intensity)
            self.intensity_maximum_estimate = intensity
            n_simulated_points = 0
            n_discarded_points = 0
            points = list()

        return np.array(points), n_simulated_points, n_discarded_points
