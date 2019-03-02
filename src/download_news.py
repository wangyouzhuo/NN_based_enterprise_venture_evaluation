import os
import logging
import re
import sys

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)


import time
from socket import timeout
from urllib import request
from urllib.error import HTTPError, URLError
import jieba
import pandas as pd
from bs4 import BeautifulSoup
from config.config import ROOT_DIR as root_dir
from config.config import REQUEST_SLEEP_TIME as sleep_time
sys.path.append('/Users/wangyouzhuo/PycharmProjects/NN_based_enterprise_venture_evaluation/utils')
from utils.txt_op import txt2list, check_path, clean_string, is_chinese


class News(object):
    def __init__(self):
        self.url = None  # 该新闻对应的url
        self.topic = None  # 新闻标题
        self.date = None  # 新闻发布日期
        self.content = None  # 新闻的正文内容
        self.author = None  # 新闻作者
        self.stock_name = None  # 新闻主体公司
        self.stock_id = None  # 主体公司的股票代码 【只考虑已上市的】


# 解析url  返回整数形 日期
def url2days(url):
    match = re.search(r'\d{4}\/\d{2}\/\d{2}', str(url))
    if match:
        result = str(match.group(0))
        day = int(result[-2:])
    return day


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


# 从topic解析出stock_name 否则返回None  顺带返回股票代码
def find_the_company(news_topic, stock_name_list, stock_id_list):
    result_id = None
    result_name = None
    news_topic = clean_string(news_topic)
    if '：' in news_topic:
        separator_index = news_topic.index('：')
        left_stock = []
        right_stock = []
        list_letf = cut_topic(news_topic[:separator_index])  # 对冒号左边进行分词
        list_right = cut_topic(news_topic[separator_index + 1:])  # 对冒号右边进行分词
        for item in list_letf:
            if item in stock_name_list: left_stock.append(item)
        for item in list_right:
            if item in stock_name_list: right_stock.append(item)
        # 人民日报：xx公司  ————> 主体为XX公司
        if len(left_stock) == 0 and len(right_stock) != 0:
            result_name = right_stock[0]
        # xx公司：gdfsgdf ————> 主体为XX公司
        if len(left_stock) != 0 and len(right_stock) == 0:
            result_name = left_stock[0]
        # AA公司:xx公司 ————> 主体为AA公司   AA证券：XX公司 ————> 主体为XX公司
        if len(left_stock) != 0 and len(right_stock) != 0:
            if '证券' in left_stock[0]:
                result_name = right_stock[0]
            else:
                result_name = left_stock[0]
    else:
        result_name_list = []
        raw_list = cut_topic(news_topic)
        for item in raw_list:
            if item in stock_name_list:
                result_name_list.append(item)
        if len(result_name_list) >= 1:
            result_name = result_name_list[0]
    if result_name:
        target_index = stock_name_list.index(result_name)
        result_id = stock_id_list[target_index]
    return result_name, result_id


def getNews(url, stock_name_list, stock_id_list):
    global count
    global html
    global days_count
    try:
        html = request.urlopen(url, timeout=20).read().decode('gb2312', 'ignore')
    except (HTTPError, URLError) as error:
        pass
    except timeout:
        logging.error('socket timed out - URL %s', url)
    else:
        logging.info('Access successful.')
    # *******************检查soup是否可被解析**************************
    soup = BeautifulSoup(html, 'html.parser')
    if not (soup.find('div', {'class': 'titmain'})):
        fail_writer.write("%s　解析 'div' {'class': 'titmain'}出错 \n" % url)
        return
    page = soup.find('div', {'class': 'titmain'})
    if not (page.find('h1')):
        fail_writer.write("%s　page.find('h1')出错 \n" % url)
        return
    topic = page.find('h1').get_text()  # 新闻标题
    if len(topic) <= 8:
        fail_writer.write("%s　topic过短出错 \n" % url)
        return
    stock_name, stock_id = find_the_company(topic, stock_name_list, stock_id_list)
    if not stock_name:
        fail_writer.write("%s　【解析不到公司名称】 \n" % url)
        return
    if not (page.find('div', {'class': 'texttit_m1'})):
        fail_writer.write("%s　解析'div', {'class': 'texttit_m1'}出错】 \n" % url)
        return

    news = News()  # 建立新闻对象
    news.topic = topic.strip()
    news.stock_name = stock_name
    news.stock_id = stock_id
    print(url)
    print("新闻标题：", news.topic)
    print("新闻主体公司为：", news.stock_name)
    print("公司股票代码为：", news.stock_id)
    days = url2days(url)  # days is int
    days_count[days] = days_count[days] + 1
    if len(str(days)) == 1:
        days = "0" + str(days)
    print("-------------" + str(year) + '-' + str(month) + '-' + str(days) + "-----------------\n\n")
    main_content = page.find('div', {'class': 'texttit_m1'})  # 新闻正文内容
    [s.extract() for s in main_content('div', {'class': 'kline'})]
    [s.extract() for s in main_content('a', {'class': 'iconnew01'})]
    [s.extract() for s in main_content('a', {'class': 'iconnew02'})]
    [s.extract() for s in main_content('p', {'align': 'center'})]
    content = ''
    # 写入txt文件
    for p in main_content.select('p'):
        content = content + clean_string(p.get_text())
    content = clean_string(content)
    if len(content) >= 32 * 30:
        news.content = str(content[:32 * 30])
    news.content = content
    news.url = url  # 新闻页面对应的url
    # 写入dataframe，方便最后存为excel
    count = count + 1
    global frame_out_to_xlsx
    frame_out_to_xlsx = frame_out_to_xlsx.append(
        {'股票代码': news.stock_id, '股票简称': news.stock_name, '新闻标题': news.topic, '新闻内容': news.content},
        ignore_index=True
    )
    txt_writer.write(
        '【Stock_ID】  ' + news.stock_id + '\n' + '【Stock_Name】  ' + news.stock_name + '\n' + '【News_Topic】  ' + news.topic + '\n' + '【News_Content】  ' + news.content + '\n' + '\n')
    # frame_out_to_xlsx.to_excel(xlsx_writer, 'Sheet1', engine="xlsxwriter")


