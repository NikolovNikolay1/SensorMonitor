# --------------------------------------------
# module class_signals - реализовать в отдельном файле
# --------------------------------------------
# про QT https://magadangorod.ru/common/upload/1/editor/file/PyQtCreatingwindowsappstoPython3Prohorenok.pdf


# при изменении имен необходимо редактировать yaml, а также прошерстить код в гуи фале
list_signals = {'A0': True, 'A1': True, 'A2': True, 'A3': True, 'A4': True, 'A5': True, 'ADC1015': True}

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtWidgets import QComboBox, QTableWidgetItem, QCheckBox, QWidget
from PyQt5.QtWidgets import QTableWidget  # https://russianblogs.com/article/7960879040/
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QVBoxLayout

from PyQt5.QtWidgets import QMdiArea, QMdiSubWindow, QTabWidget, QDialog

import matplotlib.pyplot
# пример фильтра событий https://digitrain.ru/questions/47960494/
from PyQt5.QtCore import pyqtSignal
import logging  # для отладки и сообщений  об ошибках  https://khashtamov.com/ru/python-logging/
from PyQt5.QtCore import QIODevice
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from collections import OrderedDict

matplotlib.use('TkAgg', force=True)
import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation

import numpy as np
import sys
import serial
import yaml  # https://pyneng.readthedocs.io/ru/latest/book/17_serialization/yaml.html
# https://tonais.ru/library/biblioteka-yaml-v-python
from Model_GUI_base import Ui_MainWindow # My working
#from Model_GUI_3 import Ui_MainWindow # Genia update
import time
import math
import typing  # для аннотированных списков
import struct

import threading  # многопоточность https://all-python.ru/osnovy/threading.html

import clas_for_signals
import class_build_graph
from class_work_with_file import class_work_with_file


