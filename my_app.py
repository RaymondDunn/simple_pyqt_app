from ctypes import alignment
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
from thirdparty import fastsmooth
import os
import pickle
import json
import tifffile as tf

# single-window app
class MyApp:
    
    # sometimes, putting gui code in __init__ creates problems (e.g. serialization w/r/t subprocesses)
    def __init__(self):
        self.initialize_display()

    def intialize_display(self):
        
        # make app, we do it this way in case an instance of the app is
        # already running (like if using in jupyter notebook)
        self.app = QtCore.QCoreApplication.instance()
        if self.app is None:
            self.app = QtGui.QApplication([])

        # it should exit on close per  https://stackoverflow.com/questions/57408620/cant-kill-pyqt-window-after-closing-it-which-requires-me-to-restart-the-kernal/58537032#58537032
        self.app.setQuitOnLastWindowClosed(True)

        # app has a main window
        self.window = QtGui.QWidget()
        self.window.setWindowTitle(
            "Neural State Classifier: {}".format(self.dc.fname_root)
        )
        self.window.resize(1400, 800)

        # window has a grid layout (easy to add widgets/items to)
        self.window_grid = QtGui.QGridLayout()

        # add other grids/widgets into window
        self.plot_graphics_widget = pg.GraphicsLayoutWidget()
        self.command_panel_grid = QtGui.QGridLayout()


        ##################################
        # build gui elements here



        # buttons (and callbacks)
        # slider

        ##################################

        # assemble hierarchical containers
        # add plot graphics widget and command panel to window grid
        self.window_grid.addWidget(self.plot_graphics_widget)
        self.window_grid.addItem(self.command_panel_grid)

        # set window layout to grid
        self.window.setLayout(self.window_grid)

        # show the window
        self.window.show()


# standalone testing
if __name__ == "__main__":
    