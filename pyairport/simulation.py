"""Interactive airport simulation.

This module defines the interactions with the simulation"""

import traffic

SHORTCUTS = """Shortcuts:
n: next time step
b: last time step
q: close window"""


class Simulation:
    """The simulation state, with the following attributes:
    - airport: airport.Airport (the airport)
    - flights: traffic.Flight list (the traffic)
    - t: int (current time step)"""

    def __init__(self, apt, flights, init_time=traffic.DAY // 2):
        self.airport = apt
        self.all_flights = flights
        self.conflicts = {}
        self.t = init_time
        self.current_flights = traffic.select(self.all_flights, self.t)

    def set_time(self, t):
        """set_time(int): set the current time to 't'"""
        self.t = t
        self.current_flights = traffic.select(self.all_flights, self.t)
        conflicts = traffic.detect_in(self.current_flights, self.t, self.t + traffic.DT)
        #        if len(self.conflicts) < len(conflicts):
        #            self.timer.stop()
        self.conflicts = conflicts

    def increment_time(self, dt):
        """increment_time(int): increases the current time step by 'dt'
        (dt might be negative)"""
        self.set_time(self.t + dt)
