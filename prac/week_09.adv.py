"""Fit the rocket telemetry with NumPy's vectorised Chebyshev solver"""

import numpy as np

altitude_km = [
    0.0,
    7.8,
    26.0,
    52.7,
    85.6,
    122.0,
    158.3,
    191.5,
    219.3,
    241.2,
    257.0,
    267.9,
    274.2,
    278.0,
    280.1,
]

time_s = [0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240, 260, 280]

def quantify_error(y, y_fit):
    """Return the sum of squared errors between two equally shaped arrays"""
    y = np.asarray(y, dtype=float)
    y_fit = np.asarray(y_fit, dtype=float)
    if y.shape != y_fit.shape:
        raise ValueError("y and y_fit must have the same shape")
    return float(np.sum((y - y_fit) ** 2))



def main():
    model = np.polynomial.Chebyshev.fit(time_s, altitude_km, 4)
    return quantify_error(altitude_km, model(time_s))


if __name__ == "__main__":
    error = main()
    assert np.isfinite(error)
    print(error)
