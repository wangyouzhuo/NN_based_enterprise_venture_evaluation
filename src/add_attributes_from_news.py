import pandas as pd
import numpy as np
from utils.txt_op import list2txt
from utils.xlsx_op import xlsx2dataframe,dataframe2xlsx
from src.generate_company_name_dict import id2name
from temp_data.pos_neg_dict.emotion_dict import *
import jieba.posseg as psg
import jieba
from config.config import ROOT_DIR


def cut_line(topic):
    a = psg.cut(topic)
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


def get_all_company_id_name(path):
    result_id_list = []
    result_name_list = []
    f = open(path, "r")
    for line in f.readlines():
        if len(line)>=1:
            id = line.split()[0]
            name = ''.join(line.split()[1:])
            if len(id)<6:
                 id = (6-len(id))*'0'+id
            if id in result_id_list:
                continue
            else:
                result_id_list.append(id)
                result_name_list.append(name)
    return result_id_list,result_name_list




def get_long_id(input):
    if len(str(input))<6:
         result = '0'*(6-len(str(input))) + str(input)
    else:
        result = str(input)
    return result


# 判定每条topic 消极还是积极 '亏损裁员','股价下跌','破产','违规处罚','诉讼涉案','减持','人事变动','停牌退市','推迟延期','申请遭拒','模糊消极'
def count_attributes_dict(topic):
    """
    :param topic:
    :return:  attributes_dict {"消极数量":2 , .......}
    """
    # '消极占比','积极数量','消极数量','亏损裁员',
    # '股价下跌','破产','违规处罚','诉讼涉案','减持',
    # '人事变动','停牌退市','推迟延期','申请遭拒','模糊消极'

    target_atttributes_list = ['业绩亏损','股权变动','违规处罚','诉讼涉案','高管及实控人','推迟及延期','申请遭拒']

    attributes_dict = {}
    for item in ['积极数量','消极数量']+target_atttributes_list:
        attributes_dict[item] = 0
    positive_buffer = 0
    negetive_buffer = 0
    line_list = cut_line(topic)
    for word in line_list:
        if word in positive_all: positive_buffer = positive_buffer + 1
        if word in negative_all: negetive_buffer = negetive_buffer + 1
        if negetive_buffer>0:
            attributes_dict['消极数量'] = 1
            attributes_dict['积极数量'] = 0
        elif negetive_buffer==0 and positive_buffer>0:
            attributes_dict['积极数量'] = 1
            attributes_dict['消极数量'] = 0
        else:
            attributes_dict['积极数量'] = 0
            attributes_dict['消极数量'] = 0
        for i in range(len(attributes_name)):
            if word in attributes_name[i]:
                attributes_dict[attributes_name[i]] = attributes_dict[attributes_name[i]] + 1
    return attributes_dict


def add_attibutes_from_news(id_index_list,input_xlsx = None,output_xlsx = None,
                            attibutes_list = None,name_list = None,test_atributes_list = None):
    result_dataframe =pd.DataFrame(index=range(len(id_index_list)),
                    columns=['stock_id','stock_name','news_count']+test_atributes_list
                                    )
    source_data = xlsx2dataframe(input_xlsx)
    for i in range(0,len(id_index_list)):
        result_dataframe.loc[i,'stock_id'] = id_index_list[i]
    result_dataframe = result_dataframe.fillna(0)
    for i in range(0,len(id_index_list)):
        news_count,news_score_sum,news_score_mean = 0,0,0
        stock_name = id2name(id =id_index_list[i],stock_name_list=name_list,stock_id_list=id_index_list )
        result_dataframe.loc[i,'stock_name'] = stock_name
        result_dataframe.loc[i,test_atributes_list] = 0
        for j in range(len(source_data)):
            if get_long_id(source_data['股票代码'][j]) == id_index_list[i]:
                topic =  source_data.loc[j,'新闻标题']
                news_count = news_count + 1
                attibutes_dict_of_topic = count_attributes_dict(topic)
                for attribute in test_atributes_list[1:]:
                    result_dataframe.loc[i,attribute] = result_dataframe.loc[i,attribute] + attibutes_dict_of_topic[attribute]
        result_dataframe.loc[i,'news_count'] = news_count
        if news_count == 0:
            result_dataframe.loc[i,'消极占比'] = 0
        else:
            result_dataframe.loc[i,'消极占比'] = result_dataframe.loc[i,'消极数量']/news_count*1.0
        print("------------------------------")
<<<<<<< HEAD
        print("当前第:%s条 || 进度 %%%s"%(str(i),   str(((i+1)*1.0/len(id_index_list))*100)   )  )
=======
        print("当前第:%s条 || 进度 %%%s" % (str(i), str(((i + 1) * 1.0 / len(id_index_list)) * 100)))
>>>>>>> origin/master
    return result_dataframe


if __name__ == "__main__":
    jieba.load_userdict(
<<<<<<< HEAD
        ROOT_DIR+'temp_data/word_frequence/stopword.txt')
    id_list,name_list = get_all_company_id_name(ROOT_DIR+"/raw_data/新旧上市公司名称.txt")
    result_dataframe = add_attibutes_from_news(input_xlsx=ROOT_DIR+'temp_data/完整excel/2017_excel.xlsx',
                                  id_index_list=id_list,name_list=name_list,
                                  test_atributes_list=['消极占比','积极数量','消极数量','亏损裁员','股价下跌','破产','违规处罚','诉讼涉案','减持',
                                                       '人事变动','停牌退市','推迟延期','申请遭拒','模糊消极'])
    dataframe2xlsx(result_dataframe,ROOT_DIR+"temp_data/add_attributes/2017_add_attributes.xlsx")
=======
        '/Users/wangyouzhuo/PycharmProjects/NN_based_enterprise_venture_evaluation/temp_data/word_frequence/stopword.txt')
    id_list,name_list = get_all_company_id_name("/Users/wangyouzhuo/PycharmProjects/NN_based_enterprise_venture_evaluation/raw_data/新旧上市公司名称.txt")
    for year in ['2015','2016','2017']:
        result_dataframe = (add_attibutes_from_news(input_xlsx='/Users/wangyouzhuo/PycharmProjects/NN_based_enterprise_venture_evaluation/temp_data/完整excel/'+year+'_excel.xlsx',
                                  id_index_list=id_list,name_list=name_list,
                                  test_atributes_list=['消极占比','积极数量','消极数量']+attributes_name))
        dataframe2xlsx(result_dataframe, ROOT_DIR + "temp_data/add_attributes/"+year+"_add_attributes.xlsx")
>>>>>>> origin/master
