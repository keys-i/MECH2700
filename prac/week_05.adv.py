"""
Hydrocarbon-combustion Linear system using my implementation
"""


def hydrocarbon_combustion():
    A = [
        [2.0, -1.0, 0.0],
        [8.0, -1.0, -2.0],
        [0.0, 4.0, -1.0],
    ]
    b = [4.0, 0.0, 0.0]
    return A, b


def my_det(A):
    n = len(A)

    if n == 3:
        if len(A[0]) != 3 or len(A[1]) != 3 or len(A[2]) != 3:
            raise ValueError("A must be a non-empty square matrix.")

        a, b, c = A[0]
        d, e, f = A[1]
        g, h, i = A[2]
        return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)

    if n == 2:
        if len(A[0]) != 2 or len(A[1]) != 2:
            raise ValueError("A must be a non-empty square matrix.")

        a, b = A[0]
        c, d = A[1]
        return a * d - b * c

    if n == 1:
        if len(A[0]) != 1:
            raise ValueError("A must be a non-empty square matrix.")
        return A[0][0]

    if n == 0 or any(len(row) != n for row in A):
        raise ValueError("A must be a non-empty square matrix.")

    matrix = [list(map(float, row)) for row in A]
    determinant = 1.0

    for column in range(n):
        pivot_row = column
        pivot_size = abs(matrix[column][column])

        for row in range(column + 1, n):
            candidate = abs(matrix[row][column])
            if candidate > pivot_size:
                pivot_row = row
                pivot_size = candidate

        if pivot_size == 0.0:
            return 0.0

        if pivot_row != column:
            matrix[column], matrix[pivot_row] = (
                matrix[pivot_row],
                matrix[column],
            )
            determinant = -determinant

        pivot_values = matrix[column]
        pivot = pivot_values[column]
        determinant *= pivot

        for row in range(column + 1, n):
            row_values = matrix[row]
            factor = row_values[column] / pivot
            row_values[column] = 0.0

            for entry in range(column + 1, n):
                row_values[entry] -= factor * pivot_values[entry]

    return determinant


def determine_coefficients(A, b):
    n = len(A)

    if len(b) != n:
        raise ValueError("b must have the same number of entries as A.")

    if n == 3:
        if len(A[0]) != 3 or len(A[1]) != 3 or len(A[2]) != 3:
            raise ValueError("A must be a non-empty square matrix.")

        a, c, d = A[0]
        e, f, g = A[1]
        h, i, j = A[2]
        p, q, r = b

        fj_gi = f * j - g * i
        ej_gh = e * j - g * h
        ei_fh = e * i - f * h
        determinant = a * fj_gi - c * ej_gh + d * ei_fh

        if determinant == 0:
            raise ValueError("A is singular and has no unique solution.")

        qj_gr = q * j - g * r
        qi_fr = q * i - f * r
        er_qh = e * r - q * h

        return [
            (p * fj_gi - c * qj_gr + d * qi_fr) / determinant,
            (a * qj_gr - p * ej_gh + d * er_qh) / determinant,
            (a * (f * r - q * i) - c * er_qh + p * ei_fh) / determinant,
        ]

    if n == 2:
        if len(A[0]) != 2 or len(A[1]) != 2:
            raise ValueError("A must be a non-empty square matrix.")

        a, c = A[0]
        d, e = A[1]
        determinant = a * e - c * d

        if determinant == 0:
            raise ValueError("A is singular and has no unique solution.")

        p, q = b
        return [
            (p * e - c * q) / determinant,
            (a * q - p * d) / determinant,
        ]

    if n == 1:
        if len(A[0]) != 1:
            raise ValueError("A must be a non-empty square matrix.")

        pivot = A[0][0]
        if pivot == 0:
            raise ValueError("A is singular and has no unique solution.")
        return [b[0] / pivot]

    if n == 0 or any(len(row) != n for row in A):
        raise ValueError("A must be a non-empty square matrix.")

    matrix = [list(map(float, A[row])) + [float(b[row])] for row in range(n)]

    for column in range(n):
        pivot_row = column
        pivot_size = abs(matrix[column][column])

        for row in range(column + 1, n):
            candidate = abs(matrix[row][column])
            if candidate > pivot_size:
                pivot_row = row
                pivot_size = candidate

        if pivot_size == 0.0:
            raise ValueError("A is singular and has no unique solution.")

        if pivot_row != column:
            matrix[column], matrix[pivot_row] = (
                matrix[pivot_row],
                matrix[column],
            )

        pivot_values = matrix[column]
        pivot = pivot_values[column]

        for row in range(column + 1, n):
            row_values = matrix[row]
            factor = row_values[column] / pivot
            row_values[column] = 0.0

            for entry in range(column + 1, n + 1):
                row_values[entry] -= factor * pivot_values[entry]

    coefficients = [0.0] * n

    for row in range(n - 1, -1, -1):
        row_values = matrix[row]
        total = row_values[n]

        for column in range(row + 1, n):
            total -= row_values[column] * coefficients[column]

        coefficients[row] = total / row_values[row]

    return coefficients


A, b = hydrocarbon_combustion()
x = determine_coefficients(A, b)
number = lambda value: f"{value:g}{'.' if value % 1 == 0 else ''}"
fmt = lambda values: f"[{', '.join(map(number, values))}]"

print(f"""
A = {chr(10).join(fmt(row) for row in A)}
b = {fmt(b)}
det(A) = {my_det(A):g}
x = {fmt(x)}
""")
