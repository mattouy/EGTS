'''
Created on 30 nov. 2018

@author: matth
'''

import geometry
import traffic
import math
from numpy import roll
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
    return(speed + TIMESTEP * acc)

def nextspeedclassic(speed):
    return(speed+0.9)
            
def selection_flight(fichier,quota):
    """choisi les vols egts sur un fichier classique et renvoie le callsign de ceux choisi"""
    nb_egts = 0
    callsign_egts = []
    with open(fichier) as flight:
        while nb_egts != quota:
            for (i,line) in enumerate(flight):
                words = line.strip.slipt()
                hasard = rd.randint(0,1)
                if words[2] == 'M' and hasard == 1:
                    callsign_egts.append(words[1],i)
                    nb_egts += 1
        return callsign_egts
    
#def modele_acceleration(fichier_pente):
    """ recréer un nouveau fichier lfpg_flight.txt qui prend en compte la pente du terrain"""
    
    


                
                