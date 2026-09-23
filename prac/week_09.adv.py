"""Fit the rocket telemetry with NumPy's vectorised Chebyshev solver"""

import numpy as np
from week_09 import altitude_km, quantify_error, time_s


def main():
    model = np.polynomial.Chebyshev.fit(time_s, altitude_km, 4)
    return quantify_error(altitude_km, model(time_s))


if __name__ == "__main__":
    error = main()
    assert np.isfinite(error)
    print(error)
