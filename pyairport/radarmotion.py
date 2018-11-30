"""Handling graphical aircraft representation and their motions.

This modules allows the representation of aircraft (AircraftItem)
and the management of their motions (AircraftItemsMotionManager)"""
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QBrush, QColor
from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsRectItem, QGraphicsItemGroup

import airport
import traffic
import radarview

# constant colors
DEP_COLOR = "blue"  # Departure color
ARR_COLOR = "magenta"  # Arrival color
CONF_COLOR = "red"  # Conflicting aircraft color
SEL_COLOR = "green"  # color for selected aircraft

# creating the brushes
DEP_BRUSH = QBrush(QColor(DEP_COLOR))
ARR_BRUSH = QBrush(QColor(ARR_COLOR))
CONF_BRUSH = QBrush(QColor(CONF_COLOR))

PEN_WIDTH = 3
DEP_PEN = QPen(QColor(DEP_COLOR), PEN_WIDTH)
ARR_PEN = QPen(QColor(ARR_COLOR), PEN_WIDTH)
CONF_PEN = QPen(QColor(CONF_COLOR), PEN_WIDTH)
SEL_PEN = QPen(QColor(SEL_COLOR), 40)
NO_PEN = QPen(Qt.NoPen)


class AircraftItemsMotionManager:
    """Collection of aircraft items and their motion management"""

    def __init__(self, radar):
        # reference to the radar view
        self.radarView = radar
        # list of the current flights
        self.current_flights = []
        # dictionary of the corresponding aircraft items in the scene
        self.aircraft_items_dict = {}

        # populate flight list and aircraft items dictionary then create and update the corresponding aircraft items
        self.update_aircraft_items()

    def update_aircraft_items(self):
        """ updates Plots views """
        new_flights = self.radarView.simulation.current_flights
        # add new aircraft items for flights who joined
        for f in set(new_flights) - set(self.current_flights):
            item = AircraftItem(self.radarView.simulation, f, self)  # create an item
            self.radarView.scene.addItem(item)  # add it to scene
            self.aircraft_items_dict[f] = item  # add it to item dict
        # remove aircraft items for flights who left
        for f in set(self.current_flights) - set(new_flights):
            item = self.aircraft_items_dict.pop(f)  # get item from flight in the dictionary (and remove it)
            self.radarView.scene.removeItem(item)   # remove it also from scene
        # refresh current flights list
        self.current_flights = new_flights
        # get conflicting flights
        conf = self.radarView.simulation.conflicts
        # update positions of the current aircraft items
        for aircraft_number in self.aircraft_items_dict:
            aircraft = self.aircraft_items_dict[aircraft_number]
            aircraft.update_position(aircraft.flight in conf)
        # tell everyone who is listening that there is a flight list update
        self.radarView.ask_flight_list_update(self.current_flights)

    def toggle_plots_highlighting(self, flight):
        """highlight flight item and cancel highlighting on the potentially previously clicked item"""
        for item in self.aircraft_items_dict.values():
            item.toggle_highlight(flight)


class AircraftItem(QGraphicsItemGroup):
    """The view of an aircraft in the GraphicsScene"""

    def __init__(self, simu, f, motion_manager):
        """AircraftItem constructor, creates the ellipse and adds to the scene"""
        super().__init__(None)
        self.setZValue(radarview.PLOT_Z_VALUE)

        # instance variables
        self.motion_manager = motion_manager
        self.flight = f
        self.simulation = simu

        # list to store the comet elements as ellipses
        self.comete = []

        # create the tooltip
        tooltip = f.type.name + ' ' + f.call_sign + ' ' + f.qfu

        time = self.simulation.t
        for (idx, ti) in enumerate(range(time - 4, time + 1)):
            if idx < 4:
                item = QGraphicsRectItem()
                item.setPen(DEP_PEN if self.flight.type == traffic.Movement.DEP else ARR_PEN)
            else:
                item = QGraphicsEllipseItem()
                item.setBrush(DEP_BRUSH if self.flight.type == traffic.Movement.DEP else ARR_BRUSH)
                item.setToolTip(tooltip)

            self.comete.append(item)
            self.addToGroup(item)
            position = self.flight.get_position(ti)
            item.setPos(position.x, position.y)

        # compute the width of each element
        self.update_size()
        # connect to ask_inspection_signal in order to toggle_highlight this item
        self.motion_manager.radarView.ask_inspection_signal.connect(self.toggle_highlight)

    def mousePressEvent(self, event):
        """Overrides method in QGraphicsItem for interaction on the scene"""
        event.accept()
        # ask inspection of this flight
        self.motion_manager.radarView.ask_inspection(self.flight)
        # highlight this flight and cancel highlighting on the potentially previously clicked flight
        # not necessary because each plot now listens the ask_inspection_signal and highlight itself accordingly
        # self.motion_manager.toggle_plots_highlighting(self.flight)

    def update_position(self, is_conflict):
        """moves the plot in the scene"""

        time = self.simulation.t
        for (idx, ti) in enumerate(range(time - 4, time + 1)):
            item = self.comete[idx]

            if idx == 4:
                if is_conflict:
                    item.setBrush(CONF_BRUSH)
                else:
                    item.setBrush(DEP_BRUSH if self.flight.type == traffic.Movement.DEP else ARR_BRUSH)

            position = self.flight.get_position(ti)
            item.setPos(position.x, position.y)

    def update_size(self):
        """computes and updates the size of this item"""
        width = 1.5 * traffic.SEP if self.flight.cat == airport.WakeVortexCategory.HEAVY else traffic.SEP

        for idx in range(1, 5):
            item = self.comete[idx]
            wi = width * 1 / (2 - idx / 5)
            item.setRect(-wi, -wi, wi * 2, wi * 2)

    def toggle_highlight(self, flight):
        """ this function toggles highlighting of the plot """
        self.comete[4].setPen(SEL_PEN if flight == self.flight else NO_PEN)
