import pandas as pd
import numpy as np
import jieba
from utils.txt_op import is_chinese,txt2list
import jieba.posseg as pseg



jieba.load_userdict(
    '/Users/wangyouzhuo/PycharmProjects/NN_based_enterprise_venture_evaluation/temp_data/word_frequence/stopword.txt')


def cut_line(topic):
    a = jieba.posseg.cut(topic)
    list = []
    try:
        while True:
            word, flag = a.__next__()
            if len(word) == 0: continue  # 排除空字符
            if flag[0] in ['n','a','v']:
                list.append(word)
            else:
                continue
    except:
        return list


def get_dict_of_text(filepath,dict,stop_word_path):
    stop_word_list = txt2list(stop_word_path,flatten=True)
    #print(stop_word_list)
    count = 0
    fr = open(filepath)
    for line in fr.readlines():
        if "Topic" in line or "Content" in line:
            if count%2000 == 0:print(count)
            count = count + 1
            word_list = cut_line(line)
            used_list = []
            for item in word_list:
                if item in stop_word_list:
                    continue
                else:
                    used_list.append(item)
                    if item in dict:
                        dict[item] = dict[item]+1
                    else:
                        dict[item] = 1
    return dict



# 统计15 16 17 18所有新闻的词频 排序输出成词典到txt
if __name__ == "__main__":
    dict = {}

    source_list = [
        '/Users/wangyouzhuo/PycharmProjects/NN_based_enterprise_venture_evaluation/temp_data/2015完整拼接.txt',
        '/Users/wangyouzhuo/PycharmProjects/NN_based_enterprise_venture_evaluation/temp_data/2016完整拼接.txt',
        '/Users/wangyouzhuo/PycharmProjects/NN_based_enterprise_venture_evaluation/temp_data/2017完整拼接.txt',
        '/Users/wangyouzhuo/PycharmProjects/NN_based_enterprise_venture_evaluation/temp_data/2018完整拼接.txt'
    ]

    for source in source_list:
        print(source)
        dict = get_dict_of_text(source,
                                dict,
                                '/Users/wangyouzhuo/PycharmProjects/NN_based_enterprise_venture_evaluation/temp_data/word_frequence/stopword.txt')

    save_path = '/Users/wangyouzhuo/PycharmProjects/NN_based_enterprise_venture_evaluation/temp_data/word_frequence/result_word_frequence_both_topic_content.txt'

    f = open(save_path , "w", encoding='utf-8')
    for item in sorted(dict.items(),key = lambda x:x[1],reverse = True):
        print(item[0])
        f.write(str(item[0]) +"   "+str(item[1])+ '\n')
    f.close()





