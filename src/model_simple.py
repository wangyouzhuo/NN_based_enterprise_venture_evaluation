import tensorflow as tf
from utils.xlsx_op import xlsx2dataframe
import pandas as pd
from config.config import ROOT_DIR
from sklearn.model_selection import train_test_split
import numpy as np
from sklearn.model_selection import KFold


LR = 0.0001
#BETA = 10
DROP_PRO = 0.6
L2_REG = 0.005
proportion_2015 = 0.6
proportion_2016 = 0.4
proportion_2017 = 0.4



def read_raw_data(path,year):
    raw_data = xlsx2dataframe(path)
    raw_data = raw_data[raw_data['年份'] == year]
    return raw_data


def choose_raw_data(raw_data,x_columns,y_columns,proportion,num_all):
    """

    :param raw_data:
    :param proportion: 坏样本/总样本
    :param num_all:  总样本数量
    :param year_num:  年的index 2015-0  2016-1 2017-2

    :return: data_x data_y
    """
    assert proportion < 1  #   坏样本:总样本 = proportion

    #print("需要的负样本有：%s ,实际负样本有:%s"%(int(num_all*proportion) ,len(raw_data[raw_data['是否st'] == 1])))
    if int(num_all*proportion) >= len(raw_data[raw_data['是否st'] == 1]):
        result_bad = raw_data[raw_data['是否st'] == 1]
        count_bad  = len(result_bad)
        count_good = int(num_all-count_bad)
        print("************************")
        print(len(raw_data[raw_data['是否st'] == 0]))
        print(count_good)
        result_good= raw_data[raw_data['是否st'] == 0].sample(n = count_good,axis=0)
        result     = pd.concat([result_good, result_bad], axis=0, ignore_index=True).sample(frac=1.0).reset_index()
        return np.array(result[x_columns]),np.array(result[y_columns])
    else:
        count_good = int((1.0-proportion)*num_all)
        count_bad  = int(num_all - count_good)
        result_good= raw_data[raw_data['是否st'] == 0].sample(n = count_good,axis=0)
        result_bad = raw_data[raw_data['是否st'] == 1].sample(n = count_bad ,axis=0)
        result     = pd.concat([result_good, result_bad], axis=0, ignore_index=True).sample(frac=1.0).reset_index()
        return (result[x_columns]),(result[y_columns])


class Simple_NN(object):
    def __init__(self,n_input):
        w_init = tf.random_normal_initializer(0., .1)
        self.keep_probiliaty = tf.placeholder(tf.float32)
        self.input = tf.placeholder(dtype=tf.float32, shape=[None, n_input], name='input_layer')
        self.output_truth = tf.placeholder(dtype=tf.int32, shape=[None, ], name='output_truth')
        layer_1 = tf.layers.dense(self.input, units=128, activation=tf.nn.relu,
                                  kernel_initializer=w_init, name='l_1',
                                  kernel_regularizer=tf.contrib.layers.l2_regularizer(L2_REG))
        self.layer_2 = tf.layers.dense(layer_1, units=64, activation=tf.nn.relu,
                                       kernel_initializer=w_init, name='l_2',
                                       kernel_regularizer=tf.contrib.layers.l2_regularizer(L2_REG))
        drop_layer = tf.nn.dropout(self.layer_2,keep_prob=self.keep_probiliaty)

        self.output = tf.layers.dense(drop_layer, units=2, activation=tf.nn.softmax, kernel_initializer=w_init, name='l_output')
        self.ground_truth = tf.one_hot(self.output_truth, 2, dtype=tf.float32)
        self.loss_simple = tf.nn.softmax_cross_entropy_with_logits(logits=self.output , labels=self.ground_truth)
        #self.loss_important = BETA* tf.nn.softmax_cross_entropy_with_logits(logits=self.output , labels=self.ground_truth)
        #self.loss = tf.reduce_mean(self.loss_dirty)
        #self.loss_dirty  = tf.cond(pred=self.output_truth>tf.constant(0),
        #                    true_fn = lambda:BETA*tf.nn.softmax_cross_entropy_with_logits(logits=self.output , labels=self.ground_truth),
        #                    false_fn= lambda:     tf.nn.softmax_cross_entropy_with_logits(logits=self.output , labels=self.ground_truth))
        self.loss = tf.reduce_mean(self.loss_simple)

        _,self.acc_op = tf.metrics.accuracy(labels=tf.one_hot(self.output_truth, 2, dtype=tf.float32) , predictions=self.output)
        self.opt = tf.train.AdamOptimizer(learning_rate = LR ).minimize(self.loss)




    def train(self,sess,data_x,data_y,pro):
        dict = {self.input:data_x,self.output_truth:data_y,self.keep_probiliaty:pro}
        loss_value, _,acc_value= sess.run([self.loss , self.opt ,self.acc_op],feed_dict = dict)
        #print("Loss:%2.3f , Acc：%2.3f"%(loss_value,acc_value))
        predicted_result,ground_truth = sess.run([self.output,self.ground_truth],feed_dict=dict)
        # for i in range(len(predicted_result)):
        #     predicted_one,predicted_two = predicted_result[i][0],predicted_result[i][1]
        #     print("predicted_distribution: [%1.6f,%1.6f] || ground_truth: %s " % (predicted_one,predicted_two,ground_truth[i]))

        return loss_value,acc_value

    def inference(self,sess,data_x,pro):
        dict = {self.input:data_x,self.keep_probiliaty:pro}
        result = sess.run(self.output,feed_dict = dict)
        return result


