#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 16:02:04 2019

@author: sn
"""

from weibo_class import Weibo
import os
import csv
import traceback

category = { '0': "服装", '1': "美食", '2': "美妆", '3': "动漫", '4': "电竞", '5': "育儿", '6': "淘宝"}

def get_all_posts(list_name, filter) :
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
            print(u"用户名: " + user_id[p])
            wb = Weibo(user_id[p], filter)
            wb.start()
            print(u"用户名: " + wb.username)
            print(u"全部微博数: " + str(wb.weibo_num))
            print(u"关注数: " + str(wb.following))
            print(u"粉丝数: " + str(wb.followers))
            
            file_dir = os.path.split(os.path.realpath(__file__))[0] + os.sep + "weibo"
            if not os.path.isdir(file_dir):
                os.mkdir(file_dir)
            file_path = file_dir + os.sep + "weibo_posts.csv"            
            with open(file_path, mode='a') as csv_file:
                csv_file = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_file.writerow(['ID', '昵称', '内容', '位置', '发布时间', '获得点赞数', '获得转发数', '获得评论数', '发布工具', '分类', '是否大V'])
                for i in range(1, wb.weibo_num2 + 1):
                    csv_file.writerow([wb.user_id, wb.username, wb.weibo_content[i-1],wb.weibo_place[i-1], \
                                       wb.publish_time[i-1], wb.up_num[i-1], wb.retweet_num[i-1], wb.comment_num[i-1], \
                                       wb.publish_tool[i-1], category_idx[p], big_V_idx[p]])                    
            print(u"微博写入csv完毕，保存路径:")
            print(file_path)
        
    except Exception as e:
        print("Error: ", e)
        traceback.print_exc()

def main() :
    list_file = 'weibo_info.csv'
    filter = 0
    get_all_posts(list_file, filter)
    
    
if __name__ == "__main__":
    main()