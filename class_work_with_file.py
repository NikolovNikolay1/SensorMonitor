# class_work_with_file  ver.0.0.0.1

import pickle
import scipy.io as sio  #https://coderlessons.com/tutorials/python-technologies/uchitsia-stsipi/scipy-vkhod-i-vykhod
import clas_for_signals

class class_work_with_file:

    def __init__(self):
        self.ver = '0.0.0.1'
        self.path_dir = ''
        self.file_name = ''
        self.ext = ''
        self.full_name = self.path_dir + '/' + self.file_name + self.ext
        self.list_ext = ['.mat', 'non']

    def save_data(self, data):

        if self.ext == '.mat':
            self.save_to_mat(data)

    def save_to_mat(self, data:clas_for_signals.Signals_general):

        try:
            full_name = self.path_dir + '/' + self.file_name + self.ext

            dict={'names_list_pack': data.names_list_pack,
                  'name_cod_list_pack': data.name_cod_list_pack,
                  'name_tag_list': data.name_tag_list,
                  'names_list': data.names_list,
                  'name_cod_list':data.name_cod_list,
                  'conditions_comments':data.conditions_comments}
            n=len(data.array_signals)
            for i in range(n):
                name = 'signal_' + str(i)
                time = 'time_' + str(i)
                sign = 'sign_' + str(i)
                signal_dic={name: data.array_signals[i].name,
                            time: data.array_signals[i].time_arr,
                            sign: data.array_signals[i].y_arr}

                dict.update(signal_dic)

            sio.savemat(full_name, dict) #{'Signals': data}

            #with open(full_name, "wb") as file:
            #    pickle.dump(data, file)
        except:
            print("error write to .mat file")
