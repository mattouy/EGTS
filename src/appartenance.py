import numpy as np
import delaunay
import geometry as geo

DICT_TRIANGLE = delaunay.load_alti("data_files/lfpg_alti.txt")[0]

def appartenance_triangle(point, dict_triangles):
    """ test d'appartenance du point D au triangle ABC, renvoie l'indice du triangle
    il parcourt tous les triangles possibles et essaye s'il appartient ou pas"""
    for (indice_triangle, triangle) in dict_triangles.items():
        AB = geo.Vector(triangle.sommets[0],triangle.sommets[1])
        BC = geo.Vector(triangle.sommets[1],triangle.sommets[2])
        CA = geo.Vector(triangle.sommets[2],triangle.sommets[0])
        AD = geo.Vector(triangle.sommets[0],point)
        BD = geo.Vector(triangle.sommets[1],point)
        CD = geo.Vector(triangle.sommets[2],point)
        if AB.det_2D(AD) * AD.det_2D(CA) <= 0 and AB.det_2D(BD) * BD.det_2D(BC) <= 0 and CA.det_2D(CD) * CD.det_2D(BC) <= 0:
            return indice_triangle
    print(point)
    print("Le point n'appartient pas au plan")

#p = geo.Point(-658,-1194)
#triangle = appartenance_triangle(p, triangles_daulenay.simplices)
#print(triangle)

def plan_triangle(triangle):
    '''Prend un triangle ABC, renvoie les coefficients de l'Ã©quation cartÃ©sienne du triangle sous forme d'un liste'''
    AB = geo.Vector(triangle.sommets[0],triangle.sommets[1])
    AC = geo.Vector(triangle.sommets[0],triangle.sommets[2])
    n = triangle.normal() # n est le vecteur normal Ã  AB et AC
    a, b, c = n.x, n.y, n.z
    A = triangle.sommets[0] # A appartient au plan donc il doit vÃ©rifier l'Ã©quation de plan
    d = -(a * A.x + b * A.y + c * A.z)
    return [a, b, c, d]
    

#with open ("/home/valentin/Documents/pyairport/DATA/lfpg_alti.txt",'r') as alti:
#        nb_lines=0
#        for line in alti:
#            nb_lines+=1
#with open ("/home/valentin/Documents/pyairport/DATA/lfpg_alti.txt",'r') as alti:                
#        Pt_3D=np.zeros((nb_lines,3))
#        Pt_2D=np.zeros((nb_lines,2))
#        cpt_lines=0
#        for line in alti:
#            line=line.strip().split()
#            Pt_3D[cpt_lines][0]=int(line[2])
#            Pt_3D[cpt_lines][1]=int(line[3])
#            Pt_3D[cpt_lines][2]=float(line[4]) #3e coordonnÃ©e dÃ©jÃ  prÃ©sente dans alti
#            Pt_2D[cpt_lines][0]=int(line[2])
#            Pt_2D[cpt_lines][1]=int(line[3])
#            cpt_lines+=1
#print(Pt_3D)
#print(Pt_2D)


#tri=Delaunay(Pt_2D)

def add_z(coord, indice):
    """ A partir de coordonées coord et de la place du mot sur la ligne (indice),
    add_z permet d'ajouter la coordonée sur z du point sur coord """
    coord = coord.strip().split(',')
    point = geo.Point(int(coord[0]), int(coord[1]))
    tri_contenant_pt = appartenance_triangle(point, DICT_TRIANGLE) #on rÃ©cupÃ¨re ici une liste contenant les objets point correspondant aux sommets du triangle
    eq_param = plan_triangle(tri_contenant_pt)
    z = -(eq_param[0]*point.x + eq_param[1]*point.y + eq_param[3]) / eq_param[2]
    coord[indice] = coord[indice] + ',' + str(round(z,1))

def from_file(file_map): #### A renommer avec un nom plus explicite
    """ from_file(file_map) permet d'ajouter l'altitude de chaque point de l'aéroport à partir du fichier file_map (lfpg_map) et l'écrit sur un nouveau fichier new_file_airport
    ** S'il s'agit d'un point de l'aéroport ('P'):
    ** S'il s'agit d'un taxiway ('L') :
    ** S'il s'agit d'une piste ('R'): """
    file = open(file_map)
    new_file_airport = open('/home/valentin/Documents/pyairport/DATA/lfpg_3Dmap.txt', 'x') #'x' pour crÃ©ation et Ã©criture du fichier  ##anciennement f
    for line in file:
        res = '' ## qu'est ce que c'est?
        words = line.strip().split()
        try:
            if words[0] == 'P':  # Point description
                add_z(words[3], 3)
            elif words[0] == 'L':  # Taxiway description
                for i in range(len(words[5:])):
                    add_z(words[i+5], i+5)
            elif words[0] == 'R':  # Runway description
                l = len(words)
                for i in range(1,3):
                    add_z(words[l-i], l-i)
        except Exception as error:
            print(error, line)
            
        #partie écriture sur new_file_airport
        for word in words: 
            res += (word + ' ')
        new_file_airport.write(res + '\n')
    new_file_airport.close()
    file.close()

#from_file('/home/valentin/Documents/pyairport/DATA/lfpg_map.txt')
