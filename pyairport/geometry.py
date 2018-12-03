"""Geometry classes and utilities."""


class Point(object):
    """Meters coordinates, with attributes x, y: int"""

    def __init__(self, x, y, z=0):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return "({0.x}, {0.y})".format(self)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __rmul__(self, k):
        return Point(k * self.x, k * self.y)

    def __abs__(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def sca(self, other):
        """sca(Point) return float
        returns the scalar product between self and other"""
        return self.x * other.x + self.y * other.y

    def det(self, other):
        """det(Point) return float
        returns the determinant between self and other"""
        return self.x * other.y - self.y * other.x

    def distance(self, other):
        return abs(self - other)

    def seg_dist(self, a, b):
        ab, ap, bp = b - a, self - a, self - b
        if ab.sca(ap) <= 0:
            return abs(ap)
        elif ab.sca(bp) >= 0:
            return abs(bp)
        else:
            return abs(ab.det(ap)) / abs(ap)
        
        
class Vector:
    """Vector object"""
    def __init__(self, point1, point2):
        self.x = point2.x - point1.x
        self.y = point2.y - point1.y
        self.z = point2.z - point1.z
        
    def __repr__(self):
        return "({0.x}, {0.y}, {0.z})".format(self)
    
    def sca(self, other):
        """sca(Vector) return float
        returns the scalar product between self and other"""
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def prod_linear(self, reel):
        self.x = reel*self.x
        self.y = reel*self.y
        self.z = reel.self.z
        return(self)

    def vector_prod(self, other):
        """vector_prod() renvoie le produit vectoriel"""
        x_prod = self.y*other.z - other.y*self.z
        y_prod = self.z*other.x - other.z*self.x
        z_prod = self.x*other.y - other.x*self.y
        return Vector(Point(0,0,0), Point(x_prod, y_prod, z_prod))
    
    def norm(self):
        """norm of the vector"""
        return((self.x**2 + self.y**2 + self.z**2)**0.5)
        
    def unit(self):
        """normalise le vecteur"""
        self.x = self.x/self.norm()
        self.y = self.y/self.norm()
        self.z = self.z/self.norm()
        return(self)
        
        

class PolyLine(object):
    def __init__(self, coords):
        self.length = sum(pi.distance(coords[i - 1])
                          for i, pi in enumerate(coords[1:]))
        self.coords = coords

    def __repr__(self):
        return "<geometry.Line {}>".format(len(self))

    def __str__(self):
        points = ', '.join(str(p) for p in self.coords)
        return 'PolyLine {}m: ({})'.format(self.length, points)

    def __len__(self):
        return len(self.coords)
