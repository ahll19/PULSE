from point_process import InhomogeneousPoisson, HomogeneousPoisson, Region

import numpy as np
import matplotlib.pyplot as plt


if __name__ == "__main__":
    x_max = 10
    y_max = 10
    n_intensity_samples = 100
    region = Region(np.array([[0, x_max], [0, y_max]]))

    intensity = lambda x, args: 2 + np.sin(x[0]) + np.cos(x[1])
    intensity = lambda x, args: 3 + x[0] ** 2 + x[1] ** 1.5

    intensity_sample = np.array(
        [
            [
                intensity(
                    [i * x_max / n_intensity_samples, j * y_max / n_intensity_samples],
                    None,
                )
                for i in range(n_intensity_samples)
            ]
            for j in range(n_intensity_samples)
        ]
    )

    process = InhomogeneousPoisson(region, intensity, intensity_maximum_estimate=1)
    points, n_sim, n_disc = process.simulate_process(n_points=1000)

    cb = plt.imshow(intensity_sample, extent=[0, 10, 0, 10], cmap="hot", origin="lower")
    plt.colorbar(cb)
    plt.scatter(points[:, 0], points[:, 1])
    plt.title(f"Simulation, N={points.shape[0]}")
    plt.show()
