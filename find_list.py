#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 16:56:46 2019

@author: sn
"""

from weibo_class import Weibo
import os
import csv
import traceback

this_keyword = {"服装": 0, "穿搭": 0, "品牌店": 0, "时装": 0, "品牌": 0, "买手": 0, "美衣": 0, "衣服": 0, 
                "美食": 1, "下厨房": 1, "美食达人": 1, "烘焙": 1, "甜品": 1, "好吃": 1, "厨房": 1,
                "美妆": 2, "彩妆": 2, "混油皮": 2, "干皮": 2, "化妆": 2, "眼影": 2, "美甲": 2, "护肤": 2,
                "动漫": 3, "二次元": 3, "手办": 3, "cosplay": 3,
                "电竞": 4, "电子竞技": 4, "战队": 4, "RNG": 4, "LGD": 4, "Dota": 4, "游戏": 4, "LOL": 4, "LPL": 4, "LCK": 4, "魔兽": 4, "斗鱼直播": 4, "Game": 4,
                "育儿": 5, "母婴": 5, "妈咪": 5, "童装": 5, "宝宝": 5, "宝贝": 5, "女童": 5, "男童": 5, "童品": 5, 
                "淘宝": 6, "店铺": 6, "时尚": 6,
                }

def find_list(seed, filter):
    try:
        category_count = [10, 0, 10, 10, 10, 10, 10]
        
        total_num_of_people = 60 # 总共爬取的数量
        queue = [] # 待访问待博主列表
        queue.insert(0, seed)
        visit = [] # 已经访问过的博主列表
        flag = True # 标记搜索开始
        # 广度优先一级一级读取微博博主
        while flag :
            cur = queue.pop()
            if cur in visit :
                continue
            else :
                visit.insert(0, cur) # 当前节点已经访问
                wb = Weibo(cur, filter)	 # 调用Weibo类，创建微博实例wb
                wb.get_username() # 获取微博用户名字
                wb.get_user_info() # 获取微博用户信息
                wb.get_certification() # 获取认证信息
                print(wb.certification)
                wb.get_big_V() # 获取大V信息
                
                flag_get_following = False
                if len(queue) < 100 : # 保持待读取队列里有至少100个博主
                    flag_get_following = True 
                    # 获取关注的列表
                    print(u"获取关注的列表")
                    wb.get_following_list()
                    # 写入队列
                    for i in range(len(wb.following_id)) :
                        queue.insert(0, wb.following_id[i])
                    
                if not wb.certification :
                    continue
                else :
                    for keyword in this_keyword :
                        if keyword in wb.certification :
                            # 统计该博主属于哪个category
                            category_idx = this_keyword[keyword]
                            # 如果该category已经满了，跳过
                            if category_count[category_idx] > total_num_of_people :
                                break
                            else :
                                category_count[category_idx] = category_count[category_idx] + 1
                                # 判断是否寻找足够的博主
                                tmp = 0
                                for i in range(0, 6) :
                                    tmp = tmp + category_count[i]
                                if tmp == total_num_of_people:
                                    flag = False
                                # 判断是不是大V
                                big_V_idx = 1
                                if not wb.big_V:
                                    big_V_idx = 0
                                # 把该博主信息写入csv列表   
                                file_dir = os.path.split(os.path.realpath(__file__))[0] + os.sep + "weibo"
                                if not os.path.isdir(file_dir):
                                    os.mkdir(file_dir)
                                file_path = file_dir + os.sep + "weibo_info.csv"
                                with open(file_path, mode='a') as csv_file:
                                    csv_file = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                                    csv_file.writerow([wb.user_id, wb.username,
                                                       wb.weibo_num, wb.following, wb.followers, 
                                                       category_idx, big_V_idx])
                                print(u"信息写入csv完毕，保存路径:")
                                print(file_path)
                                
                                # 把归类的博主的关注写入列表
                                if not flag_get_following :
                                    flag_get_following = True
                                    print(u"获取关注的列表")
                                    wb.get_following_list() # 获取关注的列表
                                    for i in range(len(wb.following_id)) :
                                        queue.insert(0, wb.following_id[i])
                                        
#                                print(u"爬取全部微博")
#                                wb.start()  # 爬取微博信息
#    
#                                print(u"全部微博数: " + str(wb.weibo_num))
#                                print(u"关注数: " + str(wb.following))
#                                print(u"粉丝数: " + str(wb.followers))
                                break
        
    except Exception as e:
        print("Error: ", e)
        traceback.print_exc()

def main() :
    seed = 7076023370  # 爬虫起始id
    filter = 0 # 值为0表示爬取全部微博（原创微博+转发微博），值为1表示只爬取原创微博
    # 写入csv列表
    file_dir = os.path.split(os.path.realpath(__file__))[0] + os.sep + "weibo"
    if not os.path.isdir(file_dir):
        os.mkdir(file_dir)
    file_path = file_dir + os.sep + "weibo_info.csv"
    with open(file_path, mode='a') as csv_file:
        csv_file = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_file.writerow([u"用户id", u"用户昵称", u"微博数", u"用户关注数", u"用户粉丝数", u"category", u"是不是大V"])
    find_list(seed, filter)
    

if __name__ == "__main__":
    main()

