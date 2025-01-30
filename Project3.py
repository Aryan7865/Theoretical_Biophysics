# -*- coding: utf-8 -*-


import numpy as np

inda = np.array([[6, 4, 3], [5,3,4], [4,4,3], [3,5,4], [2,4,5], [3,5,6],
                 [2,6,5], [1,5,6], [0,4,5], [1,3,4], [0,2,3], [1,1,2],
                 [2,2,1], [3,1,2], [4,2,1], [5,3,0], [4,4,1], [3,5,0],
                 [2,4,1], [1,3,0], [0,2,1], [1,3,2], [2,2,3], [3,1,4],
                 [4,2,5]])

indb = np.array([[2,4,3], [3,5,2], [4, 6,1], [5,5,0], [4,4,1], [5,3,2],
                 [6, 4,1], [5, 3,0], [6, 2,1], [5,1,2], [4,2,1], [3,1,0],
                 [2,2,1], [1,3,0], [0,2,1], [1,1,2], [2,2,3], [3,1,4],
                 [4,2,5], [3,3,4], [4,4,5], [3,3,6], [2,4,5], [1,3,6],
                 [2,2,5]])

comp = 6
gymatrix = indb


tr = 0
cr = 0
incr = 0
num = 0


data = []


for i in range(len(inda)):
    for j in range(len(indb)):
        if np.array_equal(inda[i], indb[j]):
            ra = i % comp
            rb = j % comp
            qa = i // comp
            qb = j // comp

            data.append([i, j, qa, qb, ra, rb])
            num += 1

            # Count the types of contacts
            if qa == qb and ra == rb:
                cr += 1
            elif qa != qb and ra == rb:
                tr += 1
            else:
                incr += 1

gysum = 0
n = len(gymatrix)
for i in range(n - 1):
    for j in range(i + 1, n):
        gysum += ((gymatrix[i, 0] - gymatrix[j, 0]) ** 2 +
                   (gymatrix[i, 1] - gymatrix[j, 1]) ** 2 +
                   (gymatrix[i, 2] - gymatrix[j, 2]) ** 2)


rad_gyr = np.sqrt(gysum) / 26


print("Correct contact:", cr)
print("Trapped contact:", tr)
print("Incorrect contact:", incr)
print("Radius of Gyration:", rad_gyr)
