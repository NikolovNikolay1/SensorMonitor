# class_signals
# ver 0.0.0.1

# списки Python.v.JavaScript -- https://ischurov.github.io/pythonvjs/show/lists-arrays/ru/
# массив объектов https://coderoad.ru/2674139/%D0%9C%D0%B0%D1%81%D1%81%D0%B8%D0%B2-%D0%BE%D0%B1%D1%8A%D0%B5%D0%BA%D1%82%D0%BE%D0%B2-%D1%81-%D0%BF%D0%BE%D0%BC%D0%BE%D1%89%D1%8C%D1%8E-numpy

import numpy as np


class Base_struct():
    def __init__(self):
        self.Base_struct_unsigned_int = {
            "Base_struct": "Base_struct_unsigned_int",
            "name_tag_code": 0,
            "name_tag": "",
            "time": 0,
            "val": 0,
            "crc": 0
        }
        self.Base_struct_int = {
            "Base_struct": "Base_struct_int",
            "name_tag_code": 0,
            "name_tag": "",
            "time": 0,
            "val": 0,
            "crc": 0
        }
        self.Base_struct_float = {
            "Base_struct": "Base_struct_float",
            "name_tag_code": 0,
            "name_tag": "",
            "time": 0,
            "val": 0,
            "crc": 0
        }
    # Base_struct_string = {
    #     "Base_struct": "Base_struct_float",
    #     "name_tag_code": 0,
    #     "name_tag" : "",
    #     "time" : 0,
    #     "val": 0,
    #     "crc": 0
    # }


class Signals_general():
    def __init__(self):
        self.names_list = []
        self.type_struct = ""
        self.name_cod_list = []
        self.array_signals = []  # Signal_one() # type is Signal_one
        self.dt_mean = 1  # sec

    def create_signal(self, signal_property):
        if len(self.array_signals) == 0:
            self.array_signals = Signal_one()

        self.array_signals.append(signal_property)  # signal_property - class Signal_one
        self.names_list.append(signal_property.name)
        self.name_cod_list.append(signal_property.name_cod)

    def add_value_to_signal(self, signal):  # signal - Base_struct
        L = len(self.names_list)
        c = 0
        for name_cod in range(self.name_cod_list):

            if name_cod == signal.name_tag_cod:
                self.array_signals[c].time_arr.append(signal["time"])
                self.array_signals[c].y_arr.append(signal["val"])  # необходимо добавить калибровку

                break
            c += 1


class Signal_one():
    def __init__(self):
        self.name = ""
        self.name_cod = bytes([
                                  0])  # byte ! - порядковый номер сигнала, должен быть согласовон с ардуино.  https://www.delftstack.com/ru/howto/python/how-to-convert-int-to-bytes-in-python-2-and-python-3/
        self.time_arr = []
        self.y_arr = []
        self.y_filtr_arr = []
        self.calibrovka = 1  # калибровочные данные (необходимо сделать ссылку на функцию)

        self.time_unit = ""
        self.y_unit = ""

        self.windows_flag = False  # разрешает/запрещает рассчеты в окне
        self.windows_descret_count = 2048  # в отсчетах  интервал усреднения
        self.windows_float_counr = 0  # в отсчетах
        self.windows_descret_time = 2048  # по времени
        self.windows_float_time = 0  # по времени

        self.std_y_wind = []
        self.disp_y_wind = []

        self.windows_spectr_flag = False  # разрешает/запрещает рассчеты спектра Фурье в окне
        self.spectr_points = 1024
        self.windows_descret_spectr_Freq_of_y = []  # двухмерный массив х (i) - время ; y (j)- частоты
        self.windows_descret_spectr_Pow_of_y = []  # двухмерный массив х (i) - время ; y (j)- мощность

        self.conditions_comments = ""


    def pri(self):
        print('hh')