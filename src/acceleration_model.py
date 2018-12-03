'''
Created on 30 nov. 2018

@author: matth
'''

import geometry
import traffic

def vitesse(p1, p2):
    """Défini la vitesse avec un pas de temps de 5s et de 2 points"""
    velocity = geometry.Vector(p1, p2)
    return velocity.prod_linear(1/traffic.STEP)

def normalisation_vitesse(fichier):
    """ velocity contient les vitesses entre point_n et point_n+1 pour chaque vol
    Ainsi velocity[0,0] = vitesse(p0, p1) du 1er vol"""
    velocity = []
    with open(fichier) as flight:
        for (i,line) in enumerate(flight):
            words = line.strip().split()
            velocity.append([]) #vitesse pour le nième vol
            for point in range(2,len(words)-1):
                velocity[i].append(vitesse(point, point+1).unit())
        return velocity
    
def modele_acceleration(fichier_pente,fichier):
    """ recréer un nouveau fichier lfpg_flight.txt qui prend en compte la pente du terrain"""
    

                
                
       