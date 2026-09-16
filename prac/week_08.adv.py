"""
Extend the nozzle solution with Newton's method for the practice exercises
"""

from math import cos, isclose, isfinite, pi, sin, sqrt

# == Constants ==
CP = 1005
T0 = 900
P0 = 350000
GAMMA = 1.4
EXIT_VELOCITY = 700
H = 8.3
EMISSIVITY = 0.9
SIGMA = 5.669e-8
TS = 278
TG = 302


# == Functions ==
def func(p):
    """Return the velocity residual in m/s for pressure p in Pa"""
    if not 0 <= p <= P0:
        raise ValueError("Pressure must be between 0 and P0")
    return sqrt(2 * CP * T0 * (1 - (p / P0) ** ((GAMMA - 1) / GAMMA))) - (
        EXIT_VELOCITY
    )


def bisect(f, p_left, p_right, tol=1e-8):
    """Bisect a continuous function until abs(f(p)) < tol"""
    if not isfinite(tol) or tol <= 0:
        raise ValueError("tol must be positive and finite")
    if not (isfinite(p_left) and isfinite(p_right)) or p_left > p_right:
        raise ValueError("Endpoints must be finite and ordered")

    f_left = f(p_left)
    if not isfinite(f_left):
        raise ValueError("Function values must be finite")
    if f_left == 0:
        return p_left
    f_right = f(p_right)
    if not isfinite(f_right):
        raise ValueError("Function values must be finite")
    if f_right == 0:
        return p_right
    if (f_left > 0) == (f_right > 0):
        return None

    while True:
        p_mid = 0.5 * p_left + 0.5 * p_right
        f_mid = f(p_mid)
        if not isfinite(f_mid):
            raise ValueError("Function values must be finite")
        if abs(f_mid) < tol:
            return p_mid
        if p_mid == p_left or p_mid == p_right:
            raise ArithmeticError("Tolerance is below floating-point precision")
        if (f_left > 0) == (f_mid > 0):
            p_left, f_left = p_mid, f_mid
        else:
            p_right = p_mid


def main():
    return bisect(func, 50000, P0)


def newton(f, df, x0, tol=1e-8, max_iter=50):
    """Return a Newton root with abs(f(x)) < tol or report non-convergence"""
    if not isfinite(tol) or tol <= 0 or not isfinite(x0):
        raise ValueError("tol must be positive and finite, and x0 finite")
    if not isinstance(max_iter, int) or max_iter < 1:
        raise ValueError("max_iter must be a positive integer")
    x = x0
    for iteration in range(max_iter + 1):
        value = f(x)
        if not isfinite(value):
            raise ValueError("Function values must be finite")
        if abs(value) < tol:
            return x
        if iteration == max_iter:
            break
        slope = df(x)
        if not isfinite(slope) or slope == 0:
            raise ValueError("Derivative must be finite and non-zero")
        x -= value / slope
        if not isfinite(x):
            raise ArithmeticError(
                "Newton iteration produced a non-finite value"
            )
    raise RuntimeError("Newton's method did not converge")


def thermometer_balance(temperature):
    return H * (TG - temperature) - SIGMA * EMISSIVITY * (
        temperature**4 - TS**4
    )


def thermometer_derivative(temperature):
    return -H - 4 * SIGMA * EMISSIVITY * temperature**3


if __name__ == "__main__":
    assert bisect(lambda x: x, 0, 1) == 0
    assert bisect(lambda x: x - 1, 0, 1) == 1
    assert bisect(lambda x: x - 1, 0, 2) == 1
    assert bisect(lambda x: x**2 + 1, -1, 1) is None
    root = bisect(lambda x: x**2 - 2, 0, 2)
    assert root is not None and isclose(root, sqrt(2), abs_tol=1e-8)
    assert isclose(
        newton(lambda x: x**2 - 2, lambda x: 2 * x, 1), sqrt(2), abs_tol=1e-8
    )
    pressure = main()
    assert pressure is not None and abs(func(pressure)) < 1e-8
    print(f"Nozzle exit pressure: {pressure:.6f} Pa")

    temperature = newton(thermometer_balance, thermometer_derivative, TG)
    assert TS < temperature < TG
    assert abs(thermometer_balance(temperature)) < 1e-8
    print(f"Thermometer temperature: {temperature:.6f} K")
    print(f"Measurement error (Tt - Tg): {temperature - TG:.6f} K")

    for eccentricity, mean_anomaly in ((0.05, pi / 4), (0.15, 2 * pi / 3)):

        def kepler(anomaly, e=eccentricity, M=mean_anomaly):
            return anomaly - e * sin(anomaly) - M

        def kepler_derivative(anomaly, e=eccentricity):
            return 1 - e * cos(anomaly)

        anomaly = newton(kepler, kepler_derivative, mean_anomaly)
        bracket_root = bisect(
            kepler, mean_anomaly - eccentricity, mean_anomaly + eccentricity
        )
        assert bracket_root is not None
        assert isclose(anomaly, bracket_root, abs_tol=2e-8)
        print(f"Kepler e={eccentricity:.2f}: E={anomaly:.9f} rad")
