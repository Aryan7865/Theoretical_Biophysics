# -*- coding: utf-8 -*-

Consider the given data on the trajectory of Michaelis-Menten nonlinear ODE system over the
combination of phase-spaces in (X, P, V, S, E). Compute the most probable values of eta, kappa, and
epsilon along the arclength in the respective phase-spaces for the given start and end times.
Note: scan be parameter in the range (0.1, 1.5) with an increment of 0.1
.


initial conditions: {P,X,V,S,E} = {0,0,0,1,1} at tau = 0, Euler delta tau = 0.1 \\
ARC LENGTH START tau = 0.2 ATCLENGTH END tau = 4.8 \\
P,V
"""

import numpy as np
import itertools
import matplotlib.pyplot as plt

"""Put your dataset here."""

PP = [0.0, 0.035, 0.0632625, 0.0910443, 0.118258, 0.144906, 0.170989, 0.196507, 0.221461, 0.245853, 0.269684, 0.292957, 0.315675, 0.337841, 0.35946, 0.380535, 0.40107, 0.421072, 0.440545, 0.459496, 0.47793, 0.495855, 0.513277, 0.530204, 0.546642, 0.5626, 0.578086, 0.593108, 0.607675, 0.621795, 0.635477, 0.648729, 0.661562, 0.673984, 0.686005, 0.697633, 0.708878, 0.71975, 0.730257, 0.740409, 0.750215, 0.759684, 0.768826, 0.77765, 0.786164, 0.794378, 0.802299, 0.809938, 0.817302, 0.824399, 0.831238, 0.837828, 0.844175, 0.850288, 0.856174, 0.861841, 0.867295, 0.872545, 0.877597, 0.882457, 0.887132, 0.89163, 0.895955, 0.900113, 0.904112, 0.907956, 0.911651, 0.915203, 0.918616, 0.921896, 0.925047, 0.928075, 0.930983, 0.933777, 0.93646, 0.939037, 0.941512, 0.943889, 0.946171, 0.948362]
V = [0.0, 0.35, 0.282625, 0.277818, 0.272137, 0.266482, 0.260828, 0.255179, 0.24954, 0.243916, 0.238312, 0.232732, 0.227181, 0.221664, 0.216184, 0.210747, 0.205357, 0.200017, 0.194733, 0.189507, 0.184344, 0.179247, 0.174219, 0.169264, 0.164384, 0.159582, 0.15486, 0.150221, 0.145667, 0.141199, 0.136819, 0.132529, 0.128329, 0.124221, 0.120205, 0.116282, 0.112452, 0.108714, 0.105071, 0.10152, 0.0980612, 0.0946949, 0.0914199, 0.0882356, 0.085141, 0.0821351, 0.0792168, 0.0763848, 0.0736379, 0.0709747, 0.0683936, 0.0658934, 0.0634722, 0.0611287, 0.0588611, 0.0566677, 0.054547, 0.052497, 0.0505163, 0.0486029, 0.0467551, 0.0449714, 0.0432498, 0.0415887, 0.0399863, 0.0384411, 0.0369512, 0.0355151, 0.0341311, 0.0327977, 0.0315132, 0.0302761, 0.0290848, 0.0279379, 0.026834, 0.0257715, 0.0247492, 0.0237655, 0.0228194, 0.0219093]

t = [i/10 for i in range(80)]

"""Change the plot variable based on your data."""

plt.plot(P, V)
plt.xlabel("P")
plt.ylabel("V")
plt.title("Trajectory of Michaelis-Menten System")
plt.show()

a = [i/10 for i in range(1, 16)]
combinations = list(itertools.product(a, repeat=3))

def michaelis_menten_kinetics(eta,kappa,eps,delt,tott):
    X0,P0,tau = 0,0,0
    trs = int(tott/delt)
    out = np.zeros((trs,6))

    Xtau,Ptau,Stau,Etau,Vtau = X0,P0,1.0,1.0,0
    i = 0

    while (i < trs):
        out[i,0:6] = [tau,Xtau,Ptau,Stau,Etau,Vtau]
        Xtau = Xtau + delt * ((1-Xtau)*(1-eps*Xtau-Ptau)-(eta+kappa)*Xtau) / eta
        Ptau = Ptau + delt*eps*Xtau
        Etau = 1-Xtau
        Stau = 1-eps*Xtau-Ptau
        Vtau = eps*Xtau
        tau = tau + delt
        i = i+1

    dxdt = np.diff(out[:,1])/np.diff(out[:,0])
    return (out,dxdt)

"""You'll need to change the j in res[i, j] based on your dataset \\
j = 1 for X \\
j = 2 for P \\
j = 3 for S \\
j = 4 for E \\
j = 5 for V \\
"""

def arclength(start, end, res):
  arclength = 0
  for i in range(start, end):
    arclength += np.sqrt((res[i,2] - res[i+1,2])**2 + (res[i,5]-res[i+1,5])**2) # change here - VP is 2,5
  return arclength

"""You'll need to change the j in res[i, j] based on your dataset \\
j = 1 for X \\
j = 2 for P \\
j = 3 for S \\
j = 4 for E \\
j = 5 for V \\
"""

error = []
delt = 0.1
tott = 8
for i in combinations:
  eta, kappa, eps = i
  res,dxdt = michaelis_menten_kinetics(eta,kappa,eps,delt,tott)
  index = [i for i in range(80)]
  err = 0
  err = np.float128(err)
  for i in index:
    err += (res[i, 2] - P[i])**2 # here change
  error.append(err)

"""This is your Eta, Kappa, Eps values"""

combinations[error.index(min(error))]

"""This is the error value for the above parameters"""

min(error)

"""Change the start and end values based on given dataset. \\
Just plotting and seeing if the parameter look proper.
"""

eta, kappa, eps = combinations[error.index(min(error))]
start = 2
end = 48
res,dxdt = michaelis_menten_kinetics(eta,kappa,eps,delt,tott)
arclen = arclength(start, end,res)
fig1, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.plot(P, V, c='g')
ax2.plot(res[:,2], res[:, 5],  c='r')
ax2.set_ylim(ax1.get_ylim())
plt.show()
fig1, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.plot(P, t, c='g')
ax2.plot(res[:,2], t,  c='r')
ax2.set_ylim(ax1.get_ylim())
plt.show()
fig1, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.plot(V, t, c='g')
ax2.plot(res[:,5], t,  c='r')
ax2.set_ylim(ax1.get_ylim())
plt.show()

"""This is your arclength."""

arclen
