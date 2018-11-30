"""Airport and flights visualization.

This module allows the visualization of an airport and its flights
on a scalable graphics view"""

import math

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QPen, QBrush, QColor

import airport
import traffic
import radarmotion

# constants
WIDTH = 800  # Initial window width (pixels)
HEIGHT = 450  # Initial window height (pixels)
AIRPORT_Z_VALUE = 0
PLOT_Z_VALUE = 1
ANIMATION_DELAY = 50  # milliseconds

# color constants (SVG color keyword names as defined by w3c: https://www.w3.org/TR/SVG/types.html#ColorKeywords)
APT_COLOR = "lightgrey"   # Airport elements color
STAND_COLOR = "darkgrey"  # stands color
POINT_COLOR = "grey"      # points (other than stands) color

# creating the brushes
STAND_BRUSH = QBrush(QColor(STAND_COLOR))
POINT_BRUSH = QBrush(QColor(POINT_COLOR))


class PanZoomView(QtWidgets.QGraphicsView):
    """An interactive view that supports Pan and Zoom functions"""

    def __init__(self, scene):
        super().__init__(scene)
        # enable anti-aliasing
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        # enable drag and drop of the view
        self.setDragMode(self.ScrollHandDrag)

    def wheelEvent(self, event):
        """Overrides method in QGraphicsView in order to zoom it when mouse scroll occurs"""
        factor = math.pow(1.001, event.angleDelta().y())
        self.zoom_view(factor)

    @QtCore.pyqtSlot(int)
    def zoom_view(self, factor):
        """Updates the zoom factor of the view"""
        self.setTransformationAnchor(self.AnchorUnderMouse)
        super().scale(factor, factor)


