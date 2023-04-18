# class_for_signals
# ver 0.0.0.1

# списки Python.v.JavaScript -- https://ischurov.github.io/pythonvjs/show/lists-arrays/ru/
# массив объектов https://coderoad.ru/2674139/%D0%9C%D0%B0%D1%81%D1%81%D0%B8%D0%B2-%D0%BE%D0%B1%D1%8A%D0%B5%D0%BA%D1%82%D0%BE%D0%B2-%D1%81-%D0%BF%D0%BE%D0%BC%D0%BE%D1%89%D1%8C%D1%8E-numpy
from typing import List, Any

import numpy as np
import struct
import numpy as np

import clas_for_signals


class Base_struct:
    def __init__(self):
        self.Base_struct_unsigned_int = {
            "Base_struct": "Base_struct_unsigned_int",
            "name_tag_code": 0,
            "name_tag": "",
            "time": 0,
            "val": 0,
            "crc": 0,
            "Base_struct_pack_cod": ""
        }
        self.Base_struct_int = {
            "Base_struct": "Base_struct_int",
            "name_tag_code": 0,
            "name_tag": "",
            "time": 0,
            "val": 0,
            "crc": 0,
            "Base_struct_pack_cod": ""
        }
        self.Base_struct_float = {
            "Base_struct": "Base_struct_float",
            "name_tag_code": 0,
            "name_tag": "",
            "time": 0,
            "val": 0,
            "crc": 0,
            "Base_struct_pack_cod": ""
        }
        self.Base_struct_float_diff_temperature = {  # // == 11 byte
            "Base_struct": "Base_struct_float_diff_temperature",

            "size_from_arduino": 23,
            "struct_from_arduino": '<hLffffb',
            # // соответствие типов данных С++ и Python  https://docs.python.org/3/library/struct.html#struct.calcsize
            # // размер типов для ардуино уточнять!!! на https://doc.arduino.ua/ru/prog

            "count_signals": 4,
            "name_tag_code": 0,  # // 2 byte   (- TO arduino; + FROM arduino; 0 - unAssign
            "time": 0,  # // 4 byte  unsigned long
            "val_0": 0,  # // 4 byte   float
            "val_1": 0,  # // 4 byte float
            "val_R_0": 0,  # // 4 byte float
            "val_R_1": 0,  # // 4 byte  float
            "crc": 0,  # // 1 byte  char

            "val_list_name": {
                "time": '',
                "val_0": '',
                "val_1": '',
                "val_R_0": '',
                "val_R_1": '',
                "crc": '',
            },  # соответствие между именами сигналов в yamal файле и в базовой структуре

            "list_sub_cod": {
                "time": 0,  # 0 - всегда время
                "val_0": 1,
                "val_1": 2,
                "val_R_0": 3,
                "val_R_1": 4,
                "crc": 5,  # 0 - всегда последний
            }  # соответствие между субкодом сигналов в yamal файле и в базовой структуре
        }

        self.Base_struct_float_humidity_temper = {  # // == 11 byte
            "Base_struct": "Base_struct_float_humidity_temper",

            "size_from_arduino": 15,
            "struct_from_arduino": '<hLffb',
            # // соответствие типов данных С++ и Python  https://docs.python.org/3/library/struct.html#struct.calcsize
            # // размер типов для ардуино уточнять!!! на https://doc.arduino.ua/ru/prog

            "count_signals": 2,
            "name_tag_code": 0,  # // 2 byte   (- TO arduino; + FROM arduino; 0 - unAssign
            "time": 0,  # // 4 byte  unsigned long
            "val_0": 0,  # // 4 byte   float
            "val_1": 0,  # // 4 byte float
            "crc": 0,  # // 1 byte  char

            "val_list_name": {
                "time": '',
                "val_0": '',
                "val_1": '',
                "crc": '',
            },  # соответствие между именами сигналов в yamal файле и в базовой структуре

            "list_sub_cod": {
                "time": 0,  # 0 - всегда время
                "val_0": 1,
                "val_1": 2,
                "crc": 3,  # 0 - всегда последний
            }  # соответствие между субкодом сигналов в yamal файле и в базовой структуре
        }

    def assignment(self, name_structure):

        Base_struct = 'Base_struct_unsigned_int'
        if name_structure == 'Base_struct_unsigned_int':
            Base_struct = self.Base_struct_unsigned_int
        elif name_structure == 'Base_struct_int':
            Base_struct = self.Base_struct_int
        elif name_structure == 'Base_struct_float':
            Base_struct = self.Base_struct_float
        elif name_structure == 'Base_struct_float_diff_temperature':
            Base_struct = self.Base_struct_float_diff_temperature
        elif name_structure == 'Base_struct_float_humidity_temper':
            Base_struct = self.Base_struct_float_humidity_temper
        return Base_struct
    # Base_struct_string = {
    #     "Base_struct": "Base_struct_float",
    #     "name_tag_code": 0,
    #     "name_tag" : "",
    #     "time" : 0,
    #     "val": 0,
    #     "crc": 0,
    #     "Base_struct_pack_cod" = ""
    # }


