import pandas as pd
import numpy as np
from os import listdir
from utils.txt_op import check_path,is_chinese,txt2list,clean_string
import jieba
import openpyxl


# 把每个月的txt 拼接成 一年的txt
def txt2big_txt(filepath):
    # filepath 为 finish_data路径： /Users/......../raw_data/finish_data
    for wanzheng in listdir(filepath): # wanzheng : 20xx完整
        txt_folder = filepath + '/' + wanzheng + '/' + listdir(filepath + '/' + wanzheng)[1]
        print("开始:",wanzheng)
        text = ""
        for file in listdir(txt_folder):
            print('开始拼接',file)
            fr = open(txt_folder+'/'+file)
            text = text + fr.read()
            fr.close()
        save_path = check_path('/Users/wangyouzhuo/PycharmProjects/NN_based_enterprise_venture_evaluation/temp_data/',wanzheng+"拼接.txt")
        ft = open(save_path,'w')
        ft.write(text)
        ft.close()
    print('拼接完毕')

def cut_topic(topic):
    a = jieba.cut(topic)
    list = []
    try:
        while True:
            word = a.__next__()
            if len(word) == 0: continue  # 排除空字符
            if is_chinese(word[0]):
                list.append(word)
            else:
                continue
    except:
        return list

# topic中的新三板名称组成的list
def whe_xinsanban(topic,xsb_name_list):
    result_list = []
    topic_list= cut_topic(topic)
    #print(topic_list)
    for item in topic_list:
        if item in xsb_name_list:
            result_list.append(item)
    return result_list

# 该条新闻 是否需要删除（因为主体是 新三板）
def need_delete(zhuban_name,xsb_name_list):
    if len(xsb_name_list) == 0:
        return False
    elif len(xsb_name_list) == 1:
        if zhuban_name == xsb_name_list[0]:
            return False
        elif "证券" in zhuban_name:
            return True
        else:
            return True
    else:
        return True

def txt2xlsx(filepath,output_path,xsb_name_list):
    whe_delete = False
    COUNT_ALL = 0
    COUNT_XSB = 0
    xlsx_writer = pd.ExcelWriter(output_path)
    fr = open(filepath,encoding='utf-8')
    data_excel = pd.DataFrame(columns=['股票代码', '股票简称', '新闻标题', '新闻内容'])
    buffer_id,buffer_name,buffer_topic,buffer_content = None,None,None,None
    # str.join(sequence)
    for line in fr.readlines():
        #if COUNT_ALL >= 100:break

        if "Stock_ID" in line:  buffer_id = line.split()[1]
        if "Stock_Name" in line:  buffer_name = line.split()[1]
        if "News_Topic" in line:  buffer_topic = " ".join(line.split()[1:])
        if "News_Content" in line:  buffer_content =clean_string( " ".join(line.split()[1:])+"。" ) # 防止一些新闻 content本来就是空
        if buffer_id and buffer_name and buffer_topic and buffer_content:
            # print(buffer_id)
            # print(buffer_name)
            # print(buffer_topic)
            # print(buffer_content)
            # print(COUNT_ALL)
            # print("----------------------")
            company_list = whe_xinsanban(buffer_topic, xsb_name_list)
            whe_del = need_delete(buffer_name, company_list)

            if len(company_list)>=1 and whe_del:
                COUNT_XSB = COUNT_XSB + 1
                pass
            else:
                COUNT_ALL = COUNT_ALL + 1
                data_excel = data_excel.append(
                    {'股票代码': buffer_id, '股票简称': buffer_name, '新闻标题': buffer_topic, '新闻内容': buffer_content},
                    ignore_index=True
                )
            buffer_id, buffer_name, buffer_topic, buffer_content = None, None, None, None
    print("新闻总数:%s ,其中需要删除的新三板有%s"%(COUNT_ALL,COUNT_XSB))
    print(data_excel)
    data_excel.to_excel(xlsx_writer, encoding='uft-8',sheet_name='Sheet1',engine="xlsxwriter")
    try:
        xlsx_writer.save()
    except openpyxl.utils.exceptions.IllegalCharacterError:
        pass
    xlsx_writer.close()
    print("已经结束")


if __name__ == "__main__":
    xsb_dict_path = '/Users/wangyouzhuo/PycharmProjects/NN_based_enterprise_venture_evaluation/temp_data/新三板词典.txt'
    jieba.load_userdict(xsb_dict_path)
    xsb_name_list = txt2list(xsb_dict_path,flatten=True)
    #txt2big_txt('/Users/wangyouzhuo/PycharmProjects/NN_based_enterprise_venture_evaluation/raw_data/finish_data')
    txt2xlsx('/Users/wangyouzhuo/PycharmProjects/NN_based_enterprise_venture_evaluation/temp_data/2017完整拼接.txt',
             '/Users/wangyouzhuo/PycharmProjects/NN_based_enterprise_venture_evaluation/temp_data/2017_excel.xlsx',
             xsb_name_list)