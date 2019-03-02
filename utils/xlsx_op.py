import pandas as pd
import numpy as np
import xlsxwriter


def dataframe2xlsx(data,output_path):
    xlsx_writer = pd.ExcelWriter(output_path)
    data.to_excel(xlsx_writer, 'Sheet1', engine="xlsxwriter")
    try:
        xlsx_writer.save()
        print("dataframe已经保存到对应路径下的output_path中。")
    except:
        pass
    xlsx_writer.close()



def xlsx2dataframe(input_path):
    data = pd.read_excel(input_path)
    # print("路径下的xlsx已经读取为dataframe，如下")
    # print(data)
    return data


if __name__ == "__main__":
    result = xlsx2dataframe("/Users/wangyouzhuo/PycharmProjects/NN_based_enterprise_venture_evaluation/temp_data/词频.xlsx")
    for item in result.columns:
        print(item)
        print(list(result[item]))