class Signals_general:
    #

    def __init__(self):
        self.names_list_pack = []
        self.name_cod_list_pack = []
        self.name_tag_list = []
        self.names_list = []
        self.name_alias_list = []
        self.type_struct = ""
        self.name_cod_list = []
        self.array_signals = []  # Signal_one() # type is Signal_one
        self.dt_mean = 1  # sec
        self.conditions_comments = ""

        self.current_signals = {
            'signals_num_read': 0,
            'st_struct': "",
            'size_sruct': 0,
            'cod_signal': 0
        }
        self.current_signals_num_read = 0
        self.Base_struct_list = []
        self.signals_begin_index_in_array = []

    def create_signal(self, name_signal_package, yaml_property_signal):
        # signal_property:
        # names_list  -- append to self.names_list
        # name_signal_package - name from list_signals (см. Сенсор Монитор)
        n = len(yaml_property_signal['Signals'])
        dict_ = yaml_property_signal['Signals']
        dict_keys = list(dict_)
        self.names_list_pack.append(name_signal_package)
        self.name_cod_list_pack.append(yaml_property_signal['name_code'])
        BS = Base_struct()
        self.Base_struct_list.append(BS.assignment(yaml_property_signal['Base_struct']))

        k = len(self.array_signals)
        self.signals_begin_index_in_array.append(k)

        for i in range(n):  # проходим по всем подсигналам
            # name_signal=name_signal_package +'_' + str(dict_keys[i])

            # # если не создан ниодин сигнал
            # if len(self.array_signals) == 0:
            #     self.array_signals = Signal_one()

            Signal = self.set_params_signal(str(dict_keys[i]), yaml_property_signal)
            self.names_list.append(Signal.name)  # Signal.name = name_signal_package + '_' +str(dict_keys[i])
            ##############

            self.array_signals.append(Signal)  # signal_property - class Signal_one
            self.name_tag_list.append(name_signal_package)
            self.name_cod_list.append(Signal.name_cod)
            self.name_alias_list.append(Signal.alias)

    def set_params_signal(self, name_signal, yaml_property_signal):
        Signal = Signal_one()
        # можн сделать двумя строчками, но не понятно как обращаться к свойству объекта если это свойство задано строкой
        # кроме єто так лучеш контролировать и в случае нерреализованных свойств комментировать

        Signal.name = yaml_property_signal['name_tag'] + '__' + name_signal
        Signal.name_cod = yaml_property_signal[
            'name_code']  # # byte ! - порядковый номер сигнала, должен быть согласовон с ардуино.  https://www.delftstack.com/ru/howto/python/how-to-convert-int-to-bytes-in-python-2-and-python-3/
        Signal.name_tag = yaml_property_signal[
            'name_tag']  # дублирующее имя, но может отличаться. Все программное обращение по self.name
        Signal.time_arr = []
        Signal.y_arr = []
        Signal.y_filtr_arr = []
        BS = Base_struct()
        Signal.Base_struct = BS.assignment(yaml_property_signal['Base_struct'])
        # if yaml_property_signal['Base_struct'] == 'Base_struct_unsigned_int':
        #     Signal.Base_struct = BS.Base_struct_unsigned_int
        # elif yaml_property_signal['Base_struct'] == 'Base_struct_int':
        #     Signal.Base_struct = BS.Base_struct_int
        # elif yaml_property_signal['Base_struct'] == 'Base_struct_float':
        #     Signal.Base_struct = BS.Base_struct_float

        # поиск подсигнала в yaml_property_signal
        n = len(yaml_property_signal['Signals'])
        dict_ = yaml_property_signal['Signals']
        dict_keys = list(dict_)
        for key in dict_keys:
            if key == name_signal:
                one_yaml_property_signal = yaml_property_signal['Signals'][key]
                s_temp = one_yaml_property_signal['fun_calibrovki']
                if s_temp != '':
                    Signal.calibrovka = eval(
                        'self.' + s_temp)  # калибровочные данные (необходимо сделать ссылку на функцию)
                else:
                    Signal.calibrovka = self.empty_calibrovka

                Signal.time_unit = ""
                Signal.y_unit = one_yaml_property_signal['unit']
                Signal.alias = one_yaml_property_signal['alias']
                Signal.sub_cod = one_yaml_property_signal['sub_cod']
                Signal.filtr_impuls_able_y = one_yaml_property_signal['filtr_impuls_able_y']
                break
        # дополнительные параметры на будущее

        Signal.windows_flag = False  # разрешает/запрещает рассчеты в окне
        Signal.windows_descret_count = 10  # в отсчетах  интервал усреднения
        Signal.windows_float_counr = 0  # в отсчетах
        Signal.windows_descret_time = 2048  # по времени
        Signal.windows_float_time = 0  # по времени

        Signal.std_y_wind = []
        Signal.disp_y_wind = []

        Signal.windows_spectr_flag = False  # разрешает/запрещает рассчеты спектра Фурье в окне
        Signal.spectr_points = 1024
        Signal.windows_descret_spectr_Freq_of_y = []  # двухмерный массив х (i) - время ; y (j)- частоты
        Signal.windows_descret_spectr_Pow_of_y = []  # двухмерный массив х (i) - время ; y (j)- мощность

        Signal.conditions_comments = ""
        return Signal

    def check_signal_inited(self, name_signal):
        # проверка , инициализирован ли сигнал
        flag = False
        for name_signal_inited in (self.names_list):
            if name_signal == name_signal_inited:
                flag = True
        return flag

    def add_value_to_Signals(self, signal_Base_struct):  # signal - Base_struct
        L = len(self.names_list)
        List_nums_signal_added = []
        c = 0
        signal_Base_struct_cod = signal_Base_struct['name_tag_code']
        try:
            name_cod_start_in_arr = self.name_cod_list.index(signal_Base_struct_cod)
        except:
            print(signal_Base_struct_cod)

        c = name_cod_start_in_arr

        dict_keys = list(signal_Base_struct["list_sub_cod"])
        fffff=0
        crc_temp=round(signal_Base_struct['crc'], 2)
        if crc_temp == 1: # в случаи переполнения
            for i in range(len(self.array_signals)):
                if len(self.array_signals[i].time_arr) > 0:
                    self.array_signals[i].time_shift = self.array_signals[i].time_arr[-1]
                    fffff=1
            signal_Base_struct['crc'] = 0

        if (signal_Base_struct['crc']) == 0:  # если не произошла ошибка передачи данных
            for i in range(signal_Base_struct['count_signals']):
                kay_sub_cod = dict_keys[i + 1]  # 0 - всегда время
                # st_kay_sub_kod=signal_Base_struct[kay_sub_cod]
                # self.array_signals[c+i].time_arr.append(signal_Base_struct["time"])

                t1 = signal_Base_struct["time"]
                t1 = t1 + self.array_signals[c + i].time_shift  # time_shift определяется в процедуре Миас основного кода
                # if len(self.array_signals[c + i].time_arr) > 2:
                #     t0 = self.array_signals[c + i].time_arr.ravel()[-1]  # последее значение. можно и по индексу [-1]
                #
                #     if t1 < t0:
                #         t1 = t1 + self.array_signals[c + i].time_shift  # time_shift определяется в процедуре Миас основного кода
                if t1<1000:
                    a=self.array_signals[c + i].time_arr
                self.array_signals[c + i].time_arr = np.append(self.array_signals[c + i].time_arr, t1)

                for j in range(0, signal_Base_struct['count_signals'], 1):
                    if self.array_signals[c + i + j].sub_cod == signal_Base_struct["list_sub_cod"][kay_sub_cod]:
                        # self.array_signals[c+i+j].y_arr.append(signal_Base_struct[kay_sub_cod])
                        #print("signal_Base_struct[kay_sub_cod]==" +str(signal_Base_struct[kay_sub_cod]))
                        #print("kay_sub_cod==" + str(kay_sub_cod))
                        try:
                            y = signal_Base_struct[kay_sub_cod]
                            y, flag = self.array_signals[c + i + j].calibrovka(y)
                        except Exception as e:
                            fl = True
                            print("ee add value signal signal_Base_struct[kay_sub_cod]==" + str(signal_Base_struct[kay_sub_cod]))
                            print("kay_sub_cod==" + str(kay_sub_cod))

                        if not flag:  # должно быть эквивалентно flag==False
                            ny = len(self.array_signals[c + i + j].y_arr)
                            if ny > 3:
                                y = self.array_signals[c + i + j].y_arr[ny - 1]
                        self.array_signals[c + i + j].y_arr = np.append(self.array_signals[c + i + j].y_arr, y)
                        self.array_signals[c + i + j]= self.filtr_impuls_able_y(self.array_signals[c + i + j])
                        List_nums_signal_added.append(c + i + j)
                        break
        return List_nums_signal_added

        # for name_cod in (self.name_cod_list): # list without "range"
        #
        #     if name_cod == signal_Base_struct.name_tag_cod:
        #         self.array_signals[c].time_arr.append(signal_Base_struct["time"])
        #         self.array_signals[c].y_arr.append(signal_Base_struct["val"])  # необходимо добавить калибровку
        #
        #         break
        #     c += 1

    def filtr_impuls_able_y(self, signal__one):
        L = len(signal__one.y_arr)
        w = signal__one.windows_descret_count
        if L > w + 2:
            try:
                std = np.std(signal__one.y_arr[L - w:L - 1])
                signal__one.std_y_wind = np.append(signal__one.std_y_wind, std)
                if signal__one.filtr_impuls_able_y == True:
                    mean = np.mean(signal__one.y_arr[L - w:L - 1])
                    d=np.max([std , abs(7*mean+0.1*mean)])
                    for i in range(1,w, 1):
                        if signal__one.y_arr[L - i -1] > mean + d or signal__one.y_arr[L - i - 1] < mean - d:

                            if abs(signal__one.y_arr[L - i]) > abs(signal__one.y_arr[L - i - 1] + d) and abs(
                                    signal__one.y_arr[L - i]) > abs(signal__one.y_arr[L - i + 1] + d) or abs(signal__one.y_arr[
                                L - i]) < abs(signal__one.y_arr[L - i - 1] - d) and abs(
                                    signal__one.y_arr[L - i]) < abs(signal__one.y_arr[L - i + 1] - d):
                                print("i=" + str(i))
                                print("y=" + str(signal__one.y_arr[L - i]))
                                signal__one.y_arr[L - i] = (signal__one.y_arr[L - i - 1] + signal__one.y_arr[L - i + 1]) / 2
                        if signal__one.time_arr[i+1]>signal__one.time_arr[i+2] or signal__one.time_arr[i+1]<signal__one.time_arr[i] :
                            signal__one.time_arr[i + 1]=(signal__one.time_arr[i]+signal__one.time_arr[i+2])/2

            except:
                print("err filtr_impuls_able_y")
        return signal__one

    def empty_calibrovka(self, y):
        y = y
        flag = True
        return y, flag

    def fun_calibrovki_sensor_T0(self, y):
        # пока это ток
        y = y
        flag = True
        return y, flag

    def fun_calibrovki_sensor_T1(self, y):
        y = y
        flag = True
        return y, flag

    def fun_calibrovki_sensor_R1(self, y):
        y = y / 47
        flag = True
        return y, flag

    def fun_calibrovki_sensor_AHT25_x38_T(self, y):
        flag = True
        if y > 80:
            y = 80
            flag = False
        return y, flag

    def fun_calibrovki_sensor_AHT25_x38_H(self, y):
        flag = True
        if y > 100:
            y = 100
            flag = False
        return y, flag

    def add_value_to_signal_test(self, x, y):  # signal - Base_struct
        L = len(self.names_list)

    #     c = 0
    #     for name_cod in range(self.name_cod_list):
    #
    #         if name_cod == signal_Base_struct.name_tag_cod:
    #             self.array_signals[c].time_arr.append(x)
    #             self.array_signals[c].y_arr.append(y)  # необходимо добавить калибровку
    #
    #             break
    #         c += 1

    def get_current_signals_num_read(self, num_cod):

        c = 0
        st_struct = ''
        size_sruct = 0

        f = False
        for i in self.name_cod_list_pack:
            if i == num_cod:
                self.current_signals_num_read = c
                BS = self.Base_struct_list[c]
                st_struct = BS["struct_from_arduino"]
                size_sruct = BS["size_from_arduino"]
                name_cod = self.array_signals[c].name_cod

                self.current_signals['signals_num_read'] = c
                self.current_signals['st_struct'] = st_struct
                self.current_signals['size_sruct'] = size_sruct
                self.current_signals['cod_signal'] = name_cod

                f = True
                break
            c += 1
        if f == False:
            c = -1
        return c, st_struct, size_sruct

    def unpack_data(self, data):
        tup = [0, 0]
        st_struct = self.current_signals['st_struct']
        # print(st_struct)
        try:
            tup = struct.unpack(st_struct, data)
        except:
            tup = [0, 0]
            print(st_struct)

        c = self.current_signals['signals_num_read']
        curent_val_BS = self.Base_struct_list[c]

        name_structure = curent_val_BS["Base_struct"]

        if name_structure == 'Base_struct_unsigned_int':
            Base_struct = self.Base_struct_unsigned_int
            # data2 = data[0:Base_struct["size_from_arduino"]]
            # tup = struct.unpack(st_struct, data2)
        elif name_structure == 'Base_struct_int':
            Base_struct = self.Base_struct_int
            # data2 = data[0:Base_struct["size_from_arduino"]]
            # tup = struct.unpack(st_struct, data2)
        elif name_structure == 'Base_struct_float':
            Base_struct = self.Base_struct_float
            # data2 = data[0:Base_struct["size_from_arduino"]]
            # tup = struct.unpack(st_struct, data2)
        elif name_structure == 'Base_struct_float_diff_temperature':

            # data2 = data[0:curent_val_BS["size_from_arduino"]]

            try:
                curent_val_BS["name_tag_code"] = tup[0]
                curent_val_BS["time"] = tup[1]
                curent_val_BS["val_0"] = tup[2]
                curent_val_BS["val_1"] = tup[3]
                curent_val_BS["val_R_0"] = tup[4]
                curent_val_BS["val_R_1"] = tup[5]
                curent_val_BS["crc"] = tup[6]
            except:
                print('name_tag_code---tup[0] must be 7= ' + str(tup[0]))
                curent_val_BS["name_tag_code"] = -1

        elif name_structure == 'Base_struct_float_humidity_temper':

            # data2 = data[0:curent_val_BS["size_from_arduino"]]

            try:
                curent_val_BS["name_tag_code"] = tup[0]
                curent_val_BS["time"] = tup[1]
                curent_val_BS["val_0"] = tup[2]
                curent_val_BS["val_1"] = tup[3]
                curent_val_BS["crc"] = tup[4]
            except:
                print('name_tag_code---tup[0] must be 7= ' + str(tup[0]))
                curent_val_BS["name_tag_code"] = -1

        # curent_val_BS['val_list']=
        return curent_val_BS

    def clear_data(self):
        n = len(self.array_signals)
        for i in range(n):
            self.array_signals[i].time_arr = []
            self.array_signals[i].y_arr = []
            self.array_signals[i].time_shift = 0

    def set_time_shift(self):
        # если данные не обнулялись, то время должно осчитываться от  time_shift
        for i in range(len(self.array_signals)):
            # self.Signals.array_signals[i].time_shift = self.Signals.array_signals[i].time_arr.ravel()[-1]
            if len(self.array_signals[i].time_arr) > 0:
                self.array_signals[i].time_shift = self.array_signals[i].time_arr[-1]
