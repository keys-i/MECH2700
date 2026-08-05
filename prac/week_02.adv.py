"""
A correlation for the thermal conductivity k of Titanium (in W/m/K) as a
function of temperature
"""

from math import exp

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({"text.usetex": True, "font.family": "Helvetica"})

# -- variables --
A = 1.5531
B = 0.8703
C = -12.4882 * pow(10, -4)
D = 143.6


# -- functs --
thermal_conductivity = lambda T: A * pow(T, B) * exp(C * T) * exp(D / T)


def lagrange_basis_function(j, x, xs):
    result = 1.0
    for i, xi in enumerate(xs):
        if i != j:
            result *= (x - xi) / (xs[j] - xi)
    return result


interpolate = lambda xs, ys, x: sum(
    ys[j] * lagrange_basis_function(j, x, xs) for j in range(len(xs))
)


def plot_thermal_conductivity():
    Tsf = np.linspace(100.0, 900.0, 100)
    k_interp = [interpolate(Ts, ks, T) for T in Tsf]
    plt.plot(Tsf, k_interp, label="interpolated")
    plt.plot(Ts, ks, "o", label="data")
    plt.xlabel("Temperature ($K$)")
    plt.ylabel(r"Thermal Conductivity ($\frac{W}{mK}$)")
    plt.title("Thermal Conductivity of Titanium")
    plt.legend()
    plt.show()


Ts = [100.0, 200.0, 300.0, 500.0, 700.0, 900.0]
ks = list(map(thermal_conductivity, Ts))

for t in Ts:
    print(f"Thermal Conductivity at {t}K = {thermal_conductivity(t):.2f} W/m/K")

print(
    f"\nInterpolated Conductivity at 250K = "
    f"{interpolate(Ts, ks, 250.0):.2f} W/m/K"
)
print(f"Exact Conductivity at 250K = {thermal_conductivity(250.0):.2f} W/m/K\n")

plot_thermal_conductivity()
