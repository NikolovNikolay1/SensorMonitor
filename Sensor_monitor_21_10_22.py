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
# пример фильтра событий https://digitrain.ru/questions/47960494/
from PyQt5.QtCore import pyqtSignal
import logging  # для отладки и сообщений  об ошибках  https://khashtamov.com/ru/python-logging/
from PyQt5.QtCore import QIODevice
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation

import numpy as np
import sys
import serial
import yaml  # https://pyneng.readthedocs.io/ru/latest/book/17_serialization/yaml.html
# https://tonais.ru/library/biblioteka-yaml-v-python
from Model_GUI_base import Ui_MainWindow
import time
import math
import typing # для аннотированных списков
import struct


import clas_for_signals
import class_build_graph


class SM_Win(QtWidgets.QWidget, Ui_MainWindow):
    def __init__(self):
        super().__init__()

        self.MainWindow = MainWindow
        # self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.setupUi(self.MainWindow)

        self.MainWindow.comboBox_ComPort = CustomComboBox(
            self.frame_OpenPort)  # ComboBox_ports(self.frame_OpenPort) #QtWidgets.QComboBox
        # self.MainWindow.comboBox_ComPort = CustomComboBox(self.comboBox_ComPort)
        # self.MainWindow.comboBox_ComPort.place(in_=self.frame_OpenPort, x=20, y=20)
        # https://russianblogs.com/article/54731700043/
        self.MainWindow.comboBox_ComPort.setGeometry(QtCore.QRect(40, 10, 101, 22))

        self.load_last_setting()

        self.MainWindow.table_Show_Signals = Class_Tabl_Show_Signals()  # self.Create_tabl_Show_Signals(self.frame_Signal)
        self.MainWindow.table_Show_Signals.Create_tabl_Show_Signals(self.frame_Signal)
       # self.MainWindow.table_Show_Signals = self.MainWindow.table_Show_Signals.Create_tabl_Show_Signals(
       #     self.frame_Signal)
        self.MainWindow.table_Show_Signals.setGeometry(QtCore.QRect(10, 30, 211, 241))
        self.MainWindow.table_Show_Signals.setObjectName("table_Show_Signals")
        self.table_Show_Signals_assigne_connect_events_of_check_box()

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
        self.pushButton_Start_Meas.clicked.connect(self.clicked_pushButton_Start_Meas)
        self.pushButton_Stop_Meas.clicked.connect(self.clicked_pushButton_Stop_Meas)

        self.Signals = clas_for_signals.Signals_general()
        self.Signals_propety_figs =[] #  : typing.List[class_build_graph.class_propety_figs()]
        self.init_signal()

        # !!!!!!!идет после инициализации сигналов
        self.MainWindow.table_Show_Signals.update_table_Show_Signals(self.Signals)
        #self.MainWindow.table_Show_Signals.itemSelectionChanged.connect(self.table_Show_Signals_changed) # идет после инициализации сигналов

        self.MainWindow.table_Show_Signals.itemChanged.connect(self.table_Show_Signals_changed)  # идет после инициализации сигналов

        # !!!!!!! идет после инициализации таблицы
        self.add_Signals_propety_figs_from_table()  # добавляет сигналы для рисования из таблицы на главной закладке и свойства
        self.serial = []

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

    def table_Show_Signals_assigne_connect_events_of_check_box(self):
        n = self.MainWindow.table_Show_Signals.rowCount()
        for i in range(n):
            p = self.MainWindow.table_Show_Signals.cellWidget(i, 1)
            checkBoxs = p.findChildren(QtWidgets.QCheckBox)[0]
            checkBoxs.clicked.connect(self.table_Show_Signals_changed_checkBoxs)



    def add_Signals_propety_figs_from_table (self):
        # анализируется вся таблица. Необходимо запускать или с самого начала или при глобальном перезапуске

        n = self.MainWindow.table_Show_Signals.rowCount()
        for i in range(n):
            prop_signal_graph = class_build_graph.class_propety_figs()

            name_unit_signal = self.Signals.array_signals[i].time_unit
            prop_signal_graph.unit_x.append(name_unit_signal)
            name_unit_signal = self.Signals.array_signals[i].y_unit
            prop_signal_graph.unit_y.append(name_unit_signal)

            prop_signal_graph.number_fig = self.MainWindow.table_Show_Signals.item(i, 2).text() # "Num.Fig",


            p=self.MainWindow.table_Show_Signals.cellWidget(i, 1)
            checkBoxs =p.findChildren(QtWidgets.QCheckBox)[0]
            prop_signal_graph.flag_show = checkBoxs.checkState() # показывать или нет

            prop_signal_graph.coef_scale = self.MainWindow.table_Show_Signals.item(i, 3).text() # scale
            prop_signal_graph.Shift = self.MainWindow.table_Show_Signals.item(i, 4).text() # Shift

            p = self.MainWindow.table_Show_Signals.cellWidget(i, 5)
            checkBoxs = p.findChildren(QtWidgets.QCheckBox)[0]
            prop_signal_graph.Windows_separete = checkBoxs.checkState()

            self.Signals_propety_figs.append(prop_signal_graph)

    def table_Show_Signals_changed_checkBoxs(self):
        #  анализируется вся таблица т.к. не получается обратиться к конкретному CheckBox и определить номер строки

        # obj = self.MainWindow.sender()
        # if item == QtWidgets.QCheckBox():
        #     a=1
        # else:
        #     a=2
        #   #  row = item.row()
        #   #  col = item.column()
        n = self.MainWindow.table_Show_Signals.rowCount()
        if self.flag_meas == False:

            for i in range(n):

                p = self.MainWindow.table_Show_Signals.cellWidget(i, 1)
                checkBoxs = p.findChildren(QtWidgets.QCheckBox)[0]
                # prop_signal_graph.flag_show = checkBoxs.checkState()
                self.Signals_propety_figs[i].flag_show = bool(checkBoxs.checkState()) # показывать или нет

                p = self.MainWindow.table_Show_Signals.cellWidget(i, 5)
                checkBoxs = p.findChildren(QtWidgets.QCheckBox)[0]
                self.Signals_propety_figs[i].Windows_separete = bool(checkBoxs.checkState()) # показывать или нет

        elif self.flag_meas == True: # во время измерения

            for i in range(n):
                flag_old_show=self.Signals_propety_figs[i].flag_show

                p = self.MainWindow.table_Show_Signals.cellWidget(i, 1)
                checkBoxs = p.findChildren(QtWidgets.QCheckBox)[0]
                # prop_signal_graph.flag_show = checkBoxs.checkState()
                flag_new_show =  bool(checkBoxs.checkState())
                if flag_old_show != flag_new_show:
                    self.Signals_propety_figs[i].flag_show = flag_new_show
                    if flag_new_show ==True:
                        unit_time = self.comboBox_Unit_Time.currentText()
                        self.Signals_propety_figs[i].init_fig(unit_time)



    def table_Show_Signals_changed(self, item):

        i = item.row()
        col = item.column()

        self.Signals_propety_figs[i].name = self.MainWindow.table_Show_Signals.item(i, 0).text()
       # self.Signals_propety_figs[i].time_unit =
        self.Signals_propety_figs[i].number_fig = self.MainWindow.table_Show_Signals.item(i, 2).text()
        self.Signals_propety_figs[i].coef_scale = self.MainWindow.table_Show_Signals.item(i, 3).text()  # scale
        self.Signals_propety_figs[i].Shift = self.MainWindow.table_Show_Signals.item(i, 4).text()  # Shift

        if (self.flag_meas == True) and col == 2:
            unit_time = self.comboBox_Unit_Time.currentText()
            self.Signals_propety_figs[i].init_fig(unit_time)


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
            check_box_widget.setChecked(f)
            list_signals[adc_name] = f
            # check_box_name='self.'+ check_box_name
            # check_box_widget=eval(check_box_name)
            # check_box_widget.setChecked(f)
        pprint(templates)

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

            to_yaml = {
                'Type_Controller_last': Type_Controller_last_val,
                'Link_with_PC_Speeds_last': Link_with_PC_Speeds_last_val,
                "Link_with_PC_Types_last": Link_with_PC_Types_last_val,
                'Meas_Freq_last': Edit_Data_Setting_Meas_Freq_val,
                'Meas_ADC_last': Meas_ADC_last
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
        #portx =self.comboBox_ComPort.currentText() # "COM3"
        bps = int(self.lineEdit_Speed.text())
        #bps = 115200  # 9600
        #bps = 2000000  # 2*921600  # 9600
        # Последовательный порт выполняется до тех пор, пока он не будет открыт, а затем использование команды open сообщит об ошибке
        try:
           # self.Serial = serial()
            ser = serial.Serial(portx, int(bps), timeout=1 )
            self.serial = ser # ,,

            if (self.serial.isOpen()):
                print('open success')
                # self.pushButton_Open_Port.setStyleSheet(
                #     "QPushButton::hover{"
                #     "background-color: #ffd2cf;"
                #     "border: none;"
                #     "}"
                # )
                self.pushButton_Open_Port.setStyleSheet('color: green;')
        except IOError:
            print("Invalid comm port!")
            self.pushButton_Open_Port.setStyleSheet('color: red;')
       # serial.setPortName()
       # serial.open(QIODevice.ReadWrite)

    def clicked_pushButton_Stop_Meas(self):
        self.flag_meas = False

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
        plt.show(block=False)
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

        flag_continuously = self.radioButton_Contitue_time.isChecked()  # флаг непрерывного измерения
        if flag_continuously == True:
            time_end = 1e10
        elif self.radioButton_Limit_Time.isChecked() == True:
            time_end = float(self.lineEdit_Time_Measure.text())  # общее время измерения

        self.progressBar_Time_Measure.setValue(0)
        self.progressBar_Time_Measure.update()

        time_end = time_end
        n=len(self.Signals_propety_figs)
        for i in range(n):
            self.Signals_propety_figs[i].init_fig(unit_time)
        # plt.figure()

        # Когда интерактивный режим установлен в True, график будет вырисовываться только при вызове метода draw ()
        # plt.show()
        # plt.xlabel('Час')
        # plt.ylabel('Сигнал')
        # plt.title('АЦП')

        # https://python-scripts.com/matplotlib
        # https://nbviewer.ipython.org/github/whitehorn/Scientific_graphics_in_python/blob/master/P1%20Chapter%201%20Pyplot.ipynb
        # https://pythonworld.ru/novosti-mira-python/scientific-graphics-in-python.html

        #fig, ax = plt.subplots()
        xdata, ydata = [], []


        # add_subplot -  https://stackoverflow.com/questions/3584805/in-matplotlib-what-does-the-argument-mean-in-fig-add-subplot111
        plt.ion()  # включает итеративній режим

        #x0=[]
        #y0=[]
        fl=False
        try:
            if (self.serial.isOpen()):
                fl=True
        except Exception as e:
            QtWidgets.QMessageBox.about(self, "Error", "Вероятно, порт не открыт. " + str(e))


        if (fl==True) and self.serial.isOpen()  :

            self.flag_meas = True
            time_start = time.perf_counter()  # seconds
            cur_time = 0

            #plt.show()

            c = 1
            while (self.flag_meas == True) and (cur_time <= time_end):
                tt=(time.perf_counter() - time_start)
                cur_time = tt * k

                flag_sinhronozation=False
                while (flag_sinhronozation == False):
                    fd = self.serial.read()
                    fd = int.from_bytes(fd, 'big')
                           # https://russianblogs.com/article/8614986773/
                    if fd == 123:
                        flag_sinhronozation=True

                fd=self.serial.read()
                fd = int.from_bytes(fd, 'big') # считываем код сигнала

                # self.Signals.current_signals_num_read -
                #     определям начальный индекс в массиве сигналов для соответствующего кода & определяем базовую структуру данных
                num_signal, st_struct , size_sruct = self.Signals.get_current_signals_num_read(fd)

                # read Arduino
                data = self.serial.read(size_sruct)
                unpack_data__curent_val_BS = self.Signals.unpack_data(data) # curent_val_BS
                self.Signals.add_value_to_Signals( unpack_data__curent_val_BS)

                # for i in range(n):
                #     self.Signals.array_signals[i].add_value_to_signal(x, y)
                #     self.Signals_propety_figs[i].prepear_data(self.Signals.array_signals[i])
                #
                if c>2:
                   # self.Signals_propety_figs[i].build_fig()
                    if c % 3 == 0:  # % -- mod  if  round(tt) % 0.2 == 0:
                        if flag_continuously == False:
                            self.progressBar_Time_Measure.setValue(round(cur_time/time_end*100))
                            self.progressBar_Time_Measure.update()
                            #time.sleep(50 / 1000)
                        else:
                            self.progressBar_Time_Measure.setValue(0)
                            self.progressBar_Time_Measure.update()
                        time.sleep(50 / 1000)
                #tt=unpack_data
                # # s = sys.getsizeof(data)
                # tup = struct.unpack('<hLfb', data)
                # x0.append(tup[1] / 1000)
                # y0.append(tup[2])
                #
                #
                # s = sys.getsizeof(data)
                # tup = struct.unpack('hhb', data)
                # # print(tup[0])
                # # print(tup[1])
                # # print(tup[2])
                # # time.sleep(0.005)
                #
                # size_sruct = 11
                # data = ser.read(size_sruct)
                # # s = sys.getsizeof(data)
                # tup = struct.unpack('<hLfb', data)
                # x0.append(tup[1] / 1000)
                # y0.append(tup[2])
                #
                # # cur_time = tt * k
                # # x = cur_time
                # # y = math.sin(2 * 3.14 * 10 * x)
                # x0.append(x)
                # y0.append(y)
                # n=len(self.Signals.array_signals)
                # for i in range(n):
                #     self.Signals.array_signals[i].add_value_to_signal(x, y)
                #     self.Signals_propety_figs[i].prepear_data(self.Signals.array_signals[i])
                #
                #     if c>2:
                #         self.Signals_propety_figs[i].build_fig()
                #         if c % 2 == 0:  # % -- mod  if  round(tt) % 0.2 == 0:
                #             if flag_continuously == False:
                #                 self.progressBar_Time_Measure.setValue(round(cur_time/time_end*100))
                #                 self.progressBar_Time_Measure.update()
                #             else:
                #                 self.progressBar_Time_Measure.setValue(0)
                #                 self.progressBar_Time_Measure.update()

                c += 1

        # plt.plot(x0, y0, label='A0')
        #
        self.flag_meas = False
        if flag_continuously == False:
            self.progressBar_Time_Measure.setValue(100)
            self.progressBar_Time_Measure.update()

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
        self.table_Show_Signals.cellChanged.connect(self.table_Show_Signals_cellChanged) # переназначается віше
        # return self.table_Show_Signals

    def update_table_Show_Signals(self, Signals:clas_for_signals.Signals_general):

        self.table_Show_Signals.setRowCount(1)  # and one row
        c = 0
        c2 =0
        for name_signal in Signals.names_list:  # имена сигналов  ВСЕХ   range(len(
           # a = list_signals[Signals.name_tag]
            a = list_signals[Signals.name_tag_list[c2]] # в сигнале указывается к какой группе он относится. поэтому извлекаем имя группы
            if a == True:
                if c != 0:
                    self.table_Show_Signals.insertRow(c)
                self.table_Show_Signals.setRowHeight(c, 5)
                st = name_signal
                st = Signals.name_alias_list[c]
                self.table_Show_Signals.setItem(c, 0, QTableWidgetItem(st))  # выводит имя сигнала в таблицу в 0 колонку

                st=str(Signals.array_signals[c].name_cod)
                st=st + '.' + str(Signals.array_signals[c].sub_cod)
                self.table_Show_Signals.setItem(c, 1, QTableWidgetItem(st)) # общий код сигнала, например, 7.1

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
        c2+=1
                # table_Show_Signals.itemChanged.connect(self.table_Show_Signals_itemChanged) # собітие изменение самой таблицы , а не значений
            # table_Show_Signals.cellChanged.connect(self.table_Show_Signals_cellChanged)

        # self.table_Show_Signals=table_Show_Signals

        #self.table_Show_Signals = table_Show_Signals
        self.table_Show_Signals.cellChanged.connect(self.table_Show_Signals_cellChanged) # переназначается віше
        self.table_Show_Signals

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
        n=obj.num_row
        # https://ru.stackoverflow.com/questions/1030872/%D0%9F%D1%80%D0%BE%D0%B1%D0%BB%D0%B5%D0%BC%D0%B0-%D1%81-sender-%D0%B2-pyqt5
        # name_obj = obj.objectName()
        # name_obj = name_obj[9:]  # удаляем тип виджита из имени
        # list_signals[name_obj] = obj.isChecked()

        n=self.num_row


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