class Signal_one:
    def __init__(self):
        self.name = ""
        self.name_cod = bytes([
                                  0])  # byte ! - порядковый номер сигнала, должен быть согласовон с ардуино.  https://www.delftstack.com/ru/howto/python/how-to-convert-int-to-bytes-in-python-2-and-python-3/
        self.name_tag = ""  # дублирующее имя, но может отличаться. Все программное обращение по self.name
        self.Base_struct = ""
        self.alias = ""
        self.sub_cod = 0

        self.time_arr = np.array([])
        self.time_shift = 0  # для фиксации времени после остановки
        self.y_arr = np.array([])
        self.y_filtr_arr = []
        self.calibrovka = 1  # калибровочные данные (необходимо сделать ссылку на функцию)

        self.time_unit = ""
        self.y_unit = ""

        self.filtr_impuls_able_y = True

        self.windows_flag = False  # разрешает/запрещает рассчеты в окне
        self.windows_descret_count = 10  # в отсчетах  интервал усреднения
        self.windows_float_counr = 0  # в отсчетах
        self.windows_descret_time = 2048  # по времени ??
        self.windows_float_time = 0  # по времени

        self.std_y_wind = []
        self.disp_y_wind = []

        self.windows_spectr_flag = False  # разрешает/запрещает рассчеты спектра Фурье в окне
        self.spectr_points = 1024
        self.windows_descret_spectr_Freq_of_y = []  # двухмерный массив х (i) - время ; y (j)- частоты
        self.windows_descret_spectr_Pow_of_y = []  # двухмерный массив х (i) - время ; y (j)- мощность

        self.conditions_comments = ""

    def add_value_to_signal(self, x, y):  # signal - Base_struct

        # self.time_arr.append(x)
        # self.y_arr.append(y)  # необходимо добавить калибровку
        self.time_arr = np.append(self.time_arr, x, dtype=np.float32)
        self.y_arr = np.append(self.time_arr, y, dtype=np.float32)  # необходимо добавить калибровку
