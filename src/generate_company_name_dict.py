'''
    读取文件“新旧上市公司名称.txt” ，生成一个用来分词的dict。
    原txt已经包含了新旧公司名称，但考虑部分新闻对公司描述的不准确性和模糊性，生成词典的时候存在以下规则：
         ST 明科 ————> ST 明科 / 明科
         万科A   ————>  万科A/ 万科

    【
        注意 linux中txt文件存在 with bom问题 ：
                cd root_path
                find . -type f -exec sed -i 's/\xEF\xBB\xBF//' {} \;
        解决
    】
'''

import re

import numpy as np
import pandas as pd

from config.config import ROOT_DIR as root_dir
from utils.txt_op import list2txt, just_chinses


def name2id(name, stock_name_list, stock_id_list):
    if name in stock_name_list:
        index = stock_name_list.index(name)
        return stock_id_list[index]
    else:
        print("%s不存在于name_list中" % name)
        return None


def id2name(id, stock_name_list, stock_id_list):
    if id in stock_id_list:
        index = stock_id_list.index(id)
        return stock_name_list[index]
    else:
        print("%s不存在于id_list中" % id)
        return None


# 检查缩写是否可以使用
def check_new_name(new_name, stock_name_list, stock_id_list):
    target_set = set()
    if len(new_name) == 2:
        for full_name in stock_name_list:
            if len(just_chinses(full_name)) >= 2 and new_name in full_name:
                target_set.add(full_name)
        target_name_list = list(target_set)
        target_set = set()
        for item in target_name_list:
            item_id = name2id(item, stock_name_list, stock_id_list)
            target_set.add(item_id)
        target_list = list(target_set)
        if len(target_list) >= 2:
            # result_list = [id2name(x,stock_name_list,stock_id_list) for x in target_list]
            # print("缩写为 %s , 匹配公司为%s , 对应代码列表%s"%(new_name,result_list,target_list))
            return False
        if new_name in ['神奇', '百大', '龙头', '一致', '比特', '起步', '标准',
                        '东莞', '商城', '巴士', '海洋', '创新', '隧道', '综艺',
                        '中亚', '同为', '中企']:
            return False
        return new_name


# 便于匹配 按照冗余规则生成一些新的股票的缩写 如果没有被缩写则返回None
def check_the_abbreviation(stock_name):
    # 排除名称带有英文的公司
    result = None
    if 'TCL'not in stock_name and 'G'not in stock_name :
        # xx股份—>xx   xxB股 —> xx
        if "股" in stock_name or "集团" in stock_name:
            result = stock_name[:-2]
        else:
            new_str = re.sub(r'[*]?[a-z]?[A-Z]?', "", str(stock_name).strip())
            if new_str == stock_name:  # 如果公司名称是纯中文 跳过
                return None
            else:
                result = new_str
    return result


# 股票代码格式规范化  2345 ——> 002345
def long_stock_id(stock_id_string):
    stock_id_string = str(stock_id_string).strip()
    if len(str(stock_id_string)) < 6:
        result = '0' * (6 - len(str(stock_id_string))) + str(stock_id_string)
    else:
        result = str(stock_id_string)
    return result


def get_name_dicts(pathname):
    #
    frame_demo = pd.DataFrame(columns=['股票代码', '股票简称'])
    frame_demo[['股票简称']] = frame_demo[['股票简称']].astype(str)
    frame_demo[['股票代码']] = frame_demo[['股票代码']].astype(str)
    with open(pathname, 'r', encoding='utf-8')as demo:
        for line in demo:
            list_line = line.split()
            stock_id_demo = long_stock_id(list_line[0])
            stock_name_demo = ''.join(list_line[1:])
            frame_demo = frame_demo.append({'股票代码': stock_id_demo, '股票简称': stock_name_demo}, ignore_index=True)
    list_name_demo = np.array(frame_demo['股票简称'])
    list_id_demo = np.array(frame_demo['股票代码'])
    list_name_demo = list_name_demo.reshape(-1, len(list_name_demo)).tolist()[0]
    list_id_demo = list_id_demo.reshape(-1, len(list_id_demo)).tolist()[0]
    df_empty = pd.DataFrame(columns=['股票代码', '股票简称'])
    df_empty[['股票简称']] = df_empty[['股票简称']].astype(str)
    df_empty[['股票代码']] = df_empty[['股票代码']].astype(str)
    with open(pathname, 'r', encoding='utf-8')as df:
        for line in df:
            list_line = line.split()
            stock_id = long_stock_id(list_line[0])
            stock_name = ''.join(list_line[1:])
            df_empty = df_empty.append({'股票代码': stock_id, '股票简称': stock_name}, ignore_index=True)
            if check_the_abbreviation(stock_name):
                abbreviation = check_the_abbreviation(stock_name)
                new_stock_name = check_new_name(abbreviation, list_name_demo, list_id_demo)
                if new_stock_name:
                    df_empty = df_empty.append({'股票代码': stock_id, '股票简称': new_stock_name}, ignore_index=True)
    stock_name_list = list(df_empty['股票简称'])
    stock_number_list = list(df_empty['股票代码'])
    return stock_name_list, stock_number_list


if __name__ == "__main__":

    path = root_dir + "/raw_data/新旧上市公司名称.txt"
    stock_name_list, stock_number_list = get_name_dicts(path)
    list2txt(stock_name_list, root_dir + 'temp_data/', '冗余股票名称.txt')
    list2txt(stock_number_list, root_dir + 'temp_data/', '冗余股票代码.txt')
