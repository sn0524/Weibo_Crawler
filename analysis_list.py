#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 13:10:22 2019

@author: sn
"""

from weibo_class import Weibo
import os
import csv
import traceback
import matplotlib.pyplot as plt

category = { 0: "服装", 1: "美食", 2: "美妆", 3: "动漫", 4: "电竞", 5: "育儿", 6: "淘宝", }
def analysis_list():
    try: 
        user_id = [] 
        user_name = []
        weibo_num = []
        following = []
        followers = []
        category_idx = [] 
        big_V_idx = []
        
        # 读取csv列表
        file_dir = os.path.split(os.path.realpath(__file__))[0] + os.sep + "weibo"
        if not os.path.isdir(file_dir):
            os.mkdir(file_dir)
        file_path = file_dir + os.sep + "weibo_info.csv"
        with open(file_path, mode='a') as csv_file:
            read_csv = csv.reader(csv_file, delimiter=',')
            for row in read_csv:
                user_id.append(row[0])
                user_name.append(row[1])
                weibo_num.append(row[2])
                following.append(row[3])
                followers.append(row[4])
                category_idx.append(category[row[5]])
                big_V_idx.append(row[6])
         
        
                
            
    except Exception as e:
        print("Error: ", e)
        traceback.print_exc()

if __name__ == "__main__":
    analysis_list()