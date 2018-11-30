from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGraphicsView, QShortcut


class SecondView(QGraphicsView):
    """A class for the graphical user interface of the airport and traffic"""

    def __init__(self, scene):
        """ create a window with a view and control buttons """
        super(SecondView, self).__init__()
        self.setWindowTitle('second view')
        self.setScene(scene)
        self.setDragMode(QGraphicsView.ScrollHandDrag)  # allow drag and drop of the view
        self.setRenderHint(QPainter.Antialiasing)
        self.scale(0.1, -0.1)
        shortcut = QShortcut(QKeySequence('+'), self)
        shortcut.activated.connect(lambda: self.scale(1.1, 1.1))
        shortcut = QShortcut(QKeySequence('-'), self)
        shortcut.activated.connect(lambda: self.scale(1 / 1.1, 1 / 1.1))

        self.show()