def dfs(url, list, num_list):
    global count, visited
    if whe_test and count == test_episode: return
    pattern1 = '^http://stock.jrj.com.cn/' + year + '/' + month + '\/[a-z0-9_\/\.]*$'
    pattern2 = '^http://stock.jrj.com.cn/' + year + '/' + month + '\/[0-9]{14}\.shtml$'
    pattern3 = '^http://stock.jrj.com.cn/xwk/201001/201001[0-9][0-9]\_[0-9]\.shtml$'
    if url in visited:
        return
    else:
        visited.add(url)
    time.sleep(sleep_time)
    try:
        try:
            global html
            html = request.urlopen(url, timeout=20).read().decode('utf-8', 'ignore')
        except (HTTPError, URLError) as error:
            pass
        except timeout:
            logging.error('socket timed out - URL %s', url)
        else:
            logging.info('Access successful.')
        soup = BeautifulSoup(html, 'html.parser')
        if re.match(pattern2, url):
            getNews(url, list, num_list)
        links = soup.findAll('a', href=re.compile(pattern1))
        for link in links:
            if link['href'] not in visited:
                dfs(link['href'], list, num_list)
    except URLError as e:
        return
    except HTTPError as e:
        return


if __name__ == "__main__":

    # ****************************测试与否**********************************
    whe_test = False
    test_episode = 30

    # **************************设置爬取新闻的时间*****************************
    year = str(input("请输入要爬取的年份(20XX): "))
    month = str(input("请输入要爬取的月份: "))
    if len(month) == 1:
        month = "0" + month

    # **************************文件位置***************************
    company_name_dict_path = check_path(root_dir + 'temp_data/', '冗余股票名称.txt')
    company_id_dict_path = check_path(root_dir + 'temp_data/', '冗余股票代码.txt')
    data_txt_output = check_path(root_dir + 'data_output/txt_data/', year + '年' + month + '月.txt')  # 输出txt的位置
    data_xlsx_output = check_path(root_dir + 'data_output/excel_data/', year + '年' + month + '月.xlsx')  # 输出xlsx的位置
    fail_file_path = check_path(root_dir + 'data_output/fail_record/',
                                '【' + year + month + '】fail_record.txt')  # 失败记录存储位置

    global days_count, xlsx_writer, frame_out_to_xlsx, txt_writer, fail_writer, visited

    frame_out_to_xlsx = pd.DataFrame(columns=['股票代码', '股票简称', '新闻标题', '新闻内容'])


    days_count = [0] * 32

    # jieba载入“冗余股票名称词典”
    jieba.load_userdict(company_name_dict_path)


    sys.setrecursionlimit(1000000)  # 设置递归次数为100万

    visited = set()  # 存储访问过的url

    xlsx_writer = pd.ExcelWriter(data_xlsx_output)
    txt_writer = open(data_txt_output, 'a+', encoding='utf-8')
    fail_writer = open(fail_file_path, 'a+', encoding='utf-8')

    frame_out_to_xlsx.to_excel(xlsx_writer, 'Sheet1', engine="xlsxwriter")


    stock_name_list = txt2list(company_name_dict_path, flatten=True)
    stock_id_list = txt2list(company_id_dict_path, flatten=True)

    urls_list = [
        'http://stock.jrj.com.cn/xwk/' + year + month + '/' + year + month + '{}{}_{}.shtml'.format(str(i), str(j),
                                                                                                    str(k))
        for i in range(0, 4) for j in range(1, 10) for k in range(1, 20)]

    global news_in_frame, count, error_count

    count = 0

    for url in urls_list:
        if whe_test and count == test_episode:
            break
        if url == 'http://stock.jrj.com.cn/xwk/' + year + month + '/' + year + month + '31_1.shtml':  # 需要修改以更换月份
            dfs(url, stock_name_list, stock_id_list, )
            break
        dfs(url, stock_name_list, stock_id_list)
    else:
        print("url_list迭代完毕")
        dfs(url, stock_name_list, stock_id_list)
    dfs(url, stock_name_list, stock_id_list)



    fail_writer.write("**************新闻数量统计************\n")
    days_start = 1
    for item in days_count[1:]:
        fail_writer.write("%s号————%s条新闻 \n" % (days_start, item))
        days_start = days_start + 1

    fail_writer.close()
    txt_writer.close()

    frame_out_to_xlsx.to_excel(xlsx_writer, 'Sheet1', engine="xlsxwriter")
    try:
        xlsx_writer.save()
    except:
        pass
    xlsx_writer.close()
    print("%s年%s月的新闻爬取完毕" % (year, month))
