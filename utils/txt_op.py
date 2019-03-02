import os

import numpy as np

from config.config import ROOT_DIR


# 把一个list保存为txt
def list2txt(list,save_path,file_name):
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    f = open(save_path + str(file_name), "w", encoding='utf-8')
    for item in list:
        f.write(item + '\n')
    print("list已经写入到 %s 当中" % (save_path + file_name))
    f.close()


def txt2list(file_path, flatten=False):
    result = []
    f = open(file_path, "r")
    for line in f:
        if len(line)>=1:
            item = line.split()[0]
            result.append(item)
    if flatten:
        length = len(result)
        temp = np.array(result)
        result = temp.reshape(-1, length)
        return result.tolist()[0]
    else:
        return result


def check_path(path, file_name):
    if not os.path.exists(path):
        os.makedirs(path)
    print(path+file_name)
    f = open(path+file_name,'w')
    f.close()
    return str(path + file_name)


def clean_string(target_string):
    target_string = target_string.replace(" ", '')
    target_string = target_string.strip()
    target_string = target_string.replace('\r', '').replace('\n', '').replace('\n', '').replace('\t', '')
    return target_string


def is_chinese(char):
    if char >= '\u4e00' and char <= '\u9fa5':
        return True
    else:
        return False


def is_alphabet(char):
    if (char >= '\u0041' and char <= '\u005a') or (char >= '\u0061' and char <= '\u007a'):
        return True
    else:
        return False


def is_number(char):
    if char >= '\u0030' and char <= '\u0039':
        return True
    else:
        return False

def just_chinses(string):
    result = ""
    for item in string:
        if is_chinese(item):
            result = result+item
    return result

def get_xsb_name_dict(filepath,save_path = None,file_name = None):
    fr = open(filepath)
    name_list = []
    for line in fr.readlines():
        if len(line)>=5:
            name_list.append(line.split()[1])
    list2txt(name_list,save_path,file_name)


if __name__ == "__main__":
    # a = check_path(ROOT_DIR + '/temp_data/', '冗余股票名称.txt')
    # list = txt2list(a,flatten=True)
    # for item in list:
    #     target_list = set()
    #     if len(item) == 2:
    #         for item_two in list:
    #             if len(item_two) > 2 and item in item_two:
    #                 target_list.add(item_two)
    #         # if len(target_list)>=2:
    #         print("缩写为 【%s】 匹配公司为%s" % (item, target_list))

    get_xsb_name_dict('/Users/wangyouzhuo/PycharmProjects/NN_based_enterprise_venture_evaluation/raw_data/新三板名称.txt',
                      '/Users/wangyouzhuo/PycharmProjects/NN_based_enterprise_venture_evaluation/temp_data/',
                      '新三板词典.txt')




