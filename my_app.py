# from pyqtgraph.Qt import QtGui, QtCore
# from PyQt5 import QtGui, QtCore
from PyQt5 import QtWidgets, QtCore, QtGui
from pyqtgraph import PlotWidget
from datetime import datetime
import pyqtgraph as pg
import numpy as np
import os
import pickle
import json
import tifffile as tf
import cv2

# single-window app
class MyApp:
    
    # sometimes, putting gui code in __init__ creates problems (e.g. serialization w/r/t subprocesses)
    def __init__(self, args={}):

        # initialize video capture
        self.video_fname = args.get('video_fname', None)
        self.video_cap = None
        self.video_length = None
        self.current_frame_ndx = 0
        self.load_video()

        # initialize display
        self.intialize_display()

    # create gui window
    def intialize_display(self):
        
        # make app, we do it this way in case an instance of the app is
        # already running (like if using in jupyter notebook)
        #self.app = QtCore.QCoreApplication.instance()
        #if self.app is None:
        #    self.app = QtGui.QApplication([])
        self.app = pg.mkQApp()

        # it should exit on close per  https://stackoverflow.com/questions/57408620/cant-kill-pyqt-window-after-closing-it-which-requires-me-to-restart-the-kernal/58537032#58537032
        self.app.setQuitOnLastWindowClosed(True)

        # app has a main window
        self.window = QtWidgets.QWidget()
        self.window.setWindowTitle(
            "Example PyQt app"
        )
        self.window.resize(1400, 800)

        # window has a grid layout (easy to add widgets/items to)
        self.window_grid = QtWidgets.QGridLayout()

        # add other grids/widgets into window
        self.plot_graphics_widget = pg.GraphicsLayoutWidget()
        self.command_panel_grid = QtWidgets.QGridLayout()

#
        #####################################################################
        # build gui elements here
        #####################################################################
        # image
        #############
        
        # create view box for image item with scrolling locked
        self.image_vbox = pg.ViewBox(lockAspect=True, enableMouse=False)

        # create image item to put image in
        self.image_ii = pg.ImageItem()
        
        # adjust image showing to be row-major and origin in top left, removing need for transpose
        self.image_ii.setOpts(axisOrder="row-major")
        self.image_vbox.invertY()

        # make histogram lookup widget
        self.lut_histogram_item = pg.HistogramLUTItem(image=self.image_ii, fillHistogram=False)

        # add image item to box, add image viewbox and lut histogram to plot graphics window
        self.image_vbox.addItem(self.image_ii)
        self.plot_graphics_widget.addItem(self.image_vbox)
        self.plot_graphics_widget.addItem(self.lut_histogram_item)

        ##############
        # slider
        ##############
        # label above slider
        self.frame_slider_label = QtWidgets.QLabel('frame slider: {}/{}'.format(self.current_frame_ndx, self.video_length))

        # slider
        self.video_frame_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.video_frame_slider.setMinimum(0)
        self.video_frame_slider.setMaximum(self.video_length - 1)
        self.video_frame_slider.setTickInterval(1)
        self.video_frame_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.video_frame_slider.valueChanged.connect(self.refresh_dashboard)

        # add qlabel and slider to command panel
        self.command_panel_grid.addWidget(self.frame_slider_label, 0,0,1,2, alignment=QtCore.Qt.AlignCenter)
        self.command_panel_grid.addWidget(self.video_frame_slider, 1,0,1,2)


        #############
        # button
        #############
        self.save_curation_results_button = QtWidgets.QPushButton("save curation results!")
        self.save_curation_results_button.setStyleSheet("background-color : purple")
        self.save_curation_results_button.clicked.connect(self.save_curation_results)
        self.command_panel_grid.addWidget(self.save_curation_results_button, 2, 0, 1, 1)

        #####################################################################

        # assemble hierarchical containers
        # add plot graphics widget and command panel to window grid
        self.window_grid.addWidget(self.plot_graphics_widget)
        self.window_grid.addItem(self.command_panel_grid)

        # set window layout to grid
        self.window.setLayout(self.window_grid)

        # show the window
        self.window.show()

        # update display
        self.refresh_dashboard()

        # begin event loop
        self.app.exec_()

    # helper to load video
    def load_video(self):

        # create video capture
        self.video_cap = cv2.VideoCapture(self.video_fname)
        self.video_length = int(self.video_cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # helper to get frame from video
    def get_frame_from_video(self, frame_ndx):

        # set video capture to correct index
        self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, frame_ndx)
        success, img = self.video_cap.read()

        if not success:
            print('Cant grab frame {} from video capture!'.format(frame_ndx))
        else:
            return img

    # function to update displayed images
    def update_display_image(self, img):

        self.image_ii.setImage(img, autoLevels=True)

    # function to update displayed text in the window
    def update_display_text(self):
        
        self.current_frame_ndx = self.video_frame_slider.value()
        self.frame_slider_label.setText('frame slider: {}/{}'.format(self.current_frame_ndx, self.video_length))

    # wrapper function to update the window
    def refresh_dashboard(self):

        frame_ndx = self.video_frame_slider.value()
        img = self.get_frame_from_video(frame_ndx=frame_ndx)
        self.update_display_image(img)
        self.update_display_text()

    # function to compile internal variables into dict (for easy displaying or exporting)
    def get_curation_summary(self):

        curation_summary = {
            'video_fname': self.video_fname,
            'trial_start_ndx': [],
            'curation_datetime': datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        }

        return curation_summary


    def save_curation_results(self):

        # set button to red as visual aid
        self.save_curation_results_button.setStyleSheet("background-color: red")

        # get curation results
        curation_summary = self.get_curation_summary()

        # set savefilename
        save_filename = 'curation_results.json'
        print('Saving curation results {} to: {}'.format(curation_summary, save_filename))

        # save
        with(open(save_filename, 'w') as outfile):
            json.dump(curation_summary, outfile, indent=4, sort_keys=True)

        # set button back to signify done saving
        print('Done saving!')
        self.save_curation_results_button.setStyleSheet("background-color: purple")


# standalone testing
if __name__ == "__main__":

    # load file
    video_fname = 'C:/Users/rldun/Desktop/temp_render/20221021/output.mp4'
    
    # build app input parameters
    app_args = {
        'video_fname': video_fname
        }

    # instantiate app
    myapp = MyApp(app_args)