"""Airport elements description.

This module allows to load an airport description file
and to access to all its elements information."""

import enum
import geometry


# Named points types
class PointType(enum.Enum):
    STAND = 1
    DEICING = 2
    RUNWAY_POINT = 3


# Wake vortex categories
class WakeVortexCategory(enum.Enum):
    LIGHT = 1
    MEDIUM = 2
    HEAVY = 3


# Runways area
RUNWAY_WIDTH = 90
# Taxiways area
TAXIWAY_WIDTH = 15


class NamedPoint(geometry.Point):
    """Named point of the airport, with the following attributes:
    - name: str (name of the point)
    - type: STAND | DEICING | RUNWAY_POINT (type of point)
    - x and y: coordinates of the point (inherited from Point)"""

    def __init__(self, name, pt_type, point):
        x, y = map(int, point.split(','))
        super().__init__(x, y)
        self.name = name
        self.type = pt_type

    def __repr__(self):
        return "<airport.Point {0}>".format(self.name)


class Taxiway(geometry.PolyLine):
    """Taxiway portion of the airport, with the following attributes:
    - taxi_name: str (name of the taxiway that it belongs to)
    - speed: int (max speed in m/s)
    - cat: LIGHT | MEDIUM | HEAVY (max allowed aircraft vortex category)
    - one_way: bool (is it a one-way portion ?)
    - coords: Point tuple (points composing the taxiway, inherited from PolyLine)"""

    def __init__(self, taxi_name, speed, cat, one_way, coords):
        super().__init__(coords)
        self.taxi_name = taxi_name
        self.speed = speed
        self.cat = cat
        self.one_way = one_way

    def __repr__(self):
        return "<airport.Line {0}>".format(self.taxi_name)


class Runway(geometry.PolyLine):
    """Runway of the airport, with the following attributes:
    - name: str (name of the runway)
    - qfu1: str (name of the first QFU)
    - qfu2: str (name of the second QFU)
    - ends: (Point, Point) (coordinates of end points of the runway, inherited from PolyLine)
    - named_points: NamedPoint tuple (named points on the runway axis)"""

    def __init__(self, name, qfu1, qfu2, ends, named_points):
        super().__init__(ends)
        self.name = name
        self.qfus = (qfu1, qfu2)
        self.named_points = named_points

    def __repr__(self):
        return "<airport.Runway {0}>".format(self.name)


class Airport:
    """Whole airport description, with the following attributes:
    - name: str (name of the airport)
    - points: Point tuple (named points of the airport)
    - taxiways: Line tuple (taxiways)
    - runways: Runway tuple (runways)"""

    def __init__(self, name, points, taxiways, runways):
        self.name = name
        self.points = points
        self.taxiways = taxiways
        self.runways = runways
        self.pt_dict = {p.name: p for p in points}
        self.qfu_dict = {r.qfus[i]: r for r in runways for i in range(2)}

    def __repr__(self):
        return "<airport.Airport {0}>".format(self.name)

    def get_point(self, name):
        return self.pt_dict[name]

    def get_runway(self, name):
        return self.qfu_dict[name]

    def get_qfu(self, name):
        return name if name in self.qfu_dict else None


# Reading an airport file

def xys_to_points(str_xy_list):
    """ xys_to_points(str list) returns Point tuple: converts x,y str list to Point tuple"""

    def xy_to_point(str_xy):
        x, y = map(int, str_xy.split(','))
        return geometry.Point(x, y)

    return tuple(xy_to_point(str_xy) for str_xy in str_xy_list)


def from_file(filename):
    """from_file(str) return Airport: reads an airport description file"""
    print("Loading airport", filename + '...')
    file = open(filename)
    categories = {'L': WakeVortexCategory.LIGHT,
                  'M': WakeVortexCategory.MEDIUM,
                  'H': WakeVortexCategory.HEAVY}
    point_types = [PointType.STAND, PointType.DEICING, PointType.RUNWAY_POINT]
    name = file.readline().strip()
    points, taxiways, runways = [], [], []
    for line in file:
        words = line.strip().split()
        try:
            if words[0] == 'P':  # Point description
                pt_type = point_types[int(words[2])]
                points.append(NamedPoint(words[1], pt_type, words[3]))
            elif words[0] == 'L':  # Taxiway description
                speed = int(words[2])
                cat = categories[words[3]]
                one_way = words[4] == 'S'
                xys = xys_to_points(words[5:])
                taxiways.append(Taxiway(words[1], speed, cat, one_way, xys))
            elif words[0] == 'R':  # Runway description
                pts = tuple(words[4].split(','))
                xys = xys_to_points(words[5:])
                runways.append(Runway(words[1], words[2], words[3], xys, pts))
        except Exception as error:
            print(error, line)
    file.close()
    print(name + ':', len(runways), "runways,", len([p for p in points if p.type == PointType.STAND]), "parking stands")
    return Airport(name, tuple(points), tuple(taxiways), tuple(runways))

# Versions originales à faire modifier en TP
# def find_point(apt, name):
#     """find_point(Airport, str) return Point | None
#     return the Point of 'apt' named 'name', or None"""
#     for point in apt.points:
#         if point.name == name:
#             return point


# def find_qfu(apt, name):
#     """find_qfu(Airport, str) return (Runway, int) | None
#     return the Runway and the index of the QFU of 'apt' named 'name', or None"""
#     for runway in apt.runways:
#         if name == runway.qfu1:
#             return (runway, 0)
#         elif name == runway.qfu2:
#             return (runway, 1)
