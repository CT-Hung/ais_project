import serial
from pyais import decode
import pandas as pd
import time
from os.path import exists

from tkinter import filedialog
from tkinter import *
index_columns = ['mmsi', 'shipname', 'shiptype', 'accuracy', 'lon', 'lat', 'course', 'heading', 'speed', 'second', 'time_stamp']

def convertData2DF(AIS_data_dict):
    tmp_data = pd.DataFrame(columns=index_columns)
    for key in index_columns:
        if key in AIS_data_dict:
            tmp_data.at[0, key] = AIS_data_dict[key]
        elif key == 'time_stamp':
            tmp_data.at[0, key] = time.strftime("%Y%m%d_%H:%M:%S", time.localtime())
        else:
            tmp_data.at[0, key] = -1
    return tmp_data
            
            
def storeCSV(data, save_file_path, save_file_prefix, save_file_root):
    file_name = save_file_path+f"/"+save_file_prefix+save_file_root+f".csv"
    data.to_csv(file_name, index=False)    
    print("save file => ", file_name)
        
        
class AisDecode():
    def __init__(self):
        self.ais_seq_buffer = []
        self.ais_seq_info = (-1, -1, -1)
        
    def checkForSequentialData(self, ais_byte_data):
        ais_str_data = ais_byte_data.decode()
        seq_num = int(ais_str_data[7])
        if seq_num == 1:
            return (seq_num, 0, 0)
        elif seq_num > 1:
            seq_th = int(ais_str_data[9])
            seq_id = int(ais_str_data[11])
            return (seq_num, seq_th, seq_id)
        
    def combineSequence(self, ais_byte_data, seq_num, seq_th, seq_id):
        if self.ais_seq_info[2] != seq_id:
            self.ais_seq_buffer = [ais_byte_data]
            #self.ais_seq_buffer.append(ais_str_data)
            self.ais_seq_info = (seq_num, seq_th, seq_id)
            
        elif self.ais_seq_info[2] == seq_id and self.ais_seq_info[1]+1 == seq_th:
            self.ais_seq_buffer.append(ais_byte_data)
            self.ais_seq_info = (seq_num, seq_th, seq_id)
            
        if self.ais_seq_info[0] == self.ais_seq_info[1]:
            return 1
        else:
            return 0
        
    def getAisSequence(self):
        return self.ais_seq_buffer

            
def checkFileCount(save_file_path, save_file_prefix, file_date, file_count):
    while True:
        save_file_root = file_date+"_"+str(file_count)
        file_name = save_file_path+f"/"+save_file_prefix+save_file_root+f".csv"
        if(exists(file_name)):
            file_count += 1
        else:
            return file_count    

#ser.open()
root = Tk()
root.withdraw()
save_file_path = filedialog.askdirectory() # choose dir ui
file_count = 0
file_date = time.strftime("%Y%m%d", time.localtime())
csv_samples_max = 100
#save_file_path = "."
save_file_prefix = "OS_"
file_count = checkFileCount(save_file_path, save_file_prefix, file_date, file_count)

serial_port = "COM3"
data = pd.DataFrame(columns=index_columns)
AIS_decode = AisDecode()

txt_file = 'AIS_log_1.txt'
with open(txt_file, 'rb') as f:
    lines = f.readlines()
    for ais_byte_data in lines: 
        #time.sleep(0.1)
        print(ais_byte_data)
        
        if ais_byte_data.find(b'AIVDM')>0:
            (seq_num, seq_th, seq_id) = AIS_decode.checkForSequentialData(ais_byte_data)
            if seq_num > 1:
                ais_combine_flag = AIS_decode.combineSequence(ais_byte_data, seq_num, seq_th, seq_id)
                if ais_combine_flag == 1:
                    ais_byte_data = AIS_decode.getAisSequence()
                    decoded = decode(*ais_byte_data)
                    new_ais_df = convertData2DF(decoded.asdict())
                    data = pd.concat([data, new_ais_df])
                    print("---------------------------------")
                    print(new_ais_df)
                    print("---------------------------------")
                    
            else:
                decoded = decode(ais_byte_data)
                new_ais_df = convertData2DF(decoded.asdict())
                data = pd.concat([data, new_ais_df])
                print("---------------------------------")
                print(new_ais_df)
                print("---------------------------------")

        
            if data.shape[0] >= csv_samples_max:
                tmp_date = time.strftime("%Y%m%d", time.localtime())
                if file_date != tmp_date:
                    file_count = 0
                    file_date = tmp_date
                    
                save_file_root = file_date+"_"+str(file_count)
                storeCSV(data, save_file_path, save_file_prefix, save_file_root)
                file_count += 1
                data = pd.DataFrame(columns=index_columns)
                

