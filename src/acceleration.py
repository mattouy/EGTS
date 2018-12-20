'''
Created on 30 nov. 2018

@author: matth
'''

import geometry
import traffic
import math
import random as rd

TIRERADIUS = 0.56 #en mètre
MAXEGTSTORQUE = 16000 #N.m
EGTSPOWER = 49000 #VA
BREAKAWAYRESISTANCE = 0.01 #daN/kg
ROLLINGRESISTANCE = 0.007 #daN/kg
AEROCOEF = 1.032
TIMESTEP = 4.1 #s
MASS_A319_DEP = 63000 #kg
MASS_A319_ARR = 57000 #kg
MASS_A320_DEP = 69000 #kg
MASS_A320_ARR = 62000 #kg
MASS_A321_DEP = 81000 #kg
MASS_A321_ARR = 73000 #kg
VMAX_DROIT = 10 #m/s
VMAX_COURBE = 3 #m/s

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
    
def nextspeedegts(mass, slope, speed):
    """calcul la prochaine vitesse pour un avion EGTS"""
    slope_torque = - mass * 9.81 * math.sin(math.atan(slope/100)) * TIRERADIUS
    if speed < 1:
        res_torque = - mass * BREAKAWAYRESISTANCE * 10 * TIRERADIUS
        egts_torque = MAXEGTSTORQUE
    else:
        res_torque = - mass * ROLLINGRESISTANCE * 10 * TIRERADIUS
        egts_torque = min(MAXEGTSTORQUE,EGTSPOWER/(speed/TIRERADIUS))
    aero_torque = AEROCOEF * speed**2
    torque = egts_torque + slope_torque + res_torque + aero_torque      
    acc = max(0, torque/TIRERADIUS/mass)
    return min(speed + TIMESTEP * acc, VMAX_DROIT)#choisir entre courbe et droit mais comment? faut-il détecter la courbe?

def nextspeedclassic(speed):
    return min(speed+0.9, VMAX_DROIT)#choisir entre courbe et droit
            
def selection_flight(fichier,quota):
    """choisi les vols egts sur un fichier classique et ajoute le type de motorisation (EGTS ou classique)"""
    categories = {0 :'C', 1: "E"} # C = Classic, E = EGTS
    def random_type(quota):
        return categories[np.random.binomial(1,quota)]

    file = open(fichier)
    f = open('/home/victor/Bureau/EGTS-master/data_files/lfpg_3Dflights.txt', 'x')
    res = ''
    for line in file:
        words = line.strip().split()
        if words[2] == 'M':
            words = words[:3] + random_type(quota) + words[3:] #Ajout 'EGTS' dans le fichier flight 
        else:
            words = words[:3] + ['C'] + words[3:]
        for word in words:
            res += (word +' ')
        f.write(res + '\n')
    f.close()
    file.close()
    
    
def modele_acceleration(fichier_pente, quota):
    """ recréer un nouveau fichier lfpg_flight.txt qui prend en compte la pente du terrain"""
    callsign_egts = selection_flight(fichier_pente, quota)
    with open(fichier_pente) as flight:
        for line in flight:
            words = line.strip.slipt()
            speed = 0
            if words[0] == 'DEP':
                mass = MASS_A320_DEP
            elif words[0] == 'ARR':
                mass = MASS_A320_ARR

            if words[1] in callsign_egts:
                """Si le vol est EGTS, lui appliquer le modèle d'accélération"""
                for point in range(9,len(words)):
                    slope = words[point][2] #je suppose que point chaque point c'est un tuple de la forme (x,y,pente)
                    next_speed = nextspeedegts(mass, slope, speed)
                    
                    
            else:
                """lui appliquer le modèle normal (si celui n'a pas été déjà calculer dans le fichier qu'Ahmet aurait fait (?))"""
                
                
"""Faut-il extraire les vols EGTS et afficher seulement ces vols ou les mélanger avec les autres vols avec un fichier normal qui contient
vols normaux et vols egts?
Choisir au le modèle de l'avion parmi la famille A320 pour les différentes masses."""

    


                
                
