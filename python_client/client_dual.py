
import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore    import *
from PyQt5.QtGui     import *

import observe_gui
import ambu_observe

convert = [None]*2
convert[0] = ambu_observe.convertDlcL20dD4
convert[1] = ambu_observe.convertNpa700B02WDFlow

# Marty with dual = 8090
# Marty with cal = 8099

adjust = [0] *2
adjust[1] = (8192-8112)
#adjust[1] = (8192-7616)
#adjust[1] = (8192-8022)
#adjust[1] = (8192-7612)

ambu = ambu_observe.AmbuObserve()

appTop = QApplication(sys.argv)

guiTop = observe_gui.ControlGui(ambu=ambu)
guiTop.setWindowTitle("PABV Control")
guiTop.show()

appTop.exec_()

ambu.stop()

