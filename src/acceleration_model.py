'''
Created on 30 nov. 2018

@author: matth
'''

import geometry
import traffic

def vitesse(p1, p2):
    """Défini la vitesse avec un pas de temps de 5s et de 2 points"""
    velocity = geometry.Vector(p1, p2)
    return velocity.prod_linear(1/5)

def normalisation_vitesse(fichier):
    with open(fichier) as flight:
        for pos in flight :
            
        
    
    