class SM_Win(QtWidgets.QWidget, Ui_MainWindow):
    countWin = 0

    def __init__(self):
        super().__init__()

        self.MainWindow = MainWindow
        # self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.setupUi(self.MainWindow)

        self.MainWindow.comboBox_ComPort = CustomComboBox(self.frame_OpenPort)  # ComboBox_ports(self.frame_OpenPort) #QtWidgets.QComboBox
        # self.MainWindow.comboBox_ComPort = CustomComboBox(self.comboBox_ComPort)
        # self.MainWindow.comboBox_ComPort.place(in_=self.frame_OpenPort, x=20, y=20)
        # https://russianblogs.com/article/54731700043/
        self.MainWindow.comboBox_ComPort.setGeometry(QtCore.QRect(40, 10, 101, 22))

        self.load_last_setting()

        self.MainWindow.table_Show_Signals = Class_Tabl_Show_Signals()  # self.Create_tabl_Show_Signals(self.frame_Signal)
        self.MainWindow.table_Show_Signals.Create_tabl_Show_Signals(self.frame_Signal)
        # self.MainWindow.table_Show_Signals = self.MainWindow.table_Show_Signals.Create_tabl_Show_Signals(
        #     self.frame_Signal)
        # self.MainWindow.table_Show_Signals.setGeometry(QtCore.QRect(10, 30, 211, 241))
        self.MainWindow.table_Show_Signals.table_Show_Signals.setGeometry(QtCore.QRect(10, 30, 211, 241))
        self.MainWindow.table_Show_Signals.table_Show_Signals.setObjectName("table_Show_Signals")
        self.table_Show_Signals_assigne_connect_events_of_check_box()  # присваивает события check_box таблицы

        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # other propety
        self.flag_meas = False  # флаг разрешения измерений кнопки старт

        self.checkBox_A0.clicked.connect(self.clicked_checkBox_ADC_setting)
        self.checkBox_A1.clicked.connect(self.clicked_checkBox_ADC_setting)
        self.checkBox_A2.clicked.connect(self.clicked_checkBox_ADC_setting)
        self.checkBox_A3.clicked.connect(self.clicked_checkBox_ADC_setting)
        self.checkBox_A4.clicked.connect(self.clicked_checkBox_ADC_setting)
        self.checkBox_A5.clicked.connect(self.clicked_checkBox_ADC_setting)
        self.checkBox_ADC1015.clicked.connect(self.clicked_checkBox_ADC_setting)
        self.checkBox_AHT25_x38.clicked.connect(self.clicked_checkBox_ADC_setting)

        self.progressBar_Time_Measure.setMaximum(100)
        self.progressBar_Time_Measure.setMinimum(0)
        self.progressBar_Time_Measure.setValue(0)

        units_time = ['ms', 's', 'min', 'h']
        self.comboBox_Unit_Time.addItems(units_time)
        self.radioButton_Contitue_time.setChecked(True)

        # self.MainWindow.table_Show_Signals.cellChanged.connect(self.MainWindow.table_Show_Signals_cellChanged)
        # self.MainWindow.table_Show_Signals.cellChanged=self.MainWindow.table_Show_Signals.table_Show_Signals_cellChanged
        self.MainWindow.closeEvent = self.closeEvent
        # self.MainWindow.comboBox_ComPort.popupAboutToBeShown.connect(self.clicked_comboBox_ComPort)
        self.pushButton_Open_Port.clicked.connect(self.clicked_pushButton_Open_Port)
        self.pushButton_Close_port.clicked.connect(self.clicked_pushButton_Close_port)

        self.pushButton_Start_Meas.clicked.connect(self.clicked_pushButton_Start_Meas)
        self.pushButton_Stop_Meas.clicked.connect(self.clicked_pushButton_Stop_Meas)

        self.Signals = clas_for_signals.Signals_general()
        self.Signals_propety_figs = []  # : typing.List[class_build_graph.class_propety_figs()]
        # self.Figs_arr = []  # : typing.List[class_build_graph.class_propety_figs()]
        self.Figs_mdi = class_build_graph.class_build_figs()

        self.init_signal()
        self.timing_build_graph = 0
        self.timing_update_processing = 0
        self.flag_continuously = False
        self.cur_time = 0
        self.time_end = 1e-6
        self.time_start_fig = 0
        self.List_nums_signal_added = []

        # !!!!!!!идет после инициализации сигналов
        self.MainWindow.table_Show_Signals.update_table_Show_Signals(self.Signals)
        # self.MainWindow.table_Show_Signals.itemSelectionChanged.connect(self.table_Show_Signals_changed) # идет после инициализации сигналов

        self.MainWindow.table_Show_Signals.table_Show_Signals.itemChanged.connect(
            self.table_Show_Signals_changed)  # идет после инициализации сигналов
        self.table_Show_Signals_assigne_connect_events_of_check_box()  # присваивает события check_box таблицы

        # !!!!!!! идет после инициализации таблицы
        self.add_Signals_propety_figs_from_table()  # добавляет сигналы для рисования из таблицы на главной закладке и свойства
        self.serial = []

        self.lineEdit_Time_Measure.textEdited.connect(self.lineEdit_Time_Measure_changed)  # textChanged

        self.pushButton_Clear_data.clicked.connect(self.clicked_pushButton_Clear_data)

        self.pushButton_Select_Dir_to_Save.clicked.connect(self.clicked_pushButton_Select_Dir_to_Save)

        self.work_with_file = class_work_with_file()
        self.comboBox_Type_File_Save.clear()
        self.comboBox_Type_File_Save.addItems(self.work_with_file.list_ext)

        self.checkBox_Write_Save_Data.setChecked(True)

        self.lineEdit_Path_to_Save.textEdited.connect(self.update_prop_Work_With_File)
        self.lineEdit_Name_to_Save.textEdited.connect(self.update_prop_Work_With_File)
        self.comboBox_Type_File_Save.currentTextChanged.connect(self.update_prop_Work_With_File)

        self.pushButton_set_tile_windows_mdi.clicked.connect(self.clicked_pushButton_set_tile_windows_mdi)
        self.lineEdit_Visual_Effects_thinning.textEdited.connect(self.update_Visual_Effects_thinning)
        self.lineEdit_Visual_Effects_count_points.textEdited.connect(self.update_Visual_Effects_count_points)
        self.lineEdit_Visual_Effects_dalayDrawFig.textEdited.connect(self.update_Visual_Effects_dalayDrawFig)

    def init_signal(self):

        with open('settins_templates.yaml') as f:
            yaml_templates = yaml.safe_load(f)

        for name_signal in list_signals:
            # поиск сигнала среди инициализированных
            L = len(self.Signals.names_list)

            # проверяем среди всех возможных сигналов уже зарегистрированные и добавляем новые. старые не удаляются
            # для очистки новіх сигналов должна быть кнопка Clear
            if list_signals[name_signal] == True:  # signal measuring
                # проверяем, инициализирован ли сигнал
                flag = self.Signals.check_signal_inited(name_signal)
                if flag == False:  # если True - ничего не делаем
                    property_signal = yaml_templates[name_signal]
                    self.Signals.create_signal(name_signal,
                                               property_signal)  # свойства сигнала беруться из yaml-файла, templates подставляется здесь, а не в функции,чтобы не читать файл многократно (важно при первой инициализации, открытии программы)

    def lineEdit_Time_Measure_changed(self, text):
        self.radioButton_Limit_Time.setChecked(True)

    def table_Show_Signals_assigne_connect_events_of_check_box(self):
        n = self.MainWindow.table_Show_Signals.table_Show_Signals.rowCount()
        for i in range(n):
            p = self.MainWindow.table_Show_Signals.table_Show_Signals.cellWidget(i, 2)
            checkBoxs = p.findChildren(QtWidgets.QCheckBox)[0]
            checkBoxs.clicked.connect(self.table_Show_Signals_changed_checkBoxs)

    def add_Signals_propety_figs_from_table(self):
        # анализируется вся таблица. Необходимо запускать или с самого начала или при глобальном перезапуске

        n = self.MainWindow.table_Show_Signals.table_Show_Signals.rowCount()
        for i in range(n):
            prop_signal_graph = class_build_graph.class_propety_figs()

            name_unit_signal = self.Signals.array_signals[i].time_unit
            prop_signal_graph.unit_x.append(name_unit_signal)
            name_unit_signal = self.Signals.array_signals[i].y_unit
            prop_signal_graph.unit_y.append(name_unit_signal)

            prop_signal_graph.number_fig = int(
                self.MainWindow.table_Show_Signals.table_Show_Signals.item(i, 3).text())  # "Num.Fig",

            p = self.MainWindow.table_Show_Signals.table_Show_Signals.cellWidget(i, 2)
            checkBoxs = p.findChildren(QtWidgets.QCheckBox)[0]
            prop_signal_graph.flag_show = checkBoxs.checkState()  # показывать или нет

            prop_signal_graph.coef_scale = float(
                self.MainWindow.table_Show_Signals.table_Show_Signals.item(i, 4).text())  # scale
            prop_signal_graph.Shift = float(
                self.MainWindow.table_Show_Signals.table_Show_Signals.item(i, 5).text())  # Shift

            p = self.MainWindow.table_Show_Signals.table_Show_Signals.cellWidget(i, 6)
            checkBoxs = p.findChildren(QtWidgets.QCheckBox)[0]
            prop_signal_graph.Windows_separete = checkBoxs.checkState()

            prop_signal_graph.total_points = int(self.lineEdit_Visual_Effects_count_points.text())
            prop_signal_graph.d_point = int(self.lineEdit_Visual_Effects_thinning.text())

            self.Signals_propety_figs.append(prop_signal_graph)

    def update_Visual_Effects_thinning(self):
        #if int(self.lineEdit_Visual_Effects_thinning.text()) >= 1:
        #try:
        a=self.lineEdit_Visual_Effects_thinning.text()
        if a.isdigit():
            for i in range(len(self.Signals_propety_figs)):
                self.Signals_propety_figs[i].d_point = int(self.lineEdit_Visual_Effects_thinning.text())

    def update_Visual_Effects_count_points(self):
        a = self.lineEdit_Visual_Effects_count_points.text()
        if a.isdigit():
            if int(self.lineEdit_Visual_Effects_count_points.text()) >= 1:
                for i in range(len(self.Signals_propety_figs)):
                    self.Signals_propety_figs[i].total_points = int(self.lineEdit_Visual_Effects_count_points.text())

    def update_Visual_Effects_dalayDrawFig(self):
        t = float(self.lineEdit_Visual_Effects_dalayDrawFig.text())
        if t > 0:
            self.Figs_mdi.time_limit = t
        if len(self.Figs_mdi.Figs_arr) > 0:
            for i in range(len(self.Figs_mdi.Figs_arr)):
                self.Figs_mdi.Figs_arr[i].time_limit = self.Figs_mdi.time_limit

    def init_Figs_arr(self):

        for i in range(len(self.Signals_propety_figs)):

            if self.Signals_propety_figs[i].flag_show == True:
                n = len(self.Figs_mdi.Figs_arr)
                number_fig = self.Signals_propety_figs[i].number_fig
                number_signal = i
                # if n==0:
                #
                #     Figs_arr = class_build_graph.class_propety_figs()
                #     Figs_arr.number_fig = self.Signals_propety_figs[i].number_fig
                #     Figs_arr.flag_show= self.Signals_propety_figs[i].flag_show
                #     Figs_arr.numbers_signal.append(i)
                #     Figs_arr.init_fig_mdi('',self)
                #     self.Figs_mdi.Figs_arr.append(Figs_arr)
                #
                # else:

                windows_mdi = self.mdiArea.subWindowList()
                flag_inited_win = False
                flag_inited_arr = False
                if n > 0:  # n = len(self.Figs_mdi.Figs_arr)
                    # проверка, инициализировано ли окно
                    b = self.Figs_mdi.exam_inited_win_mdi(number_fig, windows_mdi)
                    flag_inited_win = b[0]
                    num_figs_mdi_opened = b[1]
                    flag_inited_arr = b[2]

                if (flag_inited_win == False) and (
                        flag_inited_arr == False):  # окно еще не инициализировалось и нет self.Figs_arr[j]
                    Figs_arr = class_build_graph.class_propety_figs()
                    Figs_arr.number_fig = self.Signals_propety_figs[i].number_fig
                    Figs_arr.flag_show = self.Signals_propety_figs[i].flag_show
                    Figs_arr.init_fig_mdi('', self)
                    self.Figs_mdi.Figs_arr.append(Figs_arr)
                else:
                    self.Figs_mdi.Figs_arr[num_figs_mdi_opened].numbers_signal.append(i)

                nf = len(self.Figs_mdi.Figs_arr)
                # self.Figs_mdi.Figs_arr[nf-1].numbers_signal.append(i)
                self.Figs_mdi.add_number_signals(number_fig, number_signal)
        # self.Figs_mdi.time_limit = 0.2
        self.Figs_mdi.time_limit = float(self.lineEdit_Visual_Effects_dalayDrawFig.text())
        for i in range(len(self.Figs_mdi.Figs_arr)):
            # используем модуль collections.OrderedDict.fromkeys()
            # чтобы удалить дубликаты из списка
            # https://myrusakov.ru/python-remove-list-duplicate.html
            li = list(OrderedDict.fromkeys(self.Figs_mdi.Figs_arr[i].numbers_signal))
            self.Figs_mdi.Figs_arr[i].numbers_signal = li

            if self.Figs_mdi.Figs_arr[i].inited_mdi == False:
                self.Figs_mdi.Figs_arr[i].child_mdi = self.create_MDI_ver2(self.Figs_mdi.Figs_arr[i])
                self.Figs_mdi.Figs_arr[i].inited_mdi = True
                self.Figs_mdi.Figs_arr[i].time_limit = self.Figs_mdi.time_limit
        self.Figs_mdi.signals_short_2 = self.Signals_propety_figs

    def table_Show_Signals_changed_checkBoxs(self):
        #  анализируется вся таблица т.к. не получается обратиться к конкретному CheckBox и определить номер строки

        # obj = self.MainWindow.sender()
        # if item == QtWidgets.QCheckBox():
        #     a=1
        # else:
        #     a=2
        #   #  row = item.row()
        #   #  col = item.column()
        n = self.MainWindow.table_Show_Signals.table_Show_Signals.rowCount()
        if self.flag_meas == False:

            for i in range(n):
                p = self.MainWindow.table_Show_Signals.table_Show_Signals.cellWidget(i, 2)
                checkBoxs = p.findChildren(QtWidgets.QCheckBox)[0]
                # prop_signal_graph.flag_show = checkBoxs.checkState()
                self.Signals_propety_figs[i].flag_show = bool(checkBoxs.checkState())  # показывать или нет

                p = self.MainWindow.table_Show_Signals.table_Show_Signals.cellWidget(i, 6)
                checkBoxs = p.findChildren(QtWidgets.QCheckBox)[0]
                self.Signals_propety_figs[i].Windows_separete = bool(checkBoxs.checkState())  # показывать или нет

        elif self.flag_meas == True:  # во время измерения

            for i in range(n):
                flag_old_show = self.Signals_propety_figs[i].flag_show

                p = self.MainWindow.table_Show_Signals.table_Show_Signals.cellWidget(i, 2)
                checkBoxs = p.findChildren(QtWidgets.QCheckBox)[0]
                # prop_signal_graph.flag_show = checkBoxs.checkState()
                flag_new_show = bool(checkBoxs.checkState())
                if flag_old_show != flag_new_show:
                    self.Signals_propety_figs[i].flag_show = flag_new_show
                    if flag_new_show == True:
                        unit_time = self.comboBox_Unit_Time.currentText()
                        self.Signals_propety_figs[i].init_fig(unit_time)

    def table_Show_Signals_changed(self, item):

        # table_Show_Signals.setColumnWidth(0, 1)  # "Name"
        # table_Show_Signals.setColumnWidth(1, 1)  # "cod"
        # table_Show_Signals.setColumnWidth(2, 15)  # "Shw, \
        # table_Show_Signals.setColumnWidth(3, 5)  # "Num.Fig",
        # table_Show_Signals.setColumnWidth(4, 5)  # "k", \
        # table_Show_Signals.setColumnWidth(5, 8)  # Shift - смещение
        # table_Show_Signals.setColumnWidth(6, 4)  # "W"  # W - в отдельном окне
        # table_Show_Signals.setColumnWidth(7, 4)  #

        i = item.row()
        col = item.column()

        self.Signals_propety_figs[i].name = self.MainWindow.table_Show_Signals.table_Show_Signals.item(i, 0).text()
        # self.Signals_propety_figs[i].time_unit =
        self.Signals_propety_figs[i].number_fig = int(
            self.MainWindow.table_Show_Signals.table_Show_Signals.item(i, 3).text())
        self.Signals_propety_figs[i].coef_scale = float(
            self.MainWindow.table_Show_Signals.table_Show_Signals.item(i, 4).text())  # scale
        self.Signals_propety_figs[i].Shift = float(
            self.MainWindow.table_Show_Signals.table_Show_Signals.item(i, 5).text())  # Shift

        if (self.flag_meas == True) and col == 2:
            unit_time = self.comboBox_Unit_Time.currentText()
            self.Signals_propety_figs[i].init_fig(unit_time)

    def clicked_pushButton_Select_Dir_to_Save(self):
        dirlist = QFileDialog.getExistingDirectory(self, "Выбрать папку", ".")
        # self.plainTextEdit.appendHtml("<br>Выбрали папку: <b>{}</b>".format(dirlist))
        self.lineEdit_Path_to_Save.setText(str(dirlist))

    def update_prop_Work_With_File(self):
        st = str(self.lineEdit_Path_to_Save.text())
        self.work_with_file.path_dir = st
        st = str(self.lineEdit_Name_to_Save.text())
        self.work_with_file.file_name = st
        st = str(self.comboBox_Type_File_Save.currentText())
        self.work_with_file.ext = st

    def clicked_checkBox_ADC_setting(self):
        obj = self.MainWindow.sender()  # https://pythonworld.ru/gui/pyqt5-eventssignals.html
        # https://ru.stackoverflow.com/questions/1030872/%D0%9F%D1%80%D0%BE%D0%B1%D0%BB%D0%B5%D0%BC%D0%B0-%D1%81-sender-%D0%B2-pyqt5
        name_obj = obj.objectName()
        name_obj = name_obj[9:]  # удаляем тип виджита из имени
        list_signals[name_obj] = obj.isChecked()

    def load_last_setting(self):
        from pprint import pprint
        with open('settins_templates.yaml') as f:
            templates = yaml.safe_load(f)
        with open('settins_templates_last.yaml') as f2:
            templates_last = yaml.safe_load(f2)

        list1 = templates['Type_Controllers']
        self.comboBox_Type_Controller.clear()
        self.comboBox_Type_Controller.addItems(list1)

        list1 = templates['Visual_Effects']
        self.lineEdit_Visual_Effects_count_points.setText(str(list1['total_points']))
        self.lineEdit_Visual_Effects_thinning.setText(str(list1['d_point']))
        self.lineEdit_Visual_Effects_dalayDrawFig.setText(str(list1['delay_draw_fig']))

        s = templates_last['Type_Controller_last']
        self.comboBox_Type_Controller.setCurrentText(s)

        s = str(templates_last['Link_with_PC_Types_last'])
        if s == 'USB':
            self.radioButton_Link_with_PC_USB.setChecked(True)
        elif s == 'Bluetooth':
            self.radioButton_Link_with_PC_Bluetooth.setChecked(True)
        elif s == 'WiFi':
            self.radioButton_Link_with_PC_WiFi.setChecked(True)

        self.lineEdit_Data_Setting_Meas_Freq.setText(str(templates_last['Meas_Freq_last']))
        self.lineEdit_Speed.setText(str(templates_last['Link_with_PC_Speeds_last']))
        for adc_name in (templates_last['Meas_ADC_last']):
            s = adc_name
            f = templates_last['Meas_ADC_last'][s]
            check_box_name = "checkBox_" + adc_name
            check_box_widget = QCheckBox()
            check_box_widget = self.centralwidget.findChild(QCheckBox,
                                                            check_box_name)  # не работает если вместо centralwidget поставть groupBox_Setting_ADC
            if check_box_widget != None:
                check_box_widget.setChecked(f)
            list_signals[adc_name] = f
            # check_box_name='self.'+ check_box_name
            # check_box_widget=eval(check_box_name)
            # check_box_widget.setChecked(f)
        s = templates_last['Last_dir']
        self.lineEdit_Path_to_Save.setText(s)
        s = templates_last['Last_name_file']
        self.lineEdit_Name_to_Save.setText(s)
        self.update_prop_Work_With_File

        # pprint(templates)

    def closeEvent(self, event):
        # https://overcoder.net/q/1058062/pyqt-%D0%BD%D0%B0%D0%B6%D0%B0%D1%82%D0%B8%D0%B5-x-%D0%BD%D0%B5-%D0%B2%D1%8B%D0%B7%D1%8B%D0%B2%D0%B0%D0%B5%D1%82-closeevent
        # https://ru.stackoverflow.com/questions/1126936/pyqt5-%D0%BD%D0%B5-%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D0%B0%D0%B5%D1%82-closeevent
        reply = QtWidgets.QMessageBox.information(self, 'Выход', 'Вы точно хотите выйти?',
                                                  QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                  QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            if self.radioButton_Link_with_PC_USB.isChecked() == True:
                Link_with_PC_Types_last_val = 'USB'
            elif self.radioButton_Link_with_PC_Bluetooth.isChecked() == True:
                Link_with_PC_Types_last_val = 'Bluetooth'
            elif self.radioButton_Link_with_PC_WiFi.isChecked() == True:
                Link_with_PC_Types_last_val = 'WiFi'

            Edit_Data_Setting_Meas_Freq_val = self.lineEdit_Data_Setting_Meas_Freq.text()

            Type_Controller_last_val = self.comboBox_Type_Controller.currentText()

            Link_with_PC_Speeds_last_val = self.lineEdit_Speed.text()

            with open('settins_templates.yaml') as f:
                templates = yaml.safe_load(f)

            Meas_ADC_last = templates['Meas_ADC_last']  # https://russianblogs.com/article/37421047373/
            for name_ADC in list_signals:
                if list_signals[name_ADC] == True:
                    # Meas_ADC_last.update(name_ADC, True)
                    Meas_ADC_last[name_ADC] = True
                else:
                    # Meas_ADC_last.update(name_ADC, False)
                    Meas_ADC_last[name_ADC] = False

            Last_dir = str(self.lineEdit_Path_to_Save.text())
            Last_name_file = 'temp'  # self.lineEdit_Name_to_Save.setText(s)

            to_yaml = {
                'Type_Controller_last': Type_Controller_last_val,
                'Link_with_PC_Speeds_last': Link_with_PC_Speeds_last_val,
                "Link_with_PC_Types_last": Link_with_PC_Types_last_val,
                'Meas_Freq_last': Edit_Data_Setting_Meas_Freq_val,
                'Meas_ADC_last': Meas_ADC_last,
                'Last_dir': Last_dir,
                'Last_name_file': Last_name_file
            }

            with open('settins_templates_last.yaml', 'w') as f:
                yaml.dump(to_yaml, f, default_flow_style=False)

            # with open('settins_templates.yaml') as f:
            #    print(f.read())
            event.accept()
        else:
            event.ignore()

    def clicked_pushButton_Open_Port(self):
        portx = str(self.MainWindow.comboBox_ComPort.currentText())
        # portx =self.comboBox_ComPort.currentText() # "COM3"
        bps = int(self.lineEdit_Speed.text())
        # bps = 115200  # 9600
        # bps = 2000000  # 2*921600  # 9600
        # Последовательный порт выполняется до тех пор, пока он не будет открыт, а затем использование команды open сообщит об ошибке
        try:
            # self.Serial = serial()
            ser = serial.Serial(portx, int(bps), timeout=1)
            self.serial = ser  # ,,

            if (self.serial.isOpen()):
                print('open success')
                # self.pushButton_Open_Port.setStyleSheet(
                #     "QPushButton::hover{"
                #     "background-color: #ffd2cf;"
                #     "border: none;"
                #     "}"
                # )
                # flag=False
                # while flag==False:
                #     #self.serial.write(123)
                #     self.serial.write(str('s').encode())
                #    # self.serial.write(bytes(str(123).encode()))
                #     time.sleep(1)
                #     a=self.serial.read()
                #     flag = True
                #     # if len(a)>0:
                #     #     a=int(a)
                #     #     if a==123:
                #     #         flag = True

                self.pushButton_Open_Port.setStyleSheet('color: green;')
        except IOError:
            print("Invalid comm port!")
            self.pushButton_Open_Port.setStyleSheet('color: red;')

    # serial.setPortName()
    # serial.open(QIODevice.ReadWrite)

    def clicked_pushButton_Close_port(self):
        self.serial.close()
        self.pushButton_Open_Port.setStyleSheet('color: black;')

    def clicked_pushButton_Stop_Meas(self):
        self.flag_meas = False
        self.pushButton_Start_Meas.setStyleSheet('color: black;')

    def clicked_pushButton_Clear_data(self):

        n = len(self.Signals_propety_figs)
        for i in range(n):
            self.Signals_propety_figs[i].signal_short.time_arr = []
            self.Signals_propety_figs[i].signal_short.y_arr = []

            self.Signals_propety_figs[i].signal_short.time_arr.append(0)
            self.Signals_propety_figs[i].signal_short.y_arr.append(0)
            # self.Signals_propety_figs[i].build_fig_mdi()

        # n = len(self.Signals.array_signals)
        # for i in range(n):
        #     self.Signals.array_signals[i].time_arr = []
        #     self.Signals.array_signals[i].y_arr = []
        #     self.Signals.array_signals[i].time_shift = 0
        self.Signals.clear_data() # обнуляен данные и time_shift
       # n = len(self.Signals.array_signals)
        self.Figs_mdi.build_fig_mdi()
        self.reconnect_com_port()

    def reconnect_com_port(self):
        # переоткрытие порта
        try:
            if (self.serial.isOpen()):
                fl=self.flag_meas
                self.clicked_pushButton_Close_port()
                self.clicked_pushButton_Open_Port()
                self.flag_meas = fl
            else:
                fl = self.flag_meas
                self.clicked_pushButton_Open_Port()
                self.flag_meas = fl
        except:
            print("without reconnect ")


    def clicked_pushButton_Start_Meas_test(self):

        k = 1
        unit_time = self.comboBox_Unit_Time.currentText()
        if unit_time == 'ms':
            k = 1000
        elif unit_time == 's':
            k = 1
        elif unit_time == 'min':
            k = 60
        elif unit_time == 'h':
            k = 1 / 3600

            # инициализация графиков
        n = len(self.Signals_propety_figs)
        for i in range(n):
            self.Signals_propety_figs[i].init_fig(unit_time)
        # self.Signals_propety_figs[i].init_fig_mdi(unit_time)
        # self.create_MDI(self, self.Signals_propety_figs[i], unit_time)

        flag_continuously = self.radioButton_Contitue_time.isChecked()  # флаг непрерывного измерения
        if flag_continuously == True:
            time_end = 1e10

        elif self.radioButton_Limit_Time.isChecked() == True:

            time_end = float(self.lineEdit_Time_Measure.text())  # общее время измерения

        time_end = time_end

        # plt.figure()

        # Когда интерактивный режим установлен в True, график будет вырисовываться только при вызове метода draw ()
        # plt.show()
        # plt.xlabel('Час')
        # plt.ylabel('Сигнал')
        # plt.title('АЦП')

        # https://python-scripts.com/matplotlib
        # https://nbviewer.ipython.org/github/whitehorn/Scientific_graphics_in_python/blob/master/P1%20Chapter%201%20Pyplot.ipynb
        # https://pythonworld.ru/novosti-mira-python/scientific-graphics-in-python.html
        # https://jenyay.net/Matplotlib/Figure  - графики в разніх окнах
        # fig, ax = plt.subplots()
        xdata, ydata = [], []

        fig = plt.figure(figsize=(16, 8))
        axes = fig.add_subplot(111)
        # add_subplot -  https://stackoverflow.com/questions/3584805/in-matplotlib-what-does-the-argument-mean-in-fig-add-subplot111
        plt.ion()  # включает итеративній режим
        # fig, axes = plt.subplots()
        data_plot = plt.plot(0, 0)
        line, = axes.plot(0, 0)  # 'or'

        # fr_number = axes.annotate(
        #     "0",
        #     (0, 1),
        #     xycoords="axes fraction",
        #     xytext=(10, -10),
        #     textcoords="offset points",
        #     ha="left",
        #     va="top",
        #     animated=True,
        # )
        # bm = BlitManager(fig.canvas, [line, fr_number])
        x0 = []
        y0 = []

        self.flag_meas = True
        time_start = time.perf_counter()  # seconds
        cur_time = 0

        # plt.show()
        # plt.show(block=False)
        plt.pause(0.1)
        c = 1
        while (self.flag_meas == True) and (cur_time <= time_end):
            tt = (time.perf_counter() - time_start)
            cur_time = tt * k
            x = cur_time
            y = math.sin(2 * 3.14 * 10 * x)
            x0.append(x)
            y0.append(y)
            #  if c % 100 == 0:  # % -- mod
            if len(x0) > 1:

                axes.set_xlim(min(x0), max(x0))
                axes.set_ylim(-1, 1)

                line.set_xdata([])
                line.set_ydata([])
                line.set_xdata(x0)
                line.set_ydata(y0)
                if c % 100 == 0:  # % -- mod  if  round(tt) % 0.2 == 0:
                    plt.draw()
                    plt.pause(0.010)
                    L = len(x0)
                    if L > 2000:
                        del x0[0:L - 1000]
                        del y0[0:L - 1000]
                # if c % 5 == 0:  # % -- mod
                #     bm.update()

                # L=len(x0)
                # data_to_fig.set_data(x0, y0) # frames=np.linspace(0, 2 * np.pi, 128)
                # ani = FuncAnimation(fig, ln, interval=1,blit=True)#,
                # plt.show()

            c += 1

        # plt.plot(x0, y0, label='A0')
        #
        self.flag_meas = False

    def clicked_pushButton_Start_Meas(self):
        self.pushButton_Start_Meas.setStyleSheet('color: green;')
        k = 1
        unit_time = self.comboBox_Unit_Time.currentText()
        if unit_time == 'ms':
            k = 1000
        elif unit_time == 's':
            k = 1
        elif unit_time == 'min':
            k = 1 / (60)
        elif unit_time == 'h':
            k = 1 / (3600)

        self.reconnect_com_port() # для сброса времени


        flag_continuously = self.radioButton_Contitue_time.isChecked()  # флаг непрерывного измерения
        self.flag_continuously = self.radioButton_Contitue_time.isChecked()  # флаг непрерывного измерения

        if flag_continuously == True:
            time_end = 1e10
            self.time_end = 1e10
        elif self.radioButton_Limit_Time.isChecked() == True:
            time_end = float(self.lineEdit_Time_Measure.text())  # общее время измерения
            self.time_end = float(self.lineEdit_Time_Measure.text())  # общее время измерения

        self.progressBar_Time_Measure.setValue(0)
        self.progressBar_Time_Measure.update()

        self.init_Figs_arr()
        self.Figs_mdi.assign_inFigs_arr_arr__signalS_short_for_figs()

        # self.build_graph_by_Fig_arr()
        # for i in range(0, len(self.Figs_arr), 1):  # перебор по всем инициализированным окнам
        #     fig = self.Figs_mdi.Figs_arr[i].fig_axes
        #     ani = animation.FuncAnimation(fig, self.Figs_mdi.Figs_arr[i].build_fig_mdi_Fig_arr, blit=True, interval=500)
        time.sleep(2)

        time_end = time_end
        n = len(self.Signals_propety_figs)
        for i in range(n):
            # self.Signals_propety_figs[i].init_fig(unit_time)
            # self.Signals_propety_figs[i].init_fig_mdi(unit_time, self)
            self.Signals_propety_figs[i].unit_x = unit_time
            self.Signals_propety_figs[i].coef_scale_x = k / 1e6

        List_nums_signal_for_prepere = []

        #     self.Signals_propety_figs[i]=self.create_MDI_ver2(self.Signals_propety_figs[i])
        # time_pause=0.1
        # thr1 = threading.Thread(target=self.build_graph, args = (time_pause,), daemon =True)

        ######################################################
        # thr1 = threading.Thread(target=self.build_graph_by_Fig_arr, args=(,), daemon=True)
        # args=(,)

        #####################################################

        # self.Signals_propety_figs[i].inited_mdi == True

        # self.create_MDI(unit_time)
        # plt.figure()

        # Когда интерактивный режим установлен в True, график будет вырисовываться только при вызове метода draw ()
        # plt.show()
        # plt.xlabel('Час')
        # plt.ylabel('Сигнал')
        # plt.title('АЦП')

        # https://python-scripts.com/matplotlib
        # https://nbviewer.ipython.org/github/whitehorn/Scientific_graphics_in_python/blob/master/P1%20Chapter%201%20Pyplot.ipynb
        # https://pythonworld.ru/novosti-mira-python/scientific-graphics-in-python.html

        # fig, ax = plt.subplots()
        xdata, ydata = [], []

        # add_subplot -  https://stackoverflow.com/questions/3584805/in-matplotlib-what-does-the-argument-mean-in-fig-add-subplot111

        # x0=[]
        # y0=[]
        fl = False
        try:
            if (self.serial.isOpen()):
                fl = True
            else:
                QtWidgets.QMessageBox.about(self, "Error", "Порт не открыт. " )
            # plt.ion()  # включает итеративній режим
        except Exception as e:
            QtWidgets.QMessageBox.about(self, "Error", "Вероятно, порт не открыт. " + str(e))
            self.flag_meas = False

        if (fl == True) and self.serial.isOpen():

            self.flag_meas = True

            self.signals_propety_figs_prepear_data()
            for i in range(len(self.Figs_mdi.Figs_arr)):
                self.Figs_mdi.Figs_arr[i].build_fig_mdi_Fig_arr()
            # self.Figs_mdi.animation_fig_mdi()

            time.sleep(0.2)
            time_start = time.perf_counter()  # seconds
            cur_time = 0
            time_start_fig = 0

            self.cur_time = 0
            self.timing_update_processing = 0
            self.time_start_fig = 0
            # self.Figs_mdi.animation_fig_mdi()

            #        for i in range(0, len(self.Figs_mdi.Figs_arr), 1):  # перебор по всем инициализированным окнам
            #            # self.Figs_arr[i].build_fig_mdi_Fig_arr_without_timer()
            #            if i == 0:
            #                ani0 = (animation.FuncAnimation(self.Figs_mdi.Figs_arr[i].fig_plt,
            #                                                self.Figs_mdi.Figs_arr[i].build_fig_mdi_Fig_arr_without_timer, blit=True,
            #                                                interval=300))
            #            if i == 1:
            #                ani1 = (animation.FuncAnimation(self.Figs_mdi.Figs_arr[i].fig_plt,
            #                                                self.Figs_mdi.Figs_arr[i].build_fig_mdi_Fig_arr_without_timer, blit=True,
            #                                                interval=300))
            # plt.show()

            c = 1
            # thr1 = threading.Thread(target=self.visual_effects_at_time_build_graph, daemon=True)
            # thr1 = threading.Timer(1.5, self.visual_effects_at_time_build_graph)
            # thr1.start()
            # thr_test = threading.Timer(1, self.test_threading)
            # thr_test.start()
            count_ex = 0
            count_not_successful_data_in_a_row=0
            #------------------------------------------------------------------
            #------------------- Основной цикл---------------------------------
            while (self.flag_meas == True) and (self.cur_time <= self.time_end):
                count_ex += 1
                if count_ex % 50000 == 0:
                    reply = QtWidgets.QMessageBox.information(self, 'Выход', 'Связь потеряна count_ex = ' + str(count_ex),
                                                              QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                              QtWidgets.QMessageBox.No)
                    if reply == QtWidgets.QMessageBox.Yes:
                        self.flag_meas = False
                        self.clicked_pushButton_Close_port()
                        self.pushButton_Start_Meas.setStyleSheet('color: red;')
                        break


                while (self.serial.inWaiting() > 0) and (self.flag_meas == True):
                    count_ex = 0
                    tt = (time.perf_counter() - time_start)
                    cur_time = tt * k
                    self.cur_time = tt * k

                    # while (flag_sinhronozation == False):
                    #     fd = self.serial.read()
                    #     fd = int.from_bytes(fd, 'big')
                    #            # https://russianblogs.com/article/8614986773/
                    #     if fd == 123:
                    #         flag_sinhronozation=True

                    flag_sinhronozation = False
                    count_ex_flag_sinhronozation = 0
                    while (flag_sinhronozation == False):
                        count_ex_flag_sinhronozation += 1
                        fd = self.serial.read()
                        fd = int.from_bytes(fd, 'big')
                        if fd > 0 and fd < 10:
                            for ii_ in range(1, 9, 1):
                                if (fd == ii_) and (ii_ != 0):
                                    flag_sinhronozation = True
                                    if fd == 8:
                                        fd = 8
                                        #     определям начальный индекс в массиве сигналов для соответствующего кода & определяем базовую структуру данных
                                    num_signal, st_struct, size_sruct = self.Signals.get_current_signals_num_read(fd)
                                    break

                        if count_ex_flag_sinhronozation > 200:
                            QtWidgets.QMessageBox.about(self, "Error", "Данные не поступают ")
                            self.flag_meas = False
                            self.pushButton_Start_Meas.setStyleSheet('color: red;')
                            break
                        elif flag_sinhronozation == False:
                            time.sleep(0.1)
                    # можно обойтись без предварительной передачи кода сигнала, а просто считать первый байт

                    # fd=self.serial.read()
                    # fd = int.from_bytes(fd, 'big') # считываем код сигнала

                    # fd=int(fd)
                    #     print(c)
                    #     data = self.serial.readline()  # read Arduino (считівает пакет без абзацев)
                    #     fd=int(data[0])
                    # self.Signals.current_signals_num_read -
                    #     определям начальный индекс в массиве сигналов для соответствующего кода & определяем базовую структуру данных

                    # num_signal, st_struct, size_sruct = self.Signals.get_current_signals_num_read(fd)

                    if (flag_sinhronozation == True) and (self.flag_meas == True):
                        # read Arduino
                        data = self.serial.read(size_sruct)

                        time_0 = time.perf_counter()
                        #if len(data) > 23:
                        #    print('length data: ' + str(len(data)))



                        if len(data) > 0:

                            unpack_data__curent_val_BS = self.Signals.unpack_data(data)  # curent_val_BS
                            if unpack_data__curent_val_BS["name_tag_code"] > 0 and unpack_data__curent_val_BS["name_tag_code"] < 11:
                                try:
                                    List_nums_signal_added = self.Signals.add_value_to_Signals(unpack_data__curent_val_BS)
                                    List_nums_signal_for_prepere.extend(List_nums_signal_added)
                                    if len( List_nums_signal_for_prepere) ==0:
                                        count_not_successful_data_in_a_row += 1
                                except:
                                    List_nums_signal_added = []
                                    print('err SM self.Signals.add_value_to_Signals. unpack_data__curent_val_BS["name_tag_code"]:' + str(unpack_data__curent_val_BS["name_tag_code"]))
                                    count_not_successful_data_in_a_row+= 1
                                    if count_not_successful_data_in_a_row > 10:
                                        self.Signals.set_time_shift()
                                        self.reconnect_com_port()
                                # nL=len(List_nums_signal_added)
                            else:
                                List_nums_signal_added = []
                                print(
                                    'err SM self.Signals.add_value_to_Signals. unpack_data__curent_val_BS["name_tag_code"]:' + str(
                                        unpack_data__curent_val_BS["name_tag_code"]))
                            time_00 = time.perf_counter() - time_0
                            # print('data prep:' + str(time_00))
                            # time_fig = (time.perf_counter() - self.time_start_fig)
                            time_fig = (time.perf_counter() - self.time_start_fig)
                            # time_0 = time.perf_counter()
                            if (time_fig > 0.03) and len( List_nums_signal_for_prepere) > 0:  # self.Figs_mdi.time_limit: # 0.15:
                                count_not_successful_data_in_a_row = 0
                                b = set(List_nums_signal_for_prepere)
                                List_nums_signal_for_prepere = list(b)
                                for i in List_nums_signal_for_prepere:
                                    self.Signals_propety_figs[i].flag_prepered = False
                                self.pushButton_Stop_Meas.isChecked()

                            # hr2 = threading.Timer(0.15, self.visual_effects_at_time_build_graph)
                            # thr2.start()
                            #     #    #self.Signals.array_signals[i].add_value_to_signal(x, y)
                            #   self.Signals_propety_figs[i].prepear_data(self.Signals.array_signals[i])
                            #         self.Signals_propety_figs[i].build_fig_mdi()
                            #  time_1=time.perf_counter()-time_0
                            # self.Signals_propety_figs[num_sig].prepear_data - вызывается в self.build_graph_by_Fig_arr

                            # time_2 = time.perf_counter() - time_1
                            # self.build_graph_by_Fig_arr()
                            self.time_start_fig = time.perf_counter()
                        else:
                            print('data=0')

                        try:
                           self.visual_effects_at_time_build_graph()

                        except:
                            print('err SM visual_effects_at_time_build_graph()')

        # thr1.join()
        # thr1.cancel()
        ff = self.checkBox_Write_Save_Data.isChecked()
        if ff == True:
            self.work_with_file.save_data(self.Signals)

        self.flag_meas = False

        if flag_continuously == False:
            self.progressBar_Time_Measure.setValue(100)
            self.progressBar_Time_Measure.update()

        self.Signals.set_time_shift()
        # for i in range(len(self.Signals.array_signals)):
        #     # self.Signals.array_signals[i].time_shift = self.Signals.array_signals[i].time_arr.ravel()[-1]
        #     if len(self.Signals.array_signals[i].time_arr) > 0:
        #         self.Signals.array_signals[i].time_shift = self.Signals.array_signals[i].time_arr[-1]

        self.pushButton_Start_Meas.setStyleSheet('color: black;')

    def test_threading(self):
        print('test_threading ' + str(self.cur_time))

        thr_test_ = threading.Timer(1, self.test_threading)
        thr_test_.start()

    def build_graph(self, time_pause):

        if self.flag_meas == False:
            while self.flag_meas == False:
                pass
        else:
            # List_nums_signal_added = self.Signals.add_value_to_Signals(unpack_data__curent_val_BS)

            for i in range(0, len(self.Signals_propety_figs), 1):  # List_nums_signal_added:
                #    #self.Signals.array_signals[i].add_value_to_signal(x, y)
                self.Signals_propety_figs[i].prepear_data(self.Signals.array_signals[i])
                self.Signals_propety_figs[i].build_fig_mdi()
                time.sleep(time_pause)

    def visual_effects_at_time_build_graph(self):
        if self.flag_meas == False:
            while self.flag_meas == False:
                return
                # pass
        else:
            time_fig = (time.perf_counter() - self.timing_build_graph)
            time_upd_proc = (time.perf_counter() - self.timing_update_processing)
            if time_fig > self.Figs_mdi.time_limit:  # 0.15:
                # for i in List_nums_signal_added:
                #    self.Signals_propety_figs[i].flag_prepered = False
                #     #    #self.Signals.array_signals[i].add_value_to_signal(x, y)
                #   self.Signals_propety_figs[i].prepear_data(self.Signals.array_signals[i])
                #         self.Signals_propety_figs[i].build_fig_mdi()

                # self.Signals_propety_figs[num_sig].prepear_data - вызывается в self.build_graph_by_Fig_arr
                self.signals_propety_figs_prepear_data()
                time_0 = time.perf_counter()
                self.build_graph_by_Fig_arr()
                time_1 = time.perf_counter() - time_0
                #     # print('time_fig=', time_fig )
                #

                # for i in range(n):
                #     self.Signals.array_signals[i].add_value_to_signal(x, y)
                #     self.Signals_propety_figs[i].prepear_data(self.Signals.array_signals[i])
                #
                if time_upd_proc > 4:
                    # self.Signals_propety_figs[i].build_fig()
                    #    if c % 5 == 0:  # % -- mod  if  round(tt) % 0.2 == 0:
                    time_0 = time.perf_counter()
                    if self.flag_continuously == False:
                        self.progressBar_Time_Measure.setValue(round(self.cur_time / self.time_end * 100))
                        self.progressBar_Time_Measure.update()

                        # time.sleep(50 / 1000)
                    else:
                        self.progressBar_Time_Measure.setValue(0)
                        self.progressBar_Time_Measure.update()
                    # print('bui')
                    self.timing_update_processing = time.perf_counter()
                    time_11 = time.perf_counter() - time_0
                    # print('time upd: '+str(time_11))
                    # print('time fig: ' + str(time_1))
                self.timing_build_graph = time.perf_counter()

    def signals_propety_figs_prepear_data(self):
        if self.flag_meas == True:
            # List_nums_signal_added = self.Signals.add_value_to_Signals(unpack_data__curent_val_BS)

            for i in range(0, len(self.Figs_mdi.Figs_arr), 1):  # перебор по всем инициализированным окнам
                if len(self.Figs_mdi.Figs_arr[i].numbers_signal) > 0:
                    for k in range(0, len(self.Figs_mdi.Figs_arr[i].numbers_signal), 1):
                        num_sig = self.Figs_mdi.Figs_arr[i].numbers_signal[k]
                        if self.Signals_propety_figs[num_sig].flag_prepered == False:
                            self.Signals_propety_figs[num_sig].prepear_data(self.Signals.array_signals[num_sig])

    def build_graph_by_Fig_arr(self):

        # if self.flag_meas == False:
        #     while self.flag_meas == False:
        #         pass
        if self.flag_meas == True:
            # # List_nums_signal_added = self.Signals.add_value_to_Signals(unpack_data__curent_val_BS)
            #
            # for i in range(0, len(self.Figs_mdi.Figs_arr), 1):  # перебор по всем инициализированным окнам
            #     if len(self.Figs_mdi.Figs_arr[i].numbers_signal)>0:
            #         for k in range(0, len(self.Figs_mdi.Figs_arr[i].numbers_signal), 1):
            #             num_sig = self.Figs_mdi.Figs_arr[i].numbers_signal[k]
            #             if self.Signals_propety_figs[num_sig].flag_prepered == False:
            #                 self.Signals_propety_figs[num_sig].prepear_data(self.Signals.array_signals[num_sig])

            # for i in range(0,len(self.Signals_propety_figs),1) : # List_nums_signal_added:
            #    #    #self.Signals.array_signals[i].add_value_to_signal(x, y)
            #    self.Signals_propety_figs[i].prepear_data(self.Signals.array_signals[i])

            self.Figs_mdi.build_fig_mdi()
            # for i in range(0, len(self.Figs_mdi.Figs_arr), 1):
            #     self.Signals_propety_figs[i].build_fig_mdi()
            #     #time.sleep(time_pause)

    # def create_MDI(self, Signals_propety_figs, unit_time):
    #     # https://coderlessons.com/tutorials/python-technologies/izuchite-pyqt/pyqt-mnogodokumentnyi-interfeis
    #     # https://www.youtube.com/watch?v=CvWl-Rhy2wI
    #
    #     # https://www.pythonguis.com/tutorials/creating-multiple-windows/   Creating additional windows
    #
    #     #n = len(self.Signals_propety_figs)
    #    # for i in range(n):
    #
    #     # windows_mdi = self.mdiArea.subWindowList()
    #     # for i, wind in enumerate(windows_mdi):
    #     #     child = wind.widget()
    #
    #
    #     if (Signals_propety_figs.flag_show == True) and (Signals_propety_figs.inited_mdi == False):
    #         self.SM_Win.countWin = self.SM_Win.countWin + 1
    #         #self.Signals_propety_figs[i].init_fig_mdi(unit_time)
    #
    #         container = QWidget()  # QtWidgets()
    #         self.drawAreaLayout = QVBoxLayout(container)  #
    #         self.drawAreaLayout.addWidget(Signals_propety_figs.canvas)
    #         self.drawAreaLayout.addWidget(Signals_propety_figs.toolBar)
    #         # layout = QVBoxLayout(self.drawAreaLayout)
    #         # layout.addWidget(self.canvas)
    #
    #         x = [0]
    #         y = [0]
    #
    #         sub = QMdiSubWindow()
    #         sub.setWidget(container)  #
    #         name_mdi_win="Sub Wind " + str(Signals_propety_figs.number_fig);
    #         sub.setWindowTitle(name_mdi_win)
    #         sub.setObjectName(name_mdi_win)
    #
    #         self.mdiArea.addSubWindow(sub)
    #         self.mdiArea.tileSubWindows()  # Располагает подокна в MDiArea плиточным способом
    #         sub.show()
    #
    #        # fig_plt = self.figure  # (55, figsize=(6, 4))
    #       #  fig_axes = self.figure.add_subplot(111)
    #         # fig_axes.xlabel('', fontsize=12)
    #         # fig_axes.ylabel('', fontsize=12)
    #         Signals_propety_figs.fig_axes.plot(x, y)
    #         # plt.show()
    #         Signals_propety_figs.inited_mdi=True
    #         Signals_propety_figs.canvas.draw()
    #
    #     self.mdiArea.tileSubWindows()  # выравнивание окон
    #     return Signals_propety_figs
    #
    #
    #     #   !!!!!!!!!!!!!!!!освобждение памяти https://evileg.com/en/forum/topic/1229/
    #
    #   #  self.area_List = self.mdiArea.subWindowList()
    #   #  self.area[3].setActiveSubWindow(1)
    def create_MDI_ver2(self, Figs_arr_current):
        # https://coderlessons.com/tutorials/python-technologies/izuchite-pyqt/pyqt-mnogodokumentnyi-interfeis
        # https://www.youtube.com/watch?v=CvWl-Rhy2wI

        # https://www.pythonguis.com/tutorials/creating-multiple-windows/   Creating additional windows

        # n = len(self.Signals_propety_figs)
        # for i in range(n):

        # windows_mdi = self.mdiArea.subWindowList()
        # for i, wind in enumerate(windows_mdi):
        #     child = wind.widget()

        # if (Signals_propety_figs.flag_show == True) and (Signals_propety_figs.inited_mdi == False):
        # self.SM_Win.countWin = self.SM_Win.countWin + 1  # не контролируется 21.01.2023
        # self.Signals_propety_figs[i].init_fig_mdi(unit_time)

        container = QWidget()  # QtWidgets()
        self.drawAreaLayout = QVBoxLayout(container)  #
        self.drawAreaLayout.addWidget(Figs_arr_current.canvas)
        self.drawAreaLayout.addWidget(Figs_arr_current.toolBar)
        # layout = QVBoxLayout(self.drawAreaLayout)
        # layout.addWidget(self.canvas)

        x = [0]
        y = [0]

        sub = My_MdiSubWindow()  # QMdiSubWindow()
        sub.my__init__()
        sub.figs_arr = self.Figs_mdi
        sub.setWidget(container)  #
        name_mdi_win = "Fig_" + str(Figs_arr_current.number_fig);
        sub.setWindowTitle(name_mdi_win)
        sub.setObjectName(name_mdi_win)
        sub.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        # QMdiSubWindow.closeEvent.connect(self.closeWinMdiArea)
        self.mdiArea.addSubWindow(sub)
        self.mdiArea.tileSubWindows()  # Располагает подокна в MDiArea плиточным способом

        sub.show()

        time.sleep(0.2)

        #  # fig_plt = self.figure  # (55, figsize=(6, 4))
        # #  fig_axes = self.figure.add_subplot(111)
        #   # fig_axes.xlabel('', fontsize=12)
        #   # fig_axes.ylabel('', fontsize=12)
        #   Signals_propety_figs.fig_axes.plot(x, y)
        #   # plt.show()
        #   Signals_propety_figs.inited_mdi=True
        #   Signals_propety_figs.canvas.draw()

        self.mdiArea.tileSubWindows()  # выравнивание окон
        # return Signals_propety_figs
        return sub

        #   !!!!!!!!!!!!!!!!освобждение памяти https://evileg.com/en/forum/topic/1229/

    #  self.area_List = self.mdiArea.subWindowList()
    #  self.area[3].setActiveSubWindow(1)
    def clicked_pushButton_set_tile_windows_mdi(self):
        self.mdiArea.tileSubWindows()

    def create_MDI_test(self, unit_time):
        # https://coderlessons.com/tutorials/python-technologies/izuchite-pyqt/pyqt-mnogodokumentnyi-interfeis
        # https://www.youtube.com/watch?v=CvWl-Rhy2wI

        # https://www.pythonguis.com/tutorials/creating-multiple-windows/   Creating additional windows

        n = len(self.Signals_propety_figs)
        for i in range(n):

            if i == 0:
                SM_Win.countWin = SM_Win.countWin + 1
                # self.Signals_propety_figs[i].init_fig(unit_time)

                self.figure = Figure()
                self.canvas = FigureCanvas(self.figure)
                self.toolBar = NavigationToolbar(self.canvas, self)

                container = QWidget()  # QtWidgets()
                self.drawAreaLayout = QVBoxLayout(container)  #
                self.drawAreaLayout.addWidget(self.canvas)
                self.drawAreaLayout.addWidget(self.toolBar)
                # layout = QVBoxLayout(self.drawAreaLayout)
                # layout.addWidget(self.canvas)

                x = [1, 2, 3, 4]
                y = [0, 0.5, 1, 0.2]

                sub = QMdiSubWindow()
                sub.setWidget(container)  #
                sub.setWindowTitle("Sub Wind " + str(self.Signals_propety_figs[i].number_fig))

                self.mdiArea.addSubWindow(sub)
                self.mdiArea.tileSubWindows()  # Располагает подокна в MDiArea плиточным способом
                sub.show()

                fig_plt = self.figure  # (55, figsize=(6, 4))
                fig_axes = fig_plt.add_subplot(111)
                # fig_axes.xlabel('', fontsize=12)
                # fig_axes.ylabel('', fontsize=12)
                fig_axes.plot(x, y)
                # plt.show()
                self.canvas.draw()

            else:
                SM_Win.countWin = SM_Win.countWin + 1
                self.Signals_propety_figs[i].init_fig(unit_time)
                # MDIWindow.count = MDIWindow.count +1
                sub = QMdiSubWindow()
                sub.setWidget(QDialog())
                sub.setWindowTitle("Sub Wind " + str(self.Signals_propety_figs[i].number_fig))

                self.mdiArea.addSubWindow(sub)
                self.mdiArea.tileSubWindows()  # Располагает подокна в MDiArea плиточным способом
                sub.show()

                fig_plt = plt.figure(55, figsize=(6, 4))
                fig_axes = fig_plt.add_subplot(111)
                fig_axes.plot(0, 0)
                plt.xlabel('', fontsize=12)
                plt.ylabel('', fontsize=12)
                plt.show()
                plt.draw()

        #   !!!!!!!!!!!!!!!!освобждение памяти https://evileg.com/en/forum/topic/1229/

        self.area_List = self.mdiArea.subWindowList()
        self.area[3].setActiveSubWindow(1)


class My_MdiSubWindow(QMdiSubWindow):
    sigClosed = pyqtSignal(str)

    def my__init__(self):
        self.figs_arr = class_build_graph.class_build_figs()

    def closeEvent(self, event):
        """Get the name of active window about to close
        https://stackoverflow.com/questions/62504519/pyqt5-qmdiarea-subclass-with-a-custom-signal-on-close
      """
        name_obj_win = self.objectName()
        num_obj_win = name_obj_win[4:]  # delete "Fig_"
        result_serch = self.figs_arr.find_numFigs_arr_by_numMdiAreawin(num_obj_win)
        if result_serch['Flag'] == True:
            nn = result_serch['numFigs_arr']
            self.figs_arr.Figs_arr.pop(nn)

        self.sigClosed.emit(self.windowTitle())

        QMdiSubWindow.closeEvent(self, event)


class CustomComboBox(QComboBox):
    popupAboutToBeShown = pyqtSignal()

    def __init__(self, parent=None):
        super(CustomComboBox, self).__init__(parent)

    #     Функция SPOPUP
    def showPopup(self):
        # Сначала опустошена оригинальная опция
        self.clear()
        # self.insertItem(0, «Пожалуйста, выберите серийный номер реле»)
        index = 1
        # Получить всю последовательную информацию для доступа, вставить в вариант Combobox
        portlist = self.get_port_list(self)
        if portlist is not None:
            for i in portlist:
                self.insertItem(index, i)
                index += 1
        QComboBox.showPopup(self)  #

    @staticmethod
    # Получить все номера последовательных портов
    def get_port_list(self):
        try:
            portList = []
            ports = QSerialPortInfo().availablePorts()
            self.clear()
            for port in ports:
                portList.append(port.portName())
                self.addItems(portList)

            # port_list = list(serial.tools.list_ports.comports())
            # for port in port_list:
            #     yield str(port)
        except Exception as e:
            logging.error(
                "Получить все устройства последовательных портов для доступа! \ N сообщение об ошибке:" + str(e))


class Class_Tabl_Show_Signals(QTableWidget):
    # def __init__(self, QTableWidget):

    #    self.tabl_Show_Signals=self.Create_tabl_Show_Signals(object)
    def __int__(self):
        self.table_Show_Signals = QTableWidget()

    def Create_tabl_Show_Signals(self, obj):
        # QTableWidget.__init__(self)#super(QTableWidget, self).__init__() #
        table_Show_Signals = QTableWidget(obj)  # Create a table  obj - родительский объект
        table_Show_Signals.setColumnCount(7)  # Set three columns
        table_Show_Signals.setRowCount(1)  # and one row
        table_Show_Signals.setHorizontalHeaderLabels(
            ["Name", "Cod", "Shw", "Num.Fig", "k", " Sh", "W"])  # Set the table headers

        # "Name" - имя сигнала - str
        # "Sh" - показать - 1, спрятать - 0
        # "Num.Fig" - номер фигуры (рисунка)
        # "k" - масштабный коэффициент - сигнал умножается на данное значение
        # "W" - в отдельном окне - 1; во внутреннем окне - 0 QMdiArea

        # for i in range(table_Show_Signals.rowCount()):
        #    table_Show_Signals.setRowHeight(i, 5)

        table_Show_Signals.setColumnWidth(0, 1)  # "Name"
        table_Show_Signals.setColumnWidth(1, 1)  # "cod"
        table_Show_Signals.setColumnWidth(2, 15)  # "Shw, \
        table_Show_Signals.setColumnWidth(3, 5)  # "Num.Fig",
        table_Show_Signals.setColumnWidth(4, 5)  # "k", \
        table_Show_Signals.setColumnWidth(5, 8)  # Shift - смещение
        table_Show_Signals.setColumnWidth(6, 4)  # "W"  # W - в отдельном окне
        table_Show_Signals.setColumnWidth(7, 4)  #

        c = 0
        for dict_key in list_signals.keys():  # имена сигналов     range(len(
            a = list_signals[dict_key]
            if a == True:
                if c != 0:
                    table_Show_Signals.insertRow(c)
                table_Show_Signals.setRowHeight(c, 5)
                st = dict_key
                table_Show_Signals.setItem(c, 0, QTableWidgetItem(st))  # выводит имя сигнала в таблицу в 0 колонку

                check_box = self.create_checkbox()
                check_box.setObjectName(
                    'check_box_of_table_Show_Signals_Name_signal_Show_signal_' + dict_key)  # Sh - показать/спрятать сигнал
                table_Show_Signals.setCellWidget(c, 2, check_box)

                table_Show_Signals.setItem(c, 3, QTableWidgetItem(
                    str(c)))  # Num.Fig номер фигуры (по умолчанию в отдельном окне
                table_Show_Signals.setItem(c, 4, QTableWidgetItem(
                    str(1)))  # k - коэффициент усиления ; 0 - нормировка на максимум
                table_Show_Signals.setItem(c, 5, QTableWidgetItem(str(0)))  # Shift - смещение

                check_box2 = self.create_checkbox()  # W - в отдельном окне
                check_box2.num_row = c
                check_box2.setObjectName('check_box_of_table_Show_Signals_Name_signal_Separate_wind_' + dict_key)
                table_Show_Signals.setCellWidget(c, 6, check_box2)

                c += 1
                # table_Show_Signals.itemChanged.connect(self.table_Show_Signals_itemChanged) # собітие изменение самой таблицы , а не значений
            # table_Show_Signals.cellChanged.connect(self.table_Show_Signals_cellChanged)

        # self.table_Show_Signals=table_Show_Signals

        self.table_Show_Signals = table_Show_Signals
        self.table_Show_Signals.cellChanged.connect(self.table_Show_Signals_cellChanged)  # переназначается віше
        # return self.table_Show_Signals

    def update_table_Show_Signals(self, Signals: clas_for_signals.Signals_general):

        self.table_Show_Signals.setRowCount(1)  # and one row
        c = 0
        c2 = 0
        for name_signal in Signals.names_list:  # имена сигналов  ВСЕХ   range(len(
            # a = list_signals[Signals.name_tag]
            a = list_signals[Signals.name_tag_list[
                c2]]  # в сигнале указывается к какой группе он относится. поэтому извлекаем имя группы
            if a == True:
                if c != 0:
                    self.table_Show_Signals.insertRow(c)
                self.table_Show_Signals.setRowHeight(c, 5)
                st = name_signal
                st = Signals.name_alias_list[c]
                self.table_Show_Signals.setItem(c, 0, QTableWidgetItem(st))  # выводит имя сигнала в таблицу в 0 колонку

                st = str(Signals.array_signals[c].name_cod)
                st = st + '.' + str(Signals.array_signals[c].sub_cod)
                self.table_Show_Signals.setItem(c, 1, QTableWidgetItem(st))  # общий код сигнала, например, 7.1

                check_box = self.create_checkbox()
                check_box.setObjectName(
                    'check_box_of_table_Show_Signals_Name_signal_Show_signal_' + name_signal)  # Sh - показать/спрятать сигнал
                self.table_Show_Signals.setCellWidget(c, 2, check_box)

                self.table_Show_Signals.setItem(c, 3, QTableWidgetItem(
                    str(c)))  # Num.Fig номер фигуры (по умолчанию в отдельном окне
                self.table_Show_Signals.setItem(c, 4, QTableWidgetItem(
                    str(1)))  # k - коэффициент усиления ; 0 - нормировка на максимум
                self.table_Show_Signals.setItem(c, 5, QTableWidgetItem(str(0)))  # Shift - смещение

                check_box2 = self.create_checkbox()  # W - в отдельном окне
                check_box2.num_row = c
                check_box2.setObjectName('check_box_of_table_Show_Signals_Name_signal_Separate_wind_' + name_signal)
                self.table_Show_Signals.setCellWidget(c, 6, check_box2)

                c += 1
        c2 += 1
        # table_Show_Signals.itemChanged.connect(self.table_Show_Signals_itemChanged) # собітие изменение самой таблицы , а не значений
        # table_Show_Signals.cellChanged.connect(self.table_Show_Signals_cellChanged)

        # self.table_Show_Signals=table_Show_Signals

        # self.table_Show_Signals = table_Show_Signals
        self.table_Show_Signals.cellChanged.connect(self.table_Show_Signals_cellChanged)  # переназначается віше
        # self.table_Show_Signals

    def create_checkbox(self):
        Widget = QtWidgets.QWidget()
        pCheckBox = QtWidgets.QCheckBox()
        pLayout = QtWidgets.QHBoxLayout(Widget)
        pLayout.addWidget(pCheckBox)
        pLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)  # for PyQt5 :  QtCore.Qt.AlignCenter
        pLayout.setContentsMargins(0, 0, 0, 0)
        Widget.setLayout(pLayout)
        # Widget.clicked.connect(self.itemChanged_check_box_table)
        return Widget

    def itemChanged_check_box_table(self):
        obj = self.table_Show_Signals.sender()  # https://pythonworld.ru/gui/pyqt5-eventssignals.html
        n = obj.num_row
        # https://ru.stackoverflow.com/questions/1030872/%D0%9F%D1%80%D0%BE%D0%B1%D0%BB%D0%B5%D0%BC%D0%B0-%D1%81-sender-%D0%B2-pyqt5
        # name_obj = obj.objectName()
        # name_obj = name_obj[9:]  # удаляем тип виджита из имени
        # list_signals[name_obj] = obj.isChecked()

        n = self.num_row

    def table_Show_Signals_cellChanged(self, row, col):
        # print(item.row())
        # a=item.row()
        # b = item.column()
        a = row
        b = col
        print(row)


