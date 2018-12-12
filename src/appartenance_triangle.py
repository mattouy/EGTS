import geometry as geo
from scipy.spatial import Delaunay
import numpy as np

file = open("/Users/matth/eclipse-workspace/EGTS/DATA/lfpg_alti.txt")
points = []
coord = []
for line in file:
        words = line.strip().split()
        points.append([words[2], words[3]])
        coord.append(geo.Point(float(words[2]),float(words[3]),float(words[4])))

points1 = np.array(points)

file.close()

tri = Delaunay(points1)

def sign(nb):
    if nb > 0:
        return(True)
    elif nb < 0:
        return(False)
    else:
        pass



def appartenance(p):
    for k in tri.simplices:
        AB = geo.Vector(coord[k[0]],coord[k[1]])
        BC = geo.Vector(coord[k[1]],coord[k[2]])
        CA = geo.Vector(coord[k[2]],coord[k[0]])
        AD = geo.Vector(coord[k[0]],p)
        BD = geo.Vector(coord[k[1]],p)
        CD = geo.Vector(coord[k[2]],p)
        if AD.det_2D(AB) == 0:
            if sign(BD.det_2D(BC)) == sign(CD.det_2D(CA)):
                    return(k)
        elif BD.det_2D(BC) == 0:
            if sign(AD.det_2D(AB)) == sign(CD.det_2D(CA)):
                return(k)
        elif CD.det_2D(CA) == 0:
            if sign(BD.det_2D(BC)) == sign(AD.det_2D(AB)):
                return (k)
        elif sign(BD.det_2D(BC)) == sign(CD.det_2D(CA)) == sign(AD.det_2D(AB)):
            return (k)
    return ("ce point n'appartient a aucun triangle")

# print(coord[3],coord[30],coord[0])
# p = geo.Point(-1000,0)
# triangle = appartenance(p)
# print(triangle)






# http: // www.jaicompris.com / lycee / math / espace / droite - plan.php


