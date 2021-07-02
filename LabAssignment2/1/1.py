import numpy as np
# 1-A
M = np.arange(2, 27, 1)
print(M);

# 1-B
M = M.reshape(5, 5);
print(M);

# 1-C
for i in range(1, 4):
    for j in range(1, 4):
        M[i, j] = 0
print(M)

# 1-D
M = M @ M
print(M)

# 1-E
rowSum = 0
for i in range(0, 5):
    rowSum += M[0, i]*M[0, i]

print(np.sqrt(rowSum))
