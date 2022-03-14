import numpy as np

M = np.array([x for x in range(5, 21)])
print(str(M) + "\n")

M = M.reshape(4,4)
print(str(M) + "\n")

M[1:3 , 1:3] = 0
print(str(M) + "\n")

M = M@M
print(str(M) + "\n")

S = np.sqrt(np.power(M[0], 2).sum())
print(S)
