"""
    Class displaying flight information
    wraps a widget designed with Qt Designer
"""
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QListWidgetItem

import traffic
from ui_flightInspector import Ui_flightInspector


class Inspector(QWidget):
    """ Widget displaying information about a Flight """

    def __init__(self, the_radarview):
        super(Inspector, self).__init__()

        # sets up instance variables
        self.radarview = the_radarview
        self.airport = the_radarview.simulation.airport
        self.ui_flightInspector = Ui_flightInspector()

        # sets up the widget created with Qt Designer and pyuic
        self.ui_flightInspector.setupUi(self)

        # creates a flights list
        self.flights = []
        # creates filtered flights sets
        self.filtered_flights_slot = set()  # flights filtered only by slot
        self.filtered_flights_type = set()  # flights filtered only by type
        self.filtered_flights_runway = set()  # flights filtered only by runway
        self.filtered_flights_callsign = set()  # flights filtered only by a substring in callsign
        self.filtered_flights = []  # global list (intersection of the filters)

        # populates the 'filter by type' combobox
        types = ["All", "Departures", "Arrivals"]
        self.ui_flightInspector.comboBox_type.addItems(types)

        # populates the 'filter by runway' combobox
        runways = ["All", "09L-27R", "09R-27L", "08L-26R", "08R-26L"]  # todo adapter tous aéroports
        self.ui_flightInspector.comboBox_runway.addItems(runways)

        # listens newPlotsAvailable signal on radarview
        self.radarview.flight_list_changed_signal.connect(self.update_flights)
        # listens inspectionAsked signal on radarview
        self.radarview.ask_inspection_signal.connect(self.inspect)
        # listens clicks on items of the flight list in ui_flightInspector
        self.ui_flightInspector.list_flights.currentTextChanged.connect(self.ask_inspection)
        # listens changes on the 'filter by slot' group of radiobuttons
        self.ui_flightInspector.radioButton_slot.toggled.connect(self.filter_by_slot)
        self.ui_flightInspector.radioButton_noslot.toggled.connect(self.filter_by_slot)
        self.ui_flightInspector.radioButton_slotornot.toggled.connect(self.filter_by_slot)
        # listens changes on the 'filter by type' combobox
        self.ui_flightInspector.comboBox_type.currentIndexChanged.connect(self.filter_by_type)
        # listens changes on the 'filter by runway' combobox
        self.ui_flightInspector.comboBox_runway.currentIndexChanged.connect(self.filter_by_runway)
        # listens changes on the 'filter by callsign' line edit
        self.ui_flightInspector.lineEdit_callsign.textChanged.connect(self.filter_by_callsign)

        self.show()

    @pyqtSlot(list)
    def update_flights(self, flight_list):
        # populates the flight list with the current flights managed by radarview
        self.flights = flight_list
        # update the filtered flight sets according to the existing criteria and the new flight list
        # by simulating an action on all the filter widgets
        self.ui_flightInspector.radioButton_slot.toggled.emit(self.ui_flightInspector.radioButton_slot.isChecked())
        self.ui_flightInspector.radioButton_noslot.toggled.emit(self.ui_flightInspector.radioButton_noslot.isChecked())
        self.ui_flightInspector.radioButton_slotornot.toggled.emit(
            self.ui_flightInspector.radioButton_slotornot.isChecked())
        self.ui_flightInspector.comboBox_type.currentIndexChanged.emit(
            self.ui_flightInspector.comboBox_type.currentIndex())
        self.ui_flightInspector.comboBox_runway.currentIndexChanged.emit(
            self.ui_flightInspector.comboBox_runway.currentIndex())
        self.ui_flightInspector.lineEdit_callsign.textChanged.emit(self.ui_flightInspector.lineEdit_callsign.text())

    @pyqtSlot(traffic.Flight)
    def inspect(self, flight):
        # get and format info from this flight
        callsign = flight.call_sign
        flight_type = flight.type.name
        wake = flight.cat.name
        stand = flight.stand.name
        runway = flight.runway.name
        qfu = flight.qfu
        time = traffic.hms(flight.start_t)
        slot = 'No slot' if flight.slot is None else traffic.hms(flight.slot)
        # update the inspector
        self.ui_flightInspector.label_callsign.setText(callsign)
        self.ui_flightInspector.label_movement_type.setText(flight_type)
        self.ui_flightInspector.label_wake.setText(wake)
        self.ui_flightInspector.label_stand.setText(stand)
        self.ui_flightInspector.label_runway.setText(runway)
        self.ui_flightInspector.label_qfu.setText(qfu)
        self.ui_flightInspector.label_time.setText(time)
        self.ui_flightInspector.label_slot.setText(slot)

    @pyqtSlot(str)
    def ask_inspection(self, current_text):
        for flight in self.filtered_flights:
            if flight.call_sign == current_text:
                self.radarview.ask_inspection_signal.emit(flight)
                break

    def filter_flights(self):
        filtered_set = self.filtered_flights_slot.intersection(
            self.filtered_flights_type,
            self.filtered_flights_runway,
            self.filtered_flights_callsign)
        filtered_list = list(filtered_set)
        self.filtered_flights = filtered_list

    def display_filtered_flights(self):
        current_callsigns = set([self.ui_flightInspector.list_flights.item(i).text()
                                 for i in range(self.ui_flightInspector.list_flights.count())])
        new_callsigns = set([my_flight.call_sign for my_flight in self.filtered_flights])
        # removes the flights who left
        for callsign in current_callsigns - new_callsigns:
            for i in range(self.ui_flightInspector.list_flights.count()):
                if self.ui_flightInspector.list_flights.item(i).text() == callsign:
                    self.ui_flightInspector.list_flights.takeItem(i)
                    break
        # adds the new flights
        for callsign in new_callsigns - current_callsigns:
            item = QListWidgetItem(self.ui_flightInspector.list_flights)
            item.setText(callsign)
            # self.ui_flightInspector.list_flights.sortItems()  # if really need to sort but changing list so focus loss

    @pyqtSlot()
    def filter_by_slot(self):
        if self.sender().isChecked():
            filtered = []
            if self.sender() == self.ui_flightInspector.radioButton_slot:
                filtered = [flight for flight in self.flights if flight.slot is not None]
            elif self.sender() == self.ui_flightInspector.radioButton_noslot:
                filtered = [flight for flight in self.flights if flight.slot is None]
            elif self.sender() == self.ui_flightInspector.radioButton_slotornot:
                filtered = self.flights
            self.filtered_flights_slot = set(filtered)
            self.filter_flights()
            self.display_filtered_flights()

    @pyqtSlot(int)
    def filter_by_type(self, i):
        if i == 1:
            filtered = [flight for flight in self.flights if flight.type == traffic.Movement.DEP]
        elif i == 2:
            filtered = [flight for flight in self.flights if flight.type == traffic.Movement.ARR]
        else:
            filtered = self.flights
        self.filtered_flights_type = set(filtered)
        self.filter_flights()
        self.display_filtered_flights()

    @pyqtSlot(int)
    def filter_by_runway(self, i):
        if i == 1:
            filtered = [flight
                        for flight in self.flights
                        if flight.runway.name == "09L-27R"]
        elif i == 2:
            filtered = [flight
                        for flight in self.flights
                        if flight.runway.name == "09R-27L"]
        elif i == 3:
            filtered = [flight
                        for flight in self.flights
                        if flight.runway.name == "08L-26R"]
        elif i == 4:
            filtered = [flight
                        for flight in self.flights
                        if flight.runway.name == "08R-26L"]
        else:
            filtered = self.flights
        self.filtered_flights_runway = set(filtered)
        self.filter_flights()
        self.display_filtered_flights()

    @pyqtSlot(str)
    def filter_by_callsign(self, text):
        filtered = [flight for flight in self.flights if text.upper() in flight.call_sign]
        self.filtered_flights_callsign = set(filtered)
        self.filter_flights()
        self.display_filtered_flights()
