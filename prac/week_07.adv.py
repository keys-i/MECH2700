"""
Aircraft acceleration using modified Euler with preallocated arrays
"""

import numpy as np

# -- consts --
THRUST_ACCEL = 242000 / 70000
DRAG_FACTOR = 0.5 * 0.08 * 125 * 1.225 / 70000


# -- functs --
def modified_euler_step(func, t0, y0, h):
    k1 = func(t0, y0)
    return y0 + h / 2 * (k1 + func(t0 + h, y0 + h * k1))


def integrate_ode(func, t0, y0, h, n_steps):
    if n_steps < 0:
        raise ValueError("n_steps must be non-negative")
    ts = t0 + h * np.arange(n_steps + 1)
    ys = np.empty((n_steps + 1,) + np.shape(y0), dtype=float)
    ys[0] = y0
    for i in range(n_steps):
        ys[i + 1] = modified_euler_step(func, ts[i], ys[i], h)
    return ts, ys


def aircraft_ode(t, state):
    v = state[1]
    return np.array((v, THRUST_ACCEL - DRAG_FACTOR * v**2))


def main():
    _, ys = integrate_ode(aircraft_ode, 0, np.zeros(2), 1.0, 20)
    return float(ys[-1, 1])


if __name__ == "__main__":
    _, ys = integrate_ode(lambda t, y: y**2, 0, 1, 0.1, 1)
    np.testing.assert_allclose(ys, [1, 1.1105])
    print(main())
