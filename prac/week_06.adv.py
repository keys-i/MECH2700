"""
Jacobi iteration for the temperature distribution in a heated support beam
"""

import numpy as np

# -- consts --
S = 4e5 * 0.1**2 / 170

M = np.array(
    (
        (0, 0.5, 0, (300 + S) / 2),
        (0.5, 0, 0.5, S / 2),
        (0, 0.5, 0, (750 + S) / 2),
        (0, 0, 0, 1),
    )
)


# -- functs --
_step = lambda Ts: (M @ np.r_[Ts, 1])[:3]


def update_temperatures(Ts: np.ndarray) -> np.ndarray:
    return _step(Ts)


def jacobi_iteration(
    initial_guess: np.ndarray,
    n_iters: int,
):
    return (np.linalg.matrix_power(M, n_iters) @ np.r_[initial_guess, 1])[:3]


def main():
    initial_guess = np.array(
        (337.5, 375.0, 412.5),
        dtype=np.float64,
    )

    return jacobi_iteration(initial_guess, 5)


if __name__ == "__main__":
    print(main())