class BlitManager:
    def __init__(self, canvas, animated_artists=()):
        """
        Parameters
        ----------
        canvas : FigureCanvasAgg
            The canvas to work with, this only works for sub-classes of the Agg
            canvas which have the `~FigureCanvasAgg.copy_from_bbox` and
            `~FigureCanvasAgg.restore_region` methods.

        animated_artists : Iterable[Artist]
            List of the artists to manage
        """
        self.canvas = canvas
        self._bg = None
        self._artists = []

        for a in animated_artists:
            self.add_artist(a)
        # grab the background on every draw
        self.cid = canvas.mpl_connect("draw_event", self.on_draw)

    def on_draw(self, event):
        """Callback to register with 'draw_event'."""
        cv = self.canvas
        if event is not None:
            if event.canvas != cv:
                raise RuntimeError
        self._bg = cv.copy_from_bbox(cv.figure.bbox)
        self._draw_animated()

    def add_artist(self, art):
        """
        Add an artist to be managed.

        Parameters
        ----------
        art : Artist

            The artist to be added.  Will be set to 'animated' (just
            to be safe).  *art* must be in the figure associated with
            the canvas this class is managing.

        """
        if art.figure != self.canvas.figure:
            raise RuntimeError
        art.set_animated(True)
        self._artists.append(art)

    def _draw_animated(self):
        """Draw all of the animated artists."""
        fig = self.canvas.figure
        for a in self._artists:
            fig.draw_artist(a)

    def update(self):
        """Update the screen with animated artists."""
        cv = self.canvas
        fig = cv.figure
        # paranoia in case we missed the draw event,
        if self._bg is None:
            self.on_draw(None)
        else:
            # restore the background
            cv.restore_region(self._bg)
            # draw all of the animated artists
            self._draw_animated()
            # update the GUI state
            cv.blit(fig.bbox)
        # let the GUI event loop process anything it has to do
        cv.flush_events()


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
