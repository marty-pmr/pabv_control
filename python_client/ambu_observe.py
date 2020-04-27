import serial
import serial.tools.list_ports
import time
import threading
import math
import sys
import traceback
import numpy

class AmbuObserve(object):

    def __init__(self):
        self._ser = None 
        self._set_serial = False
        self._ser_ports = serial.tools.list_ports.comports()
        self._callBack = self._debugCallBack
        self._file = None
        self._runEn = False
        self._currentCycle = 0
        self._RR = 0.0 # respitory rate setting (period)
        self._IT = 0.0 # Inhaliation Time seting (sec)
        self._initData()
        # Start Serial Read Thread
        self._thread = threading.Thread(target=self._handleSerial)
        self._thread.start()
        print("AmBu init()")

    def _initData(self):
        self._data = numpy.zeros((1000,5))
        # Coule use NaN np.empty(shape), A[:]=np.NaN

    def set_serial(self, portIndex):
        device = self._ser_ports[portIndex]
        self._ser = serial.Serial(device.device, 57600, timeout=1.0)
        self._set_serial = True

    def openLog(self, fName):
        self._file = open(fName,'a')

    def closeLog(self):
        self._file.close()
        self._file = None

    def _debugCallBack(self,data,count):
        l = len(self._data['time'])
        print(f"Got data. Len={l} count={count}")

    def setCallBack(self, callBack):
        self._callBack = callBack

    def stop(self):
        self._runEn = False
        self._thread.join()

    def _handleSerial(self):
        while True: # HELP - need to close this when the AmBu object is closed somehow?
            if self._runEn:
                try:
                    raw = self._ser.readline()
                    line = raw.decode('UTF-8')
                    data = line.rstrip().split(' ')
                    ts = time.time()

                    if data[0] == 'S':
                        # Status data "S Millis RR IH TH"
                        self._RR = int(data[2])/1000.0
                        self._IH = int(data[3])/1000.0

                    if data[0] == 'P':
                        # Format = "P millis cycle relayState GaugeP FlowP"
                        onTime = float(data[1])/1000.0
                        currentCycle = int(data[2])
                        relayState = bool(data[3])
                        gaugePressVal = int(data[4])
                        flowPressVal  = int(data[5])
                        gaugePress = convertDlcL20dD4(gaugePressVal)
                        flowVolume = convertNpa700B02WDFlow(flowPressVal)

                        # Shift data in numpy array by one
                        self._data[1:,:] = self._data[:-1,:]
                        # And append new data to it
                        self._data[0,:] = (onTime, currentCycle, relayState, gaugePress, flowVolume)

                        if self._file is not None:
                            #self._file.write(f'{ts}, {count}, ' + ', '.join(map(str,convValues)))
                            #self._file.write('\n')
                            pass

                except Exception as e:
                    traceback.print_exc()
                    print(f"Got error {e}")

# ---ooo000OOOooo--- ---ooo000OOOooo--- ---ooo000OOOooo--- ---ooo000OOOooo--- ---ooo000OOOooo---
def convertArduinoHaf(val):
    flow = 50.0 * (((float(val) / 16384.0) - 0.1) / 0.8)
    return flow


def convertArduinoAdcToVolts(val):
    return float(val) * (5.0 / 1023.0)


def convertNpa700B02WD(val):
    press = float(val-8192) * ( 5.07492 / 8191.0 )
    return press


def convertNpa700B02WDFlow(val):
    #return convertNpa700B02WD(val) * 12.0
    press = float(val-8192) * ( 2.0 / 8191.0 )
    B = 62.0
    if press < 0:
        sign = -1
        press = abs(press)
    else:
        sign = 1
    return sign * B * math.sqrt(abs(press))


def convertDlcL20dD4(val):
    press = -1.25 * ((float(val) - (0.5 * float(2**24))) / (0.5 * float(2**24))) * 20.0 * 2.54
    return press


def convertDlcL20dD4Reverse(press):
    adc = ((press / (-1.25 * 20.0 * 2.54)) * (0.5 * float(2**24))) + (0.5 * float(2**24))
    return int(adc)


def convertRaw(val):
    return float(val)


def convertZero(val):
    return 0.0
