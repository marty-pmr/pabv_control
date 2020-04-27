from PyQt5.QtWidgets import *
from PyQt5.QtCore    import *
from PyQt5.QtGui     import *

import numpy as np
import matplotlib.pyplot as plt
import ambu_control

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

import time

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=10, height=10, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = [fig.add_subplot(311), fig.add_subplot(312), fig.add_subplot(313)]
        super(MplCanvas, self).__init__(fig)
        fig.tight_layout(pad=3.0)


class ControlGui(QWidget):

    updateCount = pyqtSignal(str)
    updateRate  = pyqtSignal(str)
    updateRunButton = pyqtSignal(str)
    updateSetSerial = pyqtSignal(bool)
    updateRunState = pyqtSignal(bool)

    def __init__(self, *, ambu, refPlot=False, parent=None):
        super(ControlGui, self).__init__(parent)

        self.refPlot = refPlot

        self.ambu = ambu
        self.ambu.setCallBack(self.plotData)

        # A button will toggle this to accept stream data once hooked up
        self.run_observer = False
        # The logging 

        top = QVBoxLayout()
        self.setLayout(top)

        self.plot = MplCanvas()
        top.addWidget(self.plot)

        hl = QHBoxLayout()
        top.addLayout(hl)

        # PLOT ABOVE / SETTINGS BELOW

        # Set basic parameters [ GROUP BOX ]
        gb = QGroupBox('Data Stream Control')
        hl.addWidget(gb)
        vl = QVBoxLayout()
        gb.setLayout(vl)
        fl = QFormLayout()
        fl.setRowWrapPolicy(QFormLayout.DontWrapRows)
        fl.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        fl.setLabelAlignment(Qt.AlignRight)
        vl.addLayout(fl)

        # Serial Selector  
        sp = QComboBox()  # serial port
        for p in self.ambu._ser_ports:
            sp.addItem(str(p.device) + '-' + p.manufacturer )
        sp.setCurrentIndex(-1)
        sp.currentIndexChanged.connect(self.setSerial)
        self.updateRunState.connect(sp.setEnabled)
        fl.addRow('COM:',sp)
        
        # This button stops and starts the machine, but that should be done w/ a button
        # It should instead stop/start recieving streaming data, or just be removed...
        sb = QPushButton("Start")
        sb.setEnabled(False)
        sb.clicked.connect(self.toggleStreaming)
        self.updateSetSerial.connect(sb.setEnabled)
        self.updateRunButton.connect(sb.setText)
        vl.addWidget(sb)

 
        # Period Control  [ GROUP BOX ]
        gb = QGroupBox('GUI Control')
        hl.addWidget(gb)
        vl = QVBoxLayout()
        gb.setLayout(vl)
        fl = QFormLayout()
        fl.setRowWrapPolicy(QFormLayout.DontWrapRows)
        fl.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        fl.setLabelAlignment(Qt.AlignRight)
        vl.addLayout(fl)

        # This clears cycles count, but maybe it should clear the buffer?
        pb = QPushButton('Clear Count')
        pb.setEnabled(False)
        pb.clicked.connect(self.clrCount)
        self.updateSetSerial.connect(pb.setEnabled)
        vl.addWidget(pb)

        # Keeps track of cycles, but this should come from the arduino...
        cycles = QLineEdit()
        cycles.setText("0")
        cycles.setReadOnly(True)
        cycles.setEnabled(False)
        self.updateCount.connect(cycles.setText)
        self.updateSetSerial.connect(cycles.setEnabled)
        fl.addRow('Breaths:',cycles)

        # Shows you the data rate coming form the arduino
        sampRate = QLineEdit()
        sampRate.setText("0")
        sampRate.setReadOnly(True)
        sampRate.setEnabled(ambu._set_serial)
        self.updateSetSerial.connect(sampRate.setEnabled)
        self.updateRate.connect(sampRate.setText)
        fl.addRow('Sample Rate:',sampRate)

        self.pMinValue = QLineEdit()
        self.pMinValue.setText("-5")

        # Change to plot time in window
        self.plotCycles = QLineEdit()
        self.plotCycles.setText("10")
        fl.addRow('Plot Breaths:',self.plotCycles)

        
        # Log File [ GROUP BOX ]
        gb = QGroupBox('Log File')
        hl.addWidget(gb)

        vl = QVBoxLayout()
        gb.setLayout(vl)

        fl = QFormLayout()
        fl.setRowWrapPolicy(QFormLayout.DontWrapRows)
        fl.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        fl.setLabelAlignment(Qt.AlignRight)
        vl.addLayout(fl)

        self.logFile = QLineEdit()
        fl.addRow('Log File:',self.logFile)

        # TODO - This stop/start log file could be the same button using the change text option
        pb = QPushButton('Open File')
        pb.clicked.connect(self.openPressed)
        vl.addWidget(pb)
        pb = QPushButton('Close File')
        pb.clicked.connect(self.closePressed)
        vl.addWidget(pb)

        self.rTime = time.time()
        self.plotData()

    @pyqtSlot()
    def toggleStreaming(self):
        self.ambu._runEn = not self.ambu._runEn
        print("RunEn = ", self.ambu._runEn)
        if self.ambu._runEn == True:
            self.updateRunButton.emit("Stop")
            # Used to disable serial selector once running
            self.updateRunState.emit(False)
        else:
            self.updateRunButton.emit("Start")
            # Used to enable serial selector once stopped
            self.updateRunState.emit(True)

    @pyqtSlot()
    def setRate(self):
        try:
            self.ambu.cycleRate = float(self.rp.text())
        except Exception as e:
            print(f"Got GUI value error {e}")

    @pyqtSlot()
    def setOnTime(self):
        try:
            self.ambu.onTime = float(self.ro.text())
        except Exception as e:
            print(f"Got GUI value error {e}")

    @pyqtSlot()
    def setThold(self):
        try:
            self.ambu.startThold = float(self.st.text())
        except Exception as e:
            print(f"Got GUI value error {e}")

    @pyqtSlot(int)
    def setSerial(self, value):
        print("set serial COM = " + self.ambu._ser_ports[value].device)
        try:
            self.ambu.set_serial(value)
            self.updateSetSerial.emit(True)
        except Exception as e:
            print(f"Got GUI error trying to set COM port {e}")

    @pyqtSlot(str)
    def setRunState(self, astate):
        print(f"Set run state to {astate}")
        

    @pyqtSlot(int)
    def setState(self, value):
        print(f"set state value = {value}")
        try:
            self.ambu.state = value
        except Exception as e:
            print(f"Got GUI value error {e}")

    def clrCount(self):
        self.ambu.clearCount()

    @pyqtSlot()
    def openPressed(self):
        f = self.logFile.text()
        self.ambu.openLog(f)

    @pyqtSlot()
    def closePressed(self):
        self.ambu.closeLog()

    def plotData(self):
        data = self.ambu._data
        print("Data", data[0,:])
        try:
            self.plot.axes[0].cla()
            self.plot.axes[1].cla()
            self.plot.axes[2].cla()

            self.plot.axes[0].plot(data[:,0],data[:,4], color="red",linewidth=2.0)
            self.plot.axes[1].plot(data[:,0],data[:,5], color="green",linewidth=2.0)
            self.plot.axes[2].plot(data[:,0],data[:,5], color="blue",linewidth=2.0)

            self.plot.axes[0].set_ylim([float(self.pMinValue.text()),float(self.pMaxValue.text())])
            self.plot.axes[1].set_ylim([float(self.fMinValue.text()),float(self.fMaxValue.text())])
            self.plot.axes[2].set_ylim([float(self.vMinValue.text()),float(self.vMaxValue.text())])

            self.plot.axes[0].set_xlabel('Time')

            if self.refPlot:
                self.plot.axes[0].set_ylabel('Ref Flow SL/Min')
            else:
                self.plot.axes[0].set_ylabel('Press cmH20')

            self.plot.axes[1].set_xlabel('Time')
            self.plot.axes[1].set_ylabel('Flow L/Min')

            self.plot.axes[2].set_xlabel('Time')
            self.plot.axes[2].set_ylabel('Volume mL')

            self.plot.draw()
        except Exception as e:
            print(f"Got plotting exception {e}")

# -3 offset
# Add Run/Stop

