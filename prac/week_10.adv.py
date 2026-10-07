"""Compare Euler and fourth-order Runge-Kutta for fixed-temperature ends"""

import matplotlib.pyplot as plt
import numpy as np

# == Constants ==
D = 2.2e-5  # Thermal diffusivity [m^2/s]
L = 0.5  # Rod length [m]
N = 40  # Number of subdivisions
T0 = 600  # Left boundary temperature [K]
TL = 300  # Right boundary temperature [K]
tplot = 200  # Plot interval [s]
tmax = 1000  # Simulation duration [s]


# == Functions ==
def euler_step(T, t, D, dt, dx):
    """Advance the original explicit solution with fixed end temperatures"""
    Tnew = T.copy()
    sigma = dt * D / dx**2
    Tnew[1:-1] = sigma * T[:-2] + (1 - 2 * sigma) * T[1:-1] + sigma * T[2:]
    Tnew[0] = T0
    Tnew[-1] = TL
    return Tnew


def f(t, T):
    """Return the semi-discrete heat equation with zero end derivatives"""
    dx = L / N
    derivative = np.zeros_like(T, dtype=float)
    derivative[1:-1] = D * (T[2:] - 2 * T[1:-1] + T[:-2]) / dx**2
    return derivative


def runge_kutta_step(func, t, T, dt):
    """Advance an ODE system with the classical fourth-order method"""
    k1 = func(t, T)
    k2 = func(t + dt / 2, T + dt * k1 / 2)
    k3 = func(t + dt / 2, T + dt * k2 / 2)
    k4 = func(t + dt, T + dt * k3)
    return T + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6


def main():
    x = np.linspace(0.0, L, N + 1)
    dx = x[1] - x[0]
    dt = 0.5 * dx * dx / D
    print(f"Time step: {dt:.6f} s")

    T = np.full(N + 1, TL, dtype=float)
    # Zero end derivatives preserve the temperatures supplied initially
    T[0] = T0
    Trk = T.copy()
    _, axes = plt.subplots(1, 2, sharey=True, figsize=(11, 4.5))
    for ax, title in zip(axes, ("Explicit Euler", "Fourth-order Runge-Kutta")):
        ax.plot(x, T, ".-", label="t = 0.0 s")
        ax.set_title(title)
        ax.set_xlabel("Position [m]")
    axes[0].set_ylabel("Temperature [K]")

    t = 0.0
    next_plot = tplot
    while t < tmax:
        T = euler_step(T, t, D, dt, dx)
        Trk = runge_kutta_step(f, t, Trk, dt)
        t += dt
        if t >= next_plot:
            next_plot += tplot
            axes[0].plot(x, T, ".-", label=f"t = {t:.2f} s")
            axes[1].plot(x, Trk, ".-", label=f"t = {t:.2f} s")

    for ax in axes:
        ax.legend()
    plt.tight_layout()
    print(f"Maximum final difference: {np.max(np.abs(T - Trk)):.6f} K")
    return T, Trk


if __name__ == "__main__":
    steady = np.linspace(T0, TL, N + 1)
    np.testing.assert_allclose(f(0, steady), 0, atol=1e-10)
    np.testing.assert_allclose(runge_kutta_step(f, 0, steady, 1), steady)
    np.testing.assert_allclose(
        runge_kutta_step(lambda t, y: y, 0, 1.0, 0.1), np.exp(0.1), rtol=1e-7
    )
    initial = np.full(N + 1, TL, dtype=float)
    initial[0] = T0
    derivative = f(0, initial)
    np.testing.assert_allclose(derivative[[0, -1]], 0)
    np.testing.assert_allclose(derivative[1], D * (T0 - TL) / (L / N) ** 2)

    main()
    plt.show()
