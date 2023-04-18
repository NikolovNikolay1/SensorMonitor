from Model_GUI_3 import Ui_MainWindow # Genia update
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtWidgets import QComboBox, QTableWidgetItem, QCheckBox, QWidget
from PyQt5.QtWidgets import QTableWidget  # https://russianblogs.com/article/7960879040/
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QVBoxLayout

from PyQt5.QtWidgets import QMdiArea, QMdiSubWindow, QTabWidget, QDialog
from PyQt5.QtCore import pyqtSignal


class SM_Win(QtWidgets.QWidget, Ui_MainWindow):
    countWin = 0

    def __init__(self):
        super().__init__()

        self.MainWindow = MainWindow
        # self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.setupUi(self.MainWindow)

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()

    # ui = Ui_MainWindow()
    # ui.setupUi(MainWindow)

    ui_SM = SM_Win()
    # ui_SM.setupUi(MainWindow)
    ui_SM.MainWindow.show()
    sys.exit(app.exec_())