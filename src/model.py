import pandas as pd
import keras
from random import shuffle
from utils.xlsx_op import xlsx2dataframe
from config.config import ROOT_DIR
from scipy.stats import kstest
import numpy as np
from keras.models import Sequential
from keras.layers.core import Dense,Activation
from keras import layers,optimizers





#raw_data = xlsx2dataframe(ROOT_DIR+'/temp_data/data2model/data_nm.xlsx')

def choose_raw_data(path,year):
    raw_data = xlsx2dataframe(path)
    raw_data = raw_data[int(raw_data['年份']) == year]
    return raw_data



def choose_raw_data(raw_data,year,proportion,num_all):
    assert proportion < 1  #   好样本:坏样本 = proportion
    if num_all*proportion >= len(raw_data[int(raw_data['是否st']) == 1]):
        print("%s年的坏样本不够！请调整 坏样本占比proportion 或 抽取总数量num_all ！"%year)
        return
    else:
        count_good = int((1.0-proportion)*num_all)
        count_bad  = num_all -count_good
        result_good= raw_data[int(raw_data['是否st']) == 0].sample(n = count_good,axis=0)
        result_bad = raw_data[int(raw_data['是否st']) == 1].sample(n = count_bad,axis=0)
        result     = pd.concat([result_good, result_bad], axis=0, ignore_index=True).sample(frac=1.0).reset_index()
        return result


def build_network(n_input,n_output):
    # net = Sequential()
    # net.add(Dense(n_input , 128))
    # net.add(Activation('relu'))
    # net.add(Dense(128,2))
    # net.add(Activation('softmax'))
    # net.add(Dense)
    model = Sequential()
    model.add(layers.Dense(128, activation='relu', input_shape=(8000,)))
    model.add(layers.Dense(64, activation='relu'))
    model.add(layers.Dense(1, activation='sigmoid'))
    model.compile(optimizer=optimizers.RMSprop(lr=0.001),  # 还可以通过optimizer = optimizers.RMSprop(lr=0.001)来为优化器指定参数
                  loss='binary_crossentropy',  # 等价于loss = losses.binary_crossentropy
                  metrics=['accuracy'])  # 等价于metrics = [metircs.binary_accuracy]
    return model


def train_model(model,year,batch_size,)






if __name__ == "__main__":
    raw_data = xlsx2dataframe(ROOT_DIR+'/temp_data/data2model/data_nm.xlsx')
    for item in raw_data.columns:
        target = np.array(raw_data[item]).reshape(-1,len(raw_data)).tolist()[0]
        #print("target",target)
        print("%s  : %s"%(item,kstest(target,'uniform')))
