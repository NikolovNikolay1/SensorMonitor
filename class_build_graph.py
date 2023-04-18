# slass for draw figurees ver.0.0.0.1

import time

import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QMdiSubWindow
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.animation as animation

import clas_for_signals
import numpy as np

color_list=['blue', 'green', 'red', 'cyan', 'magenta', 'black']

class class_build_figs(object):
    def __init__(self):

        self.ver = '0.0.0.1'

        self.signals_short = clas_for_signals.Signals_general() # содержатся данніе сигналов, только обрезанные, в соответствии с максимальным количеством точек
        #self.signals_short_2 = [clas_for_signals.Signals_general()]
        self.signals_short_2 = [class_propety_figs()]
        self.signals_short_2.clear() # все сигналы
        # self.array_signals = []  # данные х и у
        self.array_propety_figs = []  # данные х и у
        self.Figs_arr = [class_propety_figs()]  #
        self.Figs_arr.clear()
        self.time_limit=0.01
    def prepear_data(self, Signals : clas_for_signals.Signals_general):
          # о  тайпчекинг Аннотации типов в Python - https://semakin.dev/2020/06/type_hints/
            ##############################
          # пока не используется. используется в One- def prepear_data
          #############
        n = len(Signals.names_list)
        c=0
        for name_signal in Signals.names_list:
            n = len(Signals.array_signals[c].time_arr)
           # tp = self.array_propety_figs[c].total_points
            tp = self.array_propety_figs[c].total_points
            if n > tp:
                self.signals_short.array_signals[c].time_arr = Signals.array_signals[c].time_arr[n-1-tp: n-1]
                self.signals_short.array_signals[c].y_arr = Signals.array_signals[c].y_arr[n - 1 - tp: n - 1]
            else:
                self.signals_short.array_signals[c].time_arr = Signals.array_signals[c].time_arr
                self.signals_short.array_signals[c].y_arr = Signals.array_signals[c].y_arr

    #def set_propety_figs(self, tabl_view:):

    #    n=
    #    self.array_propety_figs.

    #def create_figs(self, propety_figs : class_propety_figs):
    def animation_fig_mdi(self):
        #ani=[]
        ani0=[]
        ani1=[]
        for i in range(0, len(self.Figs_arr), 1):  # перебор по всем инициализированным окнам
            #self.Figs_arr[i].build_fig_mdi_Fig_arr_without_timer()
            if i==0:
                ani0=(animation.FuncAnimation(self.Figs_arr[i].fig_plt, self.Figs_arr[i].build_fig_mdi_Fig_arr_without_timer, blit=True, interval=300))
            if i==1:
                ani1=(animation.FuncAnimation(self.Figs_arr[i].fig_plt, self.Figs_arr[i].build_fig_mdi_Fig_arr_without_timer,blit=True, interval=300))


            #self.Figs_arr[i].fig_plt.show()

    def build_fig_mdi(self, non_time_lim=1):
        #arr_signalS_short_for_figs=[clas_for_signals.Signals_general()]

        for i in range(0, len(self.Figs_arr), 1): # перебор по всем инициализированным окнам

            self.Figs_arr[i].build_fig_mdi_Fig_arr()

    def assign_inFigs_arr_arr__signalS_short_for_figs(self):
        # arr_signalS_short_for_figs=[clas_for_signals.Signals_general()]
        arr_signalS_short_for_figs = [clas_for_signals.Signal_one()]

        for i in range(0, len(self.Figs_arr), 1):  # перебор по всем инициализированным окнам
            self.Figs_arr[i].arr_signalS_short_for_figs = [clas_for_signals.Signal_one()]
            arr_signalS_short_for_figs.clear()
            self.Figs_arr[i].arr_signalS_short_for_figs.clear()
            for k in range(0, len(self.Figs_arr[i].numbers_signal), 1):
                num_sig = self.Figs_arr[i].numbers_signal[k]
                if self.signals_short_2[num_sig].flag_show == True:
                    arr_signalS_short_for_figs.append(self.signals_short_2[num_sig].signal_short)
                    self.Figs_arr[i].arr_signalS_short_for_figs.append(self.signals_short_2[num_sig].signal_short)
                    # self.Figs_arr[i].line.append(self.fig_axes.plot(0, 0))
                    # nl=len(self.Figs_arr[i].line)
                    # self.line[nl-1].set_xdata([])
                    # self.line[nl-1].set_ydata([])

            #self.Figs_arr[i].arr_signalS_short_for_figs = arr_signalS_short_for_figs

            # fig=self.Figs_arr[i].fig_axes
            # ani = animation.FuncAnimation(fig, self.Figs_arr[i].build_fig_mdi_Fig_arr, blit=True, interval=500)
    def find_numFigs_arr_by_numMdiAreawin(self, num_obj_win):
        num_obj_win=int(num_obj_win)
        n = len(self.Figs_arr)
        result_serch = {'Flag': False, 'numFigs_arr': -1}
        if n > 0:
            for j in range(n):
                if self.Figs_arr[j].number_fig == num_obj_win:
                    result_serch = {'Flag': True, 'numFigs_arr': j}
                    break
        return result_serch

    def exam_inited_win_mdi(self, number_fig, windows_mdi):
        # проверка, было ли уже открыто окно
        flag_inited_win = False
        num_figs_mdi_opened=-1
        n = len(self.Figs_arr)
        if n > 0:
            flag_inited_arr=False
            for j in range(n):  # n = len(self.Figs_arr)

                if len(self.Figs_arr[j].numbers_signal)>0:
                    if self.Figs_arr[j].number_fig == number_fig:
                        flag_inited_arr = True
                        num_figs_mdi_opened = j

            flag_inited_win = False
            for jj, child in enumerate(windows_mdi):
                #child = wind.widget()
                activateWindow = child.activateWindow()
               # Act_window = self.mdiArea.activeSubWindow()
                name_obj_win = child.objectName()  # имя mdi окна содержит номер фигуры
                # защита, если окно создано, но не полностю настроено
                if name_obj_win == '':
                    name_obj_win = num_figs_mdi_opened
                else:
                    name_obj_win = name_obj_win[4:]  # delete "Fig_"
                    name_obj_win = int(name_obj_win)  #
                if name_obj_win == number_fig:  # заявляемая фигура соответствует уже открітой
                    self.Figs_arr[num_figs_mdi_opened].child_mdi = child
                    self.Figs_arr[num_figs_mdi_opened].inited_mdi = True
                    child.show()
                    flag_inited_win = True
                    #num_figs_mdi_opened = j
                    break
        return [flag_inited_win, num_figs_mdi_opened, flag_inited_arr];

    def add_number_signals(self, number_fig, number_signal):
       n = len(self.Figs_arr)
       if n > 0:
           for j in range(n):
               if number_fig == self.Figs_arr[j].number_fig:
                   self.Figs_arr[j].numbers_signal.append(number_signal)

