import numpy as np
from scipy.spatial import Delaunay
import sys
sys.path.insert(0, "./airport") # On utilise le module geometry de airport
import geometry as geo

class Triangle():
    """A, B et C sont des objets Point et représentent les sommets du triangle
        indice est le numéro du triangle à parir de l'objet Delaunay"""
    def __init__(self, A, B, C):
        self.sommets = (A, B, C)
        self.normal_vector = None

    def __repr__(self):
        return self.sommets

    def normal(self):
        """ renvoie le vercteur normal unitaire du triangle"""
        ab = geo.Vector(self.sommets[0], self.sommets[1])
        ac = geo.Vector(self.sommets[0], self.sommets[2])
        return ab.vector_prod(ac).unit()
        

def load_alti(filename):
    """fichier d'altitude JBG, et revoie un dictionnaire d'objet Triangle avec comme clef leur indice ranges selon Delaunay"""
    alti_points = []
    dict_triangles = {} 
    points = []

    with open(filename) as file:
        for line in file:
            words = line.strip().split()
            points.append([int(words[2]), int(words[3])])
            alti_points.append(geo.Point(int(words[2]), int(words[3]), float(words[4])))

    for (i, triplet_sommets) in enumerate(Delaunay(points).simplices): # Delaunay.simplices est une liste de triplets d'indice de sommets
        dict_triangles[i] = Triangle(alti_points[triplet_sommets[0]], alti_points[triplet_sommets[1]], alti_points[triplet_sommets[2]])

    return dict_triangles, alti_points ######### enlever alti_points si inutile



