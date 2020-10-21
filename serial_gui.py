# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 12:17:35 2019
@author: Ammar Yasir/29433/EI
"""
#%%
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
global progress
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import sys
import serial
import threading
import time
#%%

# !!! Define the port and the Baud-Rate in the below variables !!!

COM_PORT = 'COM3' 
BAUD_RATE = 9600

#%%
serial_value = '0000'
ser = 0
test_thread = 0
new_serial = 0
dac_voltage = 0
adc_voltage = 0
adc_list =50*[]
dac_list = 50*[]
function = "00000000"

#%%
class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=6, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        fig.set_facecolor("black")
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.plot()

    def plot(self):
        self.figure.clf()
        ax = self.figure.add_subplot(111)
        ax.yaxis.tick_right()
        ax.spines['right'].set_color('white')
        ax.tick_params(axis='y', colors='white')
        adc_list.append(adc_voltage)
        dac_list.append(dac_voltage)
        if len(adc_list) > 2:
            adc_list.pop(0)
            dac_list.pop(0)
            adc_list.append(adc_voltage)
            dac_list.append(dac_voltage)
        ax.set_facecolor("black")
        ax.plot(adc_list, 'g-', label='ADC in')
        ax.plot(dac_list, 'r-', label='DAC out')
        ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left',
           ncol=2, borderaxespad=0.)
        self.draw()
# In[]
        
 #%%       
class Widget(QtWidgets.QWidget):
    def __init__(self):
        global test_thread
        super().__init__()
        self.resize(600, 500)
        self.setWindowTitle("GUI 2.0")
        
        self.connect_pb = QtWidgets.QPushButton('Connect', self)
        self.connect_pb.clicked.connect(self.connect)
        self.disconnect_pb = QtWidgets.QPushButton('Disconnect', self)
        self.disconnect_pb.clicked.connect(self.disconnect)
        
        dac = self.dac_box()
        adc = self.adc_box()
        status = self.status_box()
        mode = self.mode_box()
        self.canvas = PlotCanvas(self, width = 10, height = 4)
        
        lay = QtWidgets.QGridLayout(self)
        lay.addWidget(self.canvas, 0, 0, 4, 6)
        lay.addWidget(self.connect_pb, 1, 7, 1, 2)
        lay.addWidget(self.disconnect_pb, 2, 7, 1, 2)
        lay.addWidget(dac, 4, 0, 3, 3)
        lay.addWidget(adc, 4, 3, 3, 3)
        self.slider.sliderReleased.connect(self.value_changed)
        lay.addWidget(status, 4, 6, 3, 3)
        lay.addWidget(mode, 8, 0, 1, 9)
        self.setFixedSize(800,600)
            
        test_thread = threading.Thread(target = self.board)
            
#-----------------------------------------------------------------------------------------    
    def board(self):
        global new_serial
        global dac_voltage
        global adc_voltage
        try:
            while ser.isOpen():
                ams = '(?,{},{})'.format(function,serial_value)
                for i in ams:
                    ser.write(i.encode('utf-8'))
                    time.sleep(0.000000000001) #
                
                data = ser.readline()
                
                new_serial = list(data)
                
                new_serial = ''.join(chr(i) for i in new_serial)
                if new_serial != "":
                    if str(new_serial)[13] == ")":
                        dac_voltage = (3.3*(float(str(new_serial)[17:21]))/4095)
                        adc_voltage = (3.3*(float(str(new_serial)[22:26]))/4095)
                    elif str(new_serial)[14] == ")":
                        dac_voltage = (3.3*(float(str(new_serial)[18:22]))/4095)
                        adc_voltage = (3.3*(float(str(new_serial)[23:27]))/4095)
                        
                    elif str(new_serial)[15] == ")":
                        dac_voltage = (3.3*(float(str(new_serial)[19:23]))/4095)
                        adc_voltage = (3.3*(float(str(new_serial)[24:28]))/4095)
                        
                    elif str(new_serial)[16] == ")":
                        dac_voltage = (3.3*(float(str(new_serial)[20:24]))/4095)
                        adc_voltage = (3.3*(float(str(new_serial)[25:29]))/4095)
                        
                            
                    self.value_lcd.display(adc_voltage*1000)
                    self.canvas.plot()
                else:
                    pass
        except:
            pass
#-----------------------------------------------------------------------------------------    
    def connect(self):
        global ser
        ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=0.005) 
        if ser.isOpen():
            print(test_thread)
            self.connect_pb.setEnabled(False)
            self.disconnect_pb.setEnabled(True)      
            test_thread.start()
            
#-----------------------------------------------------------------------------------------    
    def disconnect(self):
        ser.close()
        if ser.isOpen() == False:
            print(test_thread)
            self.disconnect_pb.setEnabled(False)
            self.connect_pb.setEnabled(True)
#-----------------------------------------------------------------------------------------    
    @QtCore.pyqtSlot()
    def value_changed(self):
        global serial_value
        serial_value = int(((self.slider.value())*4095)/3.3/1000)
        
        try:
            string = str("{} mv").format(self.slider.value())
            self.dac_label.setText(string)
        except:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.setWindowModality(QtCore.Qt.ApplicationModal)
            error_dialog.showMessage('Please connect to port!')
            error_dialog.exec_() 
#-----------------------------------------------------------------------------------------
    def dac_box(self):
        group_box_settings = QtWidgets.QGroupBox(self)
        group_box_settings.setTitle("DAC V+ max.")
        
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, maximum=3300)
        
        self.dac_label = QtWidgets.QLabel("mv")
        grid = QtWidgets.QGridLayout()
        grid.addWidget(self.dac_label, 0,2,1,2)
        grid.addWidget(self.slider, 1,0,1,4)
        
        group_box_settings.setLayout(grid)

        return group_box_settings
#-----------------------------------------------------------------------------------------
    def adc_box(self):
        group_box_settings = QtWidgets.QGroupBox(self)
        group_box_settings.setTitle("ADC in")
        
        self.label = QtWidgets.QLabel("mV")
        self.value_lcd = QtWidgets.QLCDNumber()
        self.value_lcd.setFixedSize(300,50)
        grid = QtWidgets.QGridLayout()
        grid.addWidget(self.label, 0, 3)
        grid.addWidget(self.value_lcd,0, 0)
        
        group_box_settings.setLayout(grid)

        return group_box_settings
#-----------------------------------------------------------------------------------------
    def status_box(self):
        group_box_settings = QtWidgets.QGroupBox(self)
        group_box_settings.setTitle("Status")
        
        self.status_lcd = QtWidgets.QLabel()
        self.status_lcd.setAlignment(Qt.AlignCenter)
        self.status_lcd.setFont(QtGui.QFont('Arial', 20))
        grid = QtWidgets.QGridLayout()
        grid.addWidget(self.status_lcd, 0, 0)
        
        group_box_settings.setLayout(grid)

        return group_box_settings
#-----------------------------------------------------------------------------------------
    def mode_box(self):
        group_box_settings = QtWidgets.QGroupBox(self)
        group_box_settings.setTitle("Mode")
        grid = QtWidgets.QGridLayout()

        self.step_mode = QtWidgets.QRadioButton("Step")
        grid.addWidget(self.step_mode, 0, 0)
        self.step_mode.toggled.connect(self.status_changed)
        
        self.ramp_mode = QtWidgets.QRadioButton("Ramp")
        grid.addWidget(self.ramp_mode, 0, 2)
        self.ramp_mode.toggled.connect(self.status_changed)


        self.sine_mode = QtWidgets.QRadioButton("Sine")
        grid.addWidget(self.sine_mode, 0, 4)
        self.sine_mode.toggled.connect(self.status_changed)
        
        self.nc_mode_1 = QtWidgets.QRadioButton("n.c")
        grid.addWidget(self.nc_mode_1, 0, 6)    
        self.nc_mode_1.toggled.connect(self.status_changed)
        
        self.nc_mode_2 = QtWidgets.QRadioButton("n.c")
        grid.addWidget(self.nc_mode_2, 0, 8)    
        self.nc_mode_2.toggled.connect(self.status_changed)
        
        self.nc_mode_3 = QtWidgets.QRadioButton("n.c")
        grid.addWidget(self.nc_mode_3, 0, 10)    
        self.nc_mode_3.toggled.connect(self.status_changed)
        
        self.nc_mode_4 = QtWidgets.QRadioButton("n.c")
        grid.addWidget(self.nc_mode_4, 0, 12)    
        self.nc_mode_4.toggled.connect(self.status_changed)
        
        self.no_bias = QtWidgets.QRadioButton("No Bias")
        grid.addWidget(self.no_bias, 0, 14)    
        self.no_bias.toggled.connect(self.status_changed)
        
        group_box_settings.setLayout(grid)

        return group_box_settings
#-----------------------------------------------------------------------------------------    
    @QtCore.pyqtSlot()
    def status_changed(self):
        global function
        
        if self.step_mode.isChecked():
            self.status_lcd.setText("Step")
            function = "10000000"    
        if self.ramp_mode.isChecked():
            self.status_lcd.setText("Ramp")
            function = "01000000"
        if self.sine_mode.isChecked():
            self.status_lcd.setText("Sine")
            function = "00100000"
        if self.nc_mode_1.isChecked():
            self.status_lcd.setText("n.c.")
        
        if self.nc_mode_2.isChecked():
            self.status_lcd.setText("n.c.")
        
        if self.nc_mode_3.isChecked():
            self.status_lcd.setText("n.c.")
        
        if self.nc_mode_4.isChecked():
            self.status_lcd.setText("n.c.")
        
        if self.no_bias.isChecked():
            self.status_lcd.setText("No Bias")
        
#%%        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = Widget()
    w.show()
    sys.exit(app.exec_())