def compute_acc_rec(predicted_list,truth_list):
    # 样本中： 1 是
    TP,FN,FP,TN = 0,0,0,0
    ALL_COUNT = len(predicted_list)
    for i in range(ALL_COUNT):
        prediction,truth = predicted_list[i],truth_list[i]
        if prediction == truth:
            if prediction == 0:
                # 负样本 预测为 负类
                TN = TN + 1
            if prediction == 1:
                # 正样本 预测为 正类
                TP = TP + 1
        else:
            if prediction == 1:
                # 负样本 预测为 正类
                FP = FP + 1
            else:
                # 正样本 预测为 负类
                FN = FN + 1
    acc     = ((TP + TN)*1.0)/ALL_COUNT
    rec     = (TP*1.0)/sum(truth_list)
    f_score = (acc*rec*2)/(acc+rec)
    return acc,rec,f_score,TP



def get_batch_num(epoch):
    # y2 = int(50 * (np.e ** 194) * np.e**((3*epoch / 10000 - 10000) / 50) + 50)
    # y1 = int((100 - y2)/2)

    y2 = 128 * (0.66 * (np.e ** 14) * np.e ** ((3 * epoch / 100 - 1000) / 50) + 0.34)
    y1 = (128 - y2) / 2

    return y2,y1


def run_model(filepath):

    data_in_2015,data_in_2016,data_in_2017 = read_raw_data(file_path,year=2015),read_raw_data(file_path,year=2016),read_raw_data(file_path,year=2017)
    x_columns = data_in_2015.columns[4:]
    y_columns = data_in_2015.columns[3]
    SESS = tf.Session()
    n_input = len(data_in_2015.columns[4:])
    model = Simple_NN(n_input=n_input)
    SESS.run([tf.global_variables_initializer(), tf.local_variables_initializer()])
    kf = KFold(n_splits=3, shuffle=True)
    saver = tf.train.Saver()
    for train_index, test_index in kf.split(data_in_2017):
        data_train_2017 = data_in_2017.iloc[train_index,:]
        data_test_2017  = data_in_2017.iloc[test_index ,:]
        test_x = np.array(data_test_2017[x_columns])
        test_y = np.array(data_test_2017[y_columns]).tolist()
        # print("---------------------")
        # print("划分的训练集中负样本数量：",sum(np.array(data_train_2017[y_columns]).reshape([1,len(data_train_2017)]).tolist()[0]))
        # print("划分的测试集中负样本数量：",sum(np.array(data_test_2017[y_columns]).reshape([1,len(data_test_2017)]).tolist()[0]))
        max_test_recall, max_sum_recall = 0, 0
        for epoch in range(1000000):
            big,small = get_batch_num(epoch)
            x_train_2015, y_train_2015 = choose_raw_data(data_in_2015   , x_columns=x_columns,
                                                         y_columns=y_columns, proportion=proportion_2015, num_all=small)
            x_train_2016, y_train_2016 = choose_raw_data(data_in_2016   , x_columns=x_columns,
                                                         y_columns=y_columns, proportion=proportion_2016, num_all=small)
            x_train_2017, y_train_2017 = choose_raw_data(data_train_2017, x_columns=x_columns,
                                                         y_columns=y_columns, proportion=proportion_2017, num_all=big)
            x_train = pd.DataFrame(np.concatenate([x_train_2015, x_train_2016,x_train_2017]))
            y_train = pd.DataFrame(np.concatenate([y_train_2015, y_train_2016,y_train_2017]))
            shuffle_index = np.random.permutation(len(x_train))
            x_train = np.array(x_train.iloc[shuffle_index,:])
            y_train = np.array(y_train.iloc[shuffle_index,:]).reshape([1,-1])[0]
            model.train(sess=SESS, data_x=x_train, data_y=y_train,pro=DROP_PRO)
            if epoch%10 == 0:
                # 测试集jiu
                predicted_y_dirty = model.inference(sess=SESS,data_x=test_x,pro=1.0).tolist()
                predicted_y = []
                for item in predicted_y_dirty:
                    max_index = item.index(max(item))
                    predicted_y.append(max_index)
                acc_test,recall_test,f_score_test,TP_test = compute_acc_rec(predicted_y,test_y)
                # 训练集
                predicted_y_train = model.inference(sess=SESS, data_x=x_train, pro=1.0).tolist()
                predicted_train = []
                for item in predicted_y_train:
                    max_index = item.index(max(item))
                    predicted_train.append(max_index)
                acc_train,recall_train,f_score_train, TP_train = compute_acc_rec(predicted_train, y_train)
                # print
                print("-------------------------------------------------------------------------------------------")
                print("测试集——No:%6d || 准确率：%2.3f || 召回率：%2.3f || F_Score：%2.3f || 正样本总数:%2d "
                      "|| 预测的正样本总数:%2d || 成功抓出的正样本：%s"%(epoch,acc_test,recall_test,f_score_test,sum(test_y),sum(predicted_y),TP_test))

                print("训练集——No:%6d || 准确率：%2.3f || 召回率：%2.3f || F_Score：%2.3f || 正样本总数:%2d "
                      "|| 预测的正样本总数:%2d || 成功抓出的正样本：%s" % (
                      epoch, acc_train, recall_train, f_score_train, sum(y_train.tolist()), sum(predicted_train), TP_train))
                # 更新 max_test_recall  和  max_sum_recall
                if recall_test>max_test_recall and recall_test<0.7 and recall_test>0.3 and epoch>1000:
                    max_test_recall = recall_test
                if (recall_test+recall_train) > max_sum_recall and recall_test < 0.7 and recall_test > 0.3 and epoch > 1000:
                    max_sum_recall = recall_test+recall_train
                if recall_test>=0.47 and (recall_test+recall_train)>=1.0\
                        and epoch>1000 and acc_test>0.92:
                        max_test_recall_string = 'Test'+str(round(recall_test*100.0,2))+\
                                                 '%'+'_'+'Train'+ str(round(recall_train*100.0,2))+'%'+'_Acc'+str(round(acc_test*100.0,2))+'%'
                        saver.save(SESS, ROOT_DIR+'/model/'+max_test_recall_string+'.ckpt',global_step=None)










if __name__ =="__main__":
    file_path = ROOT_DIR+'/temp_data/data2model/data_nm.xlsx'
    # raw_data_train,raw_data_test = []
    # SESS = tf.Session()
    # for year in [2015,2016,2017]:
    #     data = read_raw_data(file_path, int(year))
    #     X_train, X_test, y_train, y_test = train_test_split(X, labels, test_size=0.3, random_state=42)
    #     raw_data_train.append(read_raw_data(file_path,int(year)))
    # n_input = len(raw_data_train[0].columns[4:])
    # print(n_input)
    # model = Simple_NN(n_input=n_input)
    # SESS.run([tf.global_variables_initializer(),tf.local_variables_initializer()])
    # count = 0
    # num_all = 50
    # for epoch in range(100000):
    #     for i in range(3):
    #         print("--------------------%s----------------------"%epoch)
    #         data_x,data_y = choose_raw_data(raw_data=raw_data_train[i],proportion=0.2,num_all=num_all,year_num=i)
    #         model.train(sess = SESS,data_x = data_x,data_y=data_y)
    run_model(file_path)