class RadarView(QtWidgets.QWidget):
    """An interactive view of an airport and its flights,
    with the following attributes:
    - scene: QtWidgets.QGraphicsScene (the graphic scene)
    - view: QtWidgets.QGraphicsView (the view of the scene)
    - moving_aircraft: radarmotion.AircraftItemsMotionManager  """

    # custom signal to ask inspection
    ask_inspection_signal = QtCore.pyqtSignal(traffic.Flight)
    # custom signal to tell inspector that flight list has changed
    flight_list_changed_signal = QtCore.pyqtSignal(list)

    def __init__(self, simu):
        super().__init__()
        self.simulation = simu
        self.time_increment = 1

        # Settings
        self.setWindowTitle('Airport Sim at ' + self.simulation.airport.name)
        self.resize(WIDTH, HEIGHT)

        # create components
        root_layout = QtWidgets.QVBoxLayout(self)
        self.scene = QtWidgets.QGraphicsScene()
        self.view = PanZoomView(self.scene)
        self.time_entry = QtWidgets.QLineEdit()
        toolbar = self.create_toolbar()

        # invert y axis for the view
        self.view.scale(1, -1)

        # add the airport elements to the graphic scene and then fit it in the view
        self.add_airport_items()
        self.fit_scene_in_view()

        # maintain a scene graph so as to _update_ plots
        # instead of clearing and recreating them at each update
        self.moving_aircraft = radarmotion.AircraftItemsMotionManager(self)

        # add components to the root_layout
        root_layout.addWidget(self.view)
        root_layout.addLayout(toolbar)

        # create and setup the timer
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.advance)

        # show the window
        self.show()

    def create_toolbar(self):
        # create layout for time controls and entry
        toolbar = QtWidgets.QHBoxLayout()

        def add_button(text, slot):
            """adds a button to the hbox and connects the slot"""
            button = QtWidgets.QPushButton(text)
            button.clicked.connect(slot)
            toolbar.addWidget(button)

        # lambda function allows to pass extra arguments to slots
        # added space around '-' character to avoid different look and feel
        add_button(' - ', lambda: self.view.zoom_view(0.9))
        add_button('+', lambda: self.view.zoom_view(1.1))
        toolbar.addStretch()
        add_button('<<', lambda: self.set_time_increment(-5))
        add_button(' <', lambda: self.set_time_increment(-1))
        add_button('|>', self.playpause)
        add_button(' >', lambda: self.set_time_increment(1))
        add_button('>>', lambda: self.set_time_increment(5))
        toolbar.addWidget(self.time_entry)
        self.time_entry.setInputMask("00:00:00")
        self.time_entry.editingFinished.connect(self.change_time)
        self.time_entry.setText(traffic.hms(self.simulation.t))
        toolbar.addStretch()

        # shortcuts and key bindings
        def add_shortcut(text, slot):
            """creates an application-wide key binding"""
            shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(text), self)
            shortcut.activated.connect(slot)

        add_shortcut('+', lambda: self.zoom_view(1.1))
        add_shortcut('-', lambda: self.zoom_view(1 / 1.1))
        add_shortcut(' ', self.playpause)
        add_shortcut('q', QtCore.QCoreApplication.instance().quit)

        # add a slider to change aircraft items radius
        # slider
        sld = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        sld.setMinimum(35)
        sld.setMaximum(140)
        sld.setValue(traffic.SEP)

        # labels
        lbl = QtWidgets.QLabel("Rayon")
        sliderlbl = QtWidgets.QLabel(str(traffic.SEP))
        sliderlbl.setFixedWidth(25)

        # slot
        def change_traffic_sep(val):
            traffic.SEP = val
            sliderlbl.setText(str(val))
            for item in self.moving_aircraft.aircraft_items_dict.values():
                item.update_size()

        # connect signal to slot
        sld.valueChanged.connect(change_traffic_sep)

        # add slider and labels to toolbar
        toolbar.addWidget(lbl)
        toolbar.addWidget(sld)
        toolbar.addWidget(sliderlbl)

        return toolbar

    def add_airport_items(self):
        """ Adds the airport (as a group) to the QGraphicsScene, drawn by the view"""

        airport_group = QtWidgets.QGraphicsItemGroup()
        self.scene.addItem(airport_group)
        airport_group.setZValue(AIRPORT_Z_VALUE)

        apt = self.simulation.airport

        # Taxiways
        pen = QPen(QtGui.QColor(APT_COLOR), airport.TAXIWAY_WIDTH)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        for taxiway in apt.taxiways:
            path = QtGui.QPainterPath()
            path.moveTo(taxiway.coords[0].x, taxiway.coords[0].y)
            for xy in taxiway.coords[1:]:
                path.lineTo(xy.x, xy.y)
            item = QtWidgets.QGraphicsPathItem(path, airport_group)
            item.setPen(pen)
            item.setToolTip('Taxiway ' + taxiway.taxi_name)

        # Runways
        pen = QPen(QtGui.QColor(APT_COLOR), airport.RUNWAY_WIDTH)
        for runway in apt.runways:
            (p1, p2) = runway.coords
            item = QtWidgets.QGraphicsLineItem(p1.x, p1.y, p2.x, p2.y, airport_group)
            item.setPen(pen)
            item.setToolTip('Runway ' + runway.name)

        # Named points
        pen = QPen(QtCore.Qt.transparent)
        width = 0.7 * traffic.SEP
        dw = width / 2.
        for point in apt.points:
            bounds = QtCore.QRectF(point.x - dw, point.y - dw, width, width)
            if point.type == airport.PointType.STAND:
                item = QtWidgets.QGraphicsEllipseItem(bounds, airport_group)
                item.setBrush(STAND_BRUSH)
                point_type_description = "Stand"
            else:
                item = QtWidgets.QGraphicsRectItem(bounds, airport_group)
                item.setBrush(POINT_BRUSH)
                if point.type == airport.PointType.RUNWAY_POINT:
                    point_type_description = "Runway point"
                else:
                    point_type_description = "Deicing point"
            item.setPen(pen)
            item.setToolTip(point_type_description + ' ' + point.name)

    def fit_scene_in_view(self):
        self.view.fitInView(self.view.sceneRect(), QtCore.Qt.KeepAspectRatio)

    def update_traffic(self):
        self.moving_aircraft.update_aircraft_items()
        self.time_entry.setText(traffic.hms(self.simulation.t))

    @QtCore.pyqtSlot()
    def change_time(self):
        """slot triggered when a new time is input in the text field"""
        self.simulation.set_time(traffic.time_step(self.time_entry.text()))
        self.time_entry.clearFocus()
        self.update_traffic()

    @QtCore.pyqtSlot()
    def advance(self):
        """this slot computes the new time at each time out"""
        self.simulation.increment_time(self.time_increment)
        self.update_traffic()

    @QtCore.pyqtSlot(int)
    def set_time_increment(self, dt):
        """this slot updates the speed of the replay"""
        self.time_increment = dt

    @QtCore.pyqtSlot()
    def playpause(self):
        """this slot toggles the replay using the timer as model"""
        if self.timer.isActive():
            self.timer.stop()
        else:
            self.timer.start(ANIMATION_DELAY)

    def ask_inspection(self, flight):
        self.ask_inspection_signal.emit(flight)

    def ask_flight_list_update(self, flight_list):
        self.flight_list_changed_signal.emit(flight_list)
