import pandas as pd
import numpy as np
from utils.xlsx_op import xlsx2dataframe,dataframe2xlsx

# 股票代码格式规范化  2345 ——> 002345
def long_stock_id(stock_id_string):
    stock_id_string = str(stock_id_string).strip()
    if len(str(stock_id_string)) < 6:
        result = '0' * (6 - len(str(stock_id_string))) + str(stock_id_string)
    else:
        result = str(stock_id_string)
    return result



def quchong(input_path,output_path):
    data = xlsx2dataframe(input_path)
    data.drop_duplicates(subset=['新闻标题', '股票代码'], keep='first', inplace=True)
    data['股票代码'] = data['股票代码'].map(lambda x: long_stock_id(x))
    dataframe2xlsx(data,output_path)
    print("去重完毕")



if __name__ == "__main__":
    input_list = ["/Users/wangyouzhuo/PycharmProjects/NN_based_enterprise_venture_evaluation/" \
                  "temp_data/完整excel/"+item for  item in ['2015_excel.xlsx','2016_excel.xlsx','2017_excel.xlsx']]
    output_list = ["/Users/wangyouzhuo/PycharmProjects/NN_based_enterprise_venture_evaluation/" \
                   "temp_data/完整excel/"+item for  item in ['2015_去重.xlsx','2016_去重.xlsx','2017_去重.xlsx']]
    for i in range(len(input_list)):
        quchong(input_list[i],output_list[i])
