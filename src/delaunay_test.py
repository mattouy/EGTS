import numpy as np

file = open("/Users/matth/eclipse-workspace/EGTS/DATA/lfpg_alti.txt")
points = []
for line in file:
    words = line.strip().split()
    print(words)
    points.append([words[2], words[3]])
points1 = np.array(points)
file.close()

from scipy.spatial import Delaunay
tri = Delaunay(points1)


import matplotlib.pyplot as plt
plt.triplot(points1[:,0], points1[:,1], tri.simplices)

plt.show()