class class_propety_figs:
    def __init__(self):
        # по существу, все переменные являются массивами
        self.name=''
        self.total_points = 1000
        self.d_point = 1
        self.unit_x = [''] # время визуализации
        self.unit_y = [''] # in general is massiv
        self.number_fig = 0  # по умолчанию номер фигуры соответствует номеру массива
        self.flag_show = False
        self.axes_x_limit=[0, 1]
        self.axes_y_limit = [0, 1]
        self.numbers_signal = [] # сигналы которые будут выводится на один график

        self.coef_scale = 1
        self.coef_scale_x = 1
        self.Shift = 0
        self.Windows_separete = False

        self.signal_short = clas_for_signals.Signal_one() # x,y

        #self.arr_signalS_short_for_figs=[clas_for_signals.Signal_one()]

        self.fig_plt : plt.figure
        self.fig_axes : plt.figure
        self.line : plt.figure.plot
        self.plt : plt
        self.time_cur =0 # время для перепостроения графика
        self.inited_mdi = False
        self.child_mdi : QMdiSubWindow

        self.flag_prepered = False

        self.time_limit = 0.1
        self.time_start=time.perf_counter()
        self.time_unit = ''

    def prepear_data(self, Signal : clas_for_signals.Signal_one):
          # о  тайпчекинг Аннотации типов в Python - https://semakin.dev/2020/06/type_hints/

        # n = len(Signals.names_list)
        # c=0
        # for name_signal in Signals.names_list:
            #time_0 = time.perf_counter()
            self.flag_prepered = False
            n = len(Signal.time_arr)
           # tp = self.array_propety_figs[c].total_points
            tp = self.total_points
            if n > tp*self.d_point:
                #self.signal_short.time_arr = Signal.time_arr[n-1-tp*self.d_point: n-1: self.d_point]
                #self.signal_short.y_arr = Signal.y_arr[n - 1 - tp*self.d_point: n - 1: self.d_point]

                self.signal_short.time_arr = np.array(Signal.time_arr[n - 1 - tp * self.d_point: n - 1: self.d_point],dtype = np.float32)
                self.signal_short.y_arr = np.array(Signal.y_arr[n - 1 - tp * self.d_point: n - 1: self.d_point],dtype = np.float16)
            else:
                if n>self.d_point:
                    #self.signal_short.time_arr = Signal.time_arr[0:n-1:self.d_point]
                    #self.signal_short.y_arr = Signal.y_arr[0:n-1:self.d_point]
                    self.signal_short.time_arr = np.array(Signal.time_arr[0:n-1:self.d_point],dtype = np.float32)
                    self.signal_short.y_arr = np.array(Signal.y_arr[0:n-1:self.d_point],dtype = np.float16)
                else:
                    self.signal_short.time_arr = np.array(Signal.time_arr[0:n],dtype = np.float32)
                    self.signal_short.y_arr = np.array(Signal.y_arr[0:n],dtype = np.float16)

            if len(self.signal_short.time_arr) == 0:
                self.signal_short.time_arr =np.array( 0 , dtype = np.float32)
                self.signal_short.time_arr=np.append(self.signal_short.time_arr, 0)
                self.signal_short.y_arr = np.array( 0, dtype = np.float16)
                self.signal_short.y_arr = np.append(self.signal_short.y_arr, 0)

            #time_1 = time.perf_counter() - time_0
            # калибровка по времени
            #k=self.coef_scale_x
            #self.signal_short.time_arr=[value * k for value in self.signal_short.time_arr]

            n=np.size(self.signal_short.time_arr)
            if (self.coef_scale_x != 1) or (self.coef_scale != 1) or (self.Shift != 0):
                #for i in range(n):
                #    self.signal_short.time_arr[i]=self.coef_scale_x*self.signal_short.time_arr[i]
                #    self.signal_short.y_arr[i]=self.coef_scale * self.signal_short.y_arr[i] + self.Shift
                self.signal_short.time_arr[:] = self.coef_scale_x*self.signal_short.time_arr[:]
                self.signal_short.y_arr[:] = self.coef_scale * self.signal_short.y_arr[:] + self.Shift
                #print('prepere_data: '+str(time_1))
            self.flag_prepered = True

    def init_fig(self, unit_time):
        # пока каждый график инициализируется отдельно,
        # т.е. размер массива будет равен количеству сигналов,
        # но при построении они могут не отображаться или перенаправляться в другое окно
        #self.plt = plt()
        if self.flag_show == True:
            self.fig_plt = plt.figure(self.number_fig, figsize=(6, 4))
            self.fig_axes = self.fig_plt.add_subplot(111) # один график.

       # self.plt.ion() # включает итеративній режим

            self.line, = self.fig_axes.plot(0, 0)
            self.line.set_xdata([])
            self.line.set_ydata([])
            self.fig_axes.set_xlim(0, 1)
            self.fig_axes.set_ylim(0, 1)

            plt.xlabel('', fontsize=12)
            plt.ylabel('', fontsize=12)
            plt.xlabel('Время, [' + unit_time +']', fontsize=12)
            plt.ylabel('Амплитуда, ['+self.unit_y[0] +']', fontsize=12)


            plt.show(block=False)#

            plt.pause(0.1)

            #plt.ion()
            plt.draw()

    def init_fig_mdi(self, unit_time, objj):
        # пока каждый график инициализируется отдельно,
        # т.е. размер массива будет равен количеству сигналов,
        # но при построении они могут не отображаться или перенаправляться в другое окно
        #self.plt = plt()
        if self.flag_show == True:

            self.fig_plt = Figure() #plt.figure(self.number_fig, figsize=(6, 4))
            #self.fig_plt2=plt.figure()
            self.fig_axes = self.fig_plt.add_subplot(111, xlabel='x', ylabel='y') # один график.
            plt.rcParams.update({'font.size': 8})

            self.canvas = FigureCanvas(self.fig_plt)
            self.toolBar = NavigationToolbar(self.canvas, objj)

       # self.plt.ion() # включает итеративній режим

            # see assign_inFigs_arr_arr__signalS_short_for_figs
            self.line,=self.fig_axes.plot(0, 0)
            self.line.set_xdata([])
            self.line.set_ydata([])


            self.fig_axes.set_xlim(0, 1)
            self.fig_axes.set_ylim(0, 1)
            self.fig_plt.set_animated(True)
            self.canvas.draw()

          #  self.xlabel= plt.xlabel('', fontsize=12)
          #  self.ylabel = plt.ylabel('Амплитуда, ['+self.unit_y[0] +']', fontsize=12)
           #plt.xlabel('', fontsize=12)
           # plt.ylabel('', fontsize=12)
           # plt.xlabel('Время, [' + unit_time +']', fontsize=12)
           # plt.ylabel('Амплитуда, ['+self.unit_y[0] +']', fontsize=12)


           # plt.show(block=False)#

           # plt.pause(0.1)

           # plt.ion()
          #  plt.draw()


    def build_fig(self):
        if self.flag_show == True:

            self.time_cur = (time.perf_counter() -self.time_start) # seconds

            if self.time_cur>0: #self.time_limit:

                self.fig_plt
                m=min(self.signal_short.time_arr)
                M= max(self.signal_short.time_arr)
                if m==M:
                    M=m+1

                self.fig_axes.set_xlim(m,M)
                m=min(self.signal_short.y_arr)
                M= max(self.signal_short.y_arr)
                if m==M:
                    M=m+1
                self.fig_axes.set_ylim(m, M)
                self.line.set_xdata(self.signal_short.time_arr)
                self.line.set_ydata(self.signal_short.y_arr)
                plt.draw()

                plt.pause(0.01)
                self.time_start=time.perf_counter()
                self.time_cur= 0

    def build_fig_mdi(self):
        if (self.flag_show == True) and (self.inited_mdi==True):

            self.time_cur = (time.perf_counter() -self.time_start) # seconds

            if self.time_cur>0: #self.time_limit:

                self.fig_plt
                m=min(self.signal_short.time_arr)
                M= max(self.signal_short.time_arr)
                if m==M:
                    M=m+1

                self.fig_axes.set_xlim(m,M)
                m=min(self.signal_short.y_arr)
                M= max(self.signal_short.y_arr)
                if m==M:
                    M=m+1
                self.fig_axes.set_ylim(m, M)

                if len(self.signal_short.time_arr)==0:
                    self.signal_short.time_arr= [0]
                    self.signal_short.y_arr = [0]
                self.line.set_xdata(self.signal_short.time_arr)
                self.line.set_ydata(self.signal_short.y_arr)
                self.canvas.draw()

               # plt.draw()

               # plt.pause(0.01)
                self.time_start=time.perf_counter()
                self.time_cur= 0

    def build_fig_mdi_Fig_arr(self ):
        n = len(self.arr_signalS_short_for_figs)
        plt.rcParams.update({'font.size': 8})
        #if len(self.arr_signalS_short_for_figs[0].y_arr)==0:


        self.time_cur = (time.perf_counter() - self.time_start) # seconds
        if n>0:
            #time_0 = time.perf_counter()
            if self.time_cur > self.time_limit:
            #if (arr_signalS_short_for_figs.flag_show == True): # and (self.inited_mdi==True):

                #mi_ma = self.min_max_arr_arr(arr_signalS_short_for_figs)

                mi_ma = self.min_max_arr_arr_NUMpy(self.arr_signalS_short_for_figs)

                min_t = mi_ma[0]
                max_t = mi_ma[1]
                min_y = (mi_ma[2])
                max_y = (mi_ma[3])

                try:
                    if min_t == max_t:
                        self.fig_axes.set_xlim(min_t - 0.01, max_t + 0.01)
                    else:
                        self.fig_axes.set_xlim(min_t, max_t)

                    if min_y == max_y:
                        self.fig_axes.set_ylim(min_y - 0.01, max_y + 0.01)
                    else:
                        self.fig_axes.set_ylim(min_y-0.02*min_y, max_y+0.02*max_y)
                except:
                    name_cod=self.arr_signalS_short_for_figs.name_cod
                    print('err class_build_graph.build_fig_mdi_Fig_arr(self ) name_cod' +str(name_cod))
                # if len(arr_signalS_short_for_figs.time_arr)==0:
                #     arr_signalS_short_for_figs.time_arr= [0]
                #     arr_signalS_short_for_figs.y_arr = [0]

                #t=np.asfarray(arr_signalS_short_for_figs[0].time_arr, dtype=np.float32)
               # self.line.set_xdata(self.arr_signalS_short_for_figs[0].time_arr)
                 #self.line.set_xdata(t)
              #  self.line.set_ydata(self.arr_signalS_short_for_figs[0].y_arr)

                list_t = [self.arr_signalS_short_for_figs[i].time_arr for i in range(n)]
                list_y = [self.arr_signalS_short_for_figs[i].y_arr for i in range(n)]
                list_c = [color_list[i] for i in range(n)]
                for i in range(n):
                    if i==0 and (len(self.fig_axes.lines)==1):
                        self.line.set_xdata(self.arr_signalS_short_for_figs[i].time_arr)
                        self.line.set_ydata(self.arr_signalS_short_for_figs[i].y_arr)
                    else:
                        if (len(self.fig_axes.lines)<i+1):
                            self.line=self.fig_axes.plot(self.arr_signalS_short_for_figs[i].time_arr, self.arr_signalS_short_for_figs[i].y_arr)
                        if len(self.fig_axes.lines)==n:
                            self.fig_axes.lines[i].set_xdata(self.arr_signalS_short_for_figs[i].time_arr)
                            self.fig_axes.lines[i].set_ydata(self.arr_signalS_short_for_figs[i].y_arr)
                #self.line.set_color(list_c)
                #self.line.rc('')
                #time_1 = time.perf_counter() - time_0
               # [self.fig_axes.lines[i].set_color(color) for i, color in enumerate(list_c)]
                self.canvas.draw()
            # функция  plt.gcf().canvas.flush_events() используется, чтобы дать возможность пакету matplotlib обработать свои внутренние события, в том числе и те, что отвечают за перерисовку окна.
                self.canvas.flush_events()
                #self.fig_axes.plot(self.arr_signalS_short_for_figs[0].time_arr, self.arr_signalS_short_for_figs[0].y_arr )
               # plt.draw()

                #plt.pause(0.1)
                self.time_start=time.perf_counter()
                self.time_cur= 0
               # time_2 = time.perf_counter()-time_0
               # print('buil fig prep in class: ' + str(time_1))
               # print('buil fig in class: '+str(time_2))
    def build_fig_mdi_Fig_arr_without_timer(self ):
        self.arr_signalS_short_for_figs[0].time_arr[0]=0
        self.arr_signalS_short_for_figs[0].time_arr[1] = 0.1
        self.arr_signalS_short_for_figs[0].y_arr[0]=0
        self.arr_signalS_short_for_figs[0].y_arr[1] = 0.1

        n = len(self.arr_signalS_short_for_figs)
        self.line.set_xdata([])
        self.line.set_ydata([])
        #if len(self.arr_signalS_short_for_figs[0].y_arr)==0:


       # self.time_cur = (time.perf_counter() - self.time_start) # seconds
        self.time_cur=1
        if n>0:
            time_0 = time.perf_counter()
            if self.time_cur > 0:
            #if (arr_signalS_short_for_figs.flag_show == True): # and (self.inited_mdi==True):

                #mi_ma = self.min_max_arr_arr(arr_signalS_short_for_figs)

                mi_ma = self.min_max_arr_arr_NUMpy(self.arr_signalS_short_for_figs)

                min_t = mi_ma[0]
                max_t = mi_ma[1]
                min_y = (mi_ma[2])
                max_y = (mi_ma[3])



                #self.fig_plt
                # m=min(arr_signalS_short_for_figs.time_arr)
                # M= max(arr_signalS_short_for_figs.time_arr)
                # if m==M:
                #     M=m+1
                #
                #
                # m=min(arr_signalS_short_for_figs.y_arr)
                # M= max(arr_signalS_short_for_figs.y_arr)
                # if m==M:
                #     M=m+1
                if min_t+0.01*min_t == max_t+0.01*max_t:
                    self.fig_axes.set_xlim(min_t - 0.01, max_t + 0.01)
                    self.fig_axes.set_ylim(min_y - 0.01, max_y + 0.01)
                else:
                    self.fig_axes.set_xlim(min_t-0.01*min_t, max_t+0.01*max_t)
                    self.fig_axes.set_ylim(min_y-0.01*min_y, max_y+0.01*max_y)

                # if len(arr_signalS_short_for_figs.time_arr)==0:
                #     arr_signalS_short_for_figs.time_arr= [0]
                #     arr_signalS_short_for_figs.y_arr = [0]

                #t=np.asfarray(arr_signalS_short_for_figs[0].time_arr, dtype=np.float32)
                self.line.set_xdata(self.arr_signalS_short_for_figs[0].time_arr)
                #self.line.set_xdata(t)
                self.line.set_ydata(self.arr_signalS_short_for_figs[0].y_arr)
                #time_1 = time.perf_counter() - time_0

                self.canvas.draw()
               # функция canvas.flush_events() используется, чтобы дать возможность пакету matplotlib обработать свои внутренние события, в том числе и те, что отвечают за перерисовку окна.
                self.canvas.flush_events()
                #self.fig_axes.plot(self.arr_signalS_short_for_figs[0].time_arr, self.arr_signalS_short_for_figs[0].y_arr )
               # plt.draw()

                #plt.pause(0.1)
                self.time_start=time.perf_counter()
                self.time_cur= 0
                time_2 = time.perf_counter()-time_0
               # print('buil fig prep in class: ' + str(time_1))
                print('buil fig in class: '+str(time_2))

    def min_max_arr_arr(self, arr_arr):

        n = len(arr_arr)
        m=1e6
        M=-1e6
        mi_x = []
        ma_x = []
        mi_y = []
        ma_y = []
        mi_ma = []
        for i in range(n):
            mm=min(arr_arr[i].time_arr)
            mi_x.append(mm)
            MM=max(arr_arr[i].time_arr)
            ma_x.append(MM)

            mm = min(arr_arr[i].y_arr)
            mi_y.append(mm)
            MM = max(arr_arr[i].y_arr)
            ma_y.append(MM)

        mi_ma.append(min(mi_x))
        mi_ma.append(max(ma_x))
        mi_ma.append(min(mi_y))
        mi_ma.append(max(ma_y))

        return mi_ma

    def min_max_arr_arr_NUMpy(self, arr_arr):

        n = len(arr_arr)
        m=1e6
        M=-1e6
        mi_x = np.array([], dtype=np.float16)
        ma_x = np.array([], dtype=np.float16)
        mi_y = np.array([], dtype=np.float16)
        ma_y = np.array([], dtype=np.float16)
        mi_ma = np.array([], dtype=np.float16)
        for i in range(n):
            mm=np.min(arr_arr[i].time_arr)
            mi_x=np.append(mi_x, mm)
            MM=np.max(arr_arr[i].time_arr)
            ma_x=np.append(ma_x, MM)

            mm = np.min(arr_arr[i].y_arr)
            mi_y=np.append(mi_y, mm)
            MM = np.max(arr_arr[i].y_arr)
            ma_y=np.append(ma_y, MM)
            if (np.isinf(MM)==True) or (np.isinf(mm)==True):
                print("")

        mi_ma=np.append(mi_ma, np.min(mi_x))
        mi_ma=np.append(mi_ma, np.max(ma_x))
        mi_ma=np.append(mi_ma, np.min(mi_y))
        mi_ma=np.append(mi_ma, np.max(ma_y))

        return mi_ma
