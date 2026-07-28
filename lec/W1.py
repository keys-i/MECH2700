"""Code written during Lecture - W1"""
from numpy import exp

# variables
x  = -0.4
n = 10
t = 1.0
ssum = 1.0

for i in range(1, n+1):
    t *= x/i
    ssum += t
    print(f'i={i:3d} t={t:12.4e} ssum={ssum:16.8e}')

print("-"*50)
print(f"the actual sum is exp({x:f})={exp(x):16.8e}")
