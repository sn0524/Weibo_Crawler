#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 23:15:53 2019

@author: sn
"""

from weibo_class import Weibo
import os
import csv
import traceback
import numpy as np

category = { '0': "服装", '1': "美食", '2': "美妆", '3': "动漫", '4': "电竞", '5': "育儿", '6': "淘宝"}

list_name = 'weibo_info.csv'
filter = 0

try :
    user_id = [] 
    user_name = []
    weibo_num = []
    following = []
    followers = []
    category_idx = [] 
    big_V_idx = []

    with open(list_name, mode='r') as csv_file:
        read_csv = csv.reader(csv_file, delimiter=',')
        next(read_csv)
        for row in read_csv:
            user_id.append(int(row[0]))
            user_name.append(row[1])
            weibo_num.append(int(row[2]))
            following.append(int(row[3]))
            followers.append(int(row[4]))
            category_idx.append(category[row[5]])
            big_V_idx.append(row[6])
    
    for p in range(0, len(user_id)) :
        # print(u"用户名: " + str(user_id[p]) + ": " + str(p))
        
        file_dir = os.path.split(os.path.realpath(__file__))[0] + os.sep + "weibo"
        if not os.path.isdir(file_dir):
            os.mkdir(file_dir)
        file_path = file_dir + os.sep + str(user_id[p]) + '.csv'
        with open(file_path, mode='r') as csv_file:
            q = np.array(list(csv_file)).shape[0]
            print(q)
            
            if q == 1 and weibo_num[p] < 5000:
                wb = Weibo(user_id[p], filter)
                wb.start()
                print(u"用户名: " + wb.username)
                print(u"全部微博数: " + str(wb.weibo_num))
                print(u"关注数: " + str(wb.following))
                print(u"粉丝数: " + str(wb.followers))
                
except Exception as e:
    print("Error: ", e)
    traceback.print_exc()