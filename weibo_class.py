#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import re
import requests
import sys
import traceback
import csv
from datetime import datetime
from datetime import timedelta
from lxml import etree
from tqdm import tqdm

class Weibo:
    cookie = {"Cookie": "_T_WM=2511a628e6fced6a05f7131cbb1c1dd5; SUB=_2A25xg5SMDeRhGeFO6VAY-S7LzT6IHXVSjzzErDV6PUJbkdAKLXXdkW1NQWscFJcav_-wQEwqRQMvJXMiTqmXP7mK; SUHB=0laFDJpsEHEnm9; SCF=Au3QOsGhtllfKXXXl3ZZsoRw5Rrhc92mZF0Q6Kpl1lw18X2drsD7z4dr_QK_hR-dDhcr-uVxYNnj9C5N0_BkgG8.; SSOLoginState=1552409820; MLOGIN=1; XSRF-TOKEN=fb01b2; WEIBOCN_FROM=1110006030; M_WEIBOCN_PARAMS=uicode%3D20000174"}  # 将your cookie替换成自己的cookie

    # Weibo类初始化
    def __init__(self, user_id, filter=0):
        self.user_id = user_id  # 用户id，即需要我们输入的数字，如昵称为“Dear-迪丽热巴”的id为1669879400
        self.filter = filter  # 取值范围为0、1，程序默认值为0，代表要爬取用户的全部微博，1代表只爬取用户的原创微博
        self.username = ''  # 用户名，如“Dear-迪丽热巴”
        self.weibo_num = 0  # 用户全部微博数
        self.weibo_num2 = 0  # 爬取到的微博数
        self.following = 0  # 用户关注数
        self.followers = 0  # 用户粉丝数
        self.weibo_content = []  # 微博内容
        self.weibo_place = []  # 微博位置
        self.publish_time = []  # 微博发布时间
        self.up_num = []  # 微博对应的点赞数
        self.retweet_num = []  # 微博对应的转发数
        self.comment_num = []  # 微博对应的评论数
        self.publish_tool = []  # 微博发布工具
        self.certification = [] # 微博认证内容
        self.big_V = True # 是不是大V
        self.following_id = [] # 用户关注列表
        self.following_num = [] # 用户关注的人的粉丝数

    # 获取用户昵称
    def get_username(self):
        try:
            url = "https://weibo.cn/%d/info" % (self.user_id)
            html = requests.get(url, cookies=self.cookie).content
            selector = etree.HTML(html)
            username = selector.xpath("//title/text()")[0]
            self.username = username[:-3]
            print(u"用户名: " + self.username)
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    # 获取用户微博数、关注数、粉丝数
    def get_user_info(self):
        try:
            url = "https://weibo.cn/u/%d?page=1" % (self.user_id)
            html = requests.get(url, cookies=self.cookie).content
            selector = etree.HTML(html)
            pattern = r"\d+\.?\d*"

            # 微博数
            str_wb = selector.xpath("//div[@class='tip2']/span[@class='tc']/text()")[0]
            guid = re.findall(pattern, str_wb, re.S | re.M)
            for value in guid:
                num_wb = int(value)
                break
            self.weibo_num = num_wb
            print(u"微博数: " + str(self.weibo_num))

            # 关注数
            str_gz = selector.xpath("//div[@class='tip2']/a/text()")[0]
            guid = re.findall(pattern, str_gz, re.M)
            self.following = int(guid[0])
            print(u"关注数: " + str(self.following))

            # 粉丝数
            str_fs = selector.xpath("//div[@class='tip2']/a/text()")[1]
            guid = re.findall(pattern, str_fs, re.M)
            self.followers = int(guid[0])
            print(u"粉丝数: " + str(self.followers))
            print(
                "===========================================================================")
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    # 获取"长原创微博"
    def get_long_weibo(self, weibo_link):
        try:
            html = requests.get(weibo_link, cookies=self.cookie).content
            selector = etree.HTML(html)
            info = selector.xpath("//div[@class='c']")[1]
            wb_content = info.xpath(
                "string(.)").replace(u"\u200b", "").encode(sys.stdout.encoding, "ignore").decode(
                sys.stdout.encoding)
            wb_time = info.xpath("//span[@class='ct']/text()")[0]
            wb_content = wb_content[wb_content.find(
                ":") + 1:wb_content.rfind(wb_time)]
            return wb_content
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    # 获取原创微博
    def get_original_weibo(self, info):
        try:
            weibo_content = info.xpath("string(.)").replace(u"\u200b", "").encode(
                sys.stdout.encoding, "ignore").decode(
                sys.stdout.encoding)
            weibo_content = weibo_content[:weibo_content.rfind(u"赞")]
            a_text = info.xpath("div//a/text()")
            if u"全文" in a_text:
                weibo_id = info.xpath("@id")[0][2:]
                weibo_link = "https://weibo.cn/comment/" + weibo_id
                wb_content = self.get_long_weibo(weibo_link)
                if wb_content:
                    weibo_content = wb_content
            return weibo_content
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    # 获取"长转发微博"
    def get_long_retweet(self, weibo_link):
        try:
            wb_content = self.get_long_weibo(weibo_link)
            wb_content = wb_content[:wb_content.rfind(u"原文转发")]
            return wb_content
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    # 获取转发微博
    def get_retweet(self, info):
        try:
            original_user = info.xpath("div/span[@class='cmt']/a/text()")
            if not original_user:
                wb_content = u"转发微博已被删除"
                return wb_content
            else:
                original_user = original_user[0]
            wb_content = info.xpath("string(.)").replace(u"\u200b", "").encode(
                sys.stdout.encoding, "ignore").decode(
                sys.stdout.encoding)
            wb_content = wb_content[wb_content.find(
                ":") + 1:wb_content.rfind(u"赞")]
            wb_content = wb_content[:wb_content.rfind(u"赞")]
            a_text = info.xpath("div//a/text()")
            if u"全文" in a_text:
                weibo_id = info.xpath("@id")[0][2:]
                weibo_link = "https://weibo.cn/comment/" + weibo_id
                wb_content = self.get_long_retweet(weibo_link)
                if wb_content:
                    weibo_content = wb_content
            retweet_reason = info.xpath("div")[-1].xpath("string(.)").replace(u"\u200b", "").encode(
                sys.stdout.encoding, "ignore").decode(
                sys.stdout.encoding)
            retweet_reason = retweet_reason[:retweet_reason.rindex(u"赞")]
            wb_content = (retweet_reason + "\n" + u"原始用户: " +
                          original_user + "\n" + u"转发内容: " + wb_content)
            return wb_content
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    # 获取微博内容
    def get_weibo_content(self, info):
        try:
            is_retweet = info.xpath("div/span[@class='cmt']")
            if is_retweet:
                weibo_content = self.get_retweet(info)
            else:
                weibo_content = self.get_original_weibo(info)
            self.weibo_content.append(weibo_content)
            print(weibo_content)
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    # 获取微博发布位置
    def get_weibo_place(self, info):
        try:
            div_first = info.xpath("div")[0]
            a_list = div_first.xpath("a")
            weibo_place = u"无"
            for a in a_list:
                if ("place.weibo.com" in a.xpath("@href")[0] and
                        a.xpath("text()")[0] == u"显示地图"):
                    weibo_a = div_first.xpath("span[@class='ctt']/a")
                    if len(weibo_a) >= 1:
                        weibo_place = weibo_a[-1]
                        if u"的秒拍视频" in div_first.xpath("span[@class='ctt']/a/text()")[-1]:
                            if len(weibo_a) >= 2:
                                weibo_place = weibo_a[-2]
                            else:
                                weibo_place = u"无"
                        weibo_place = weibo_place.xpath("string(.)").encode(
                            sys.stdout.encoding, "ignore").decode(sys.stdout.encoding)
                        break
            self.weibo_place.append(weibo_place)
            print(u"微博位置: " + weibo_place)
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    # 获取微博发布时间
    def get_publish_time(self, info):
        try:
            str_time = info.xpath("div/span[@class='ct']")
            str_time = str_time[0].xpath("string(.)").encode(
                sys.stdout.encoding, "ignore").decode(sys.stdout.encoding)
            publish_time = str_time.split(u'来自')[0]
            if u"刚刚" in publish_time:
                publish_time = datetime.now().strftime(
                    '%Y-%m-%d %H:%M')
            elif u"分钟" in publish_time:
                minute = publish_time[:publish_time.find(u"分钟")]
                minute = timedelta(minutes=int(minute))
                publish_time = (datetime.now() - minute).strftime(
                    "%Y-%m-%d %H:%M")
            elif u"今天" in publish_time:
                today = datetime.now().strftime("%Y-%m-%d")
                time = publish_time[3:]
                publish_time = today + " " + time
            elif u"月" in publish_time:
                year = datetime.now().strftime("%Y")
                month = publish_time[0:2]
                day = publish_time[3:5]
                time = publish_time[7:12]
                publish_time = (year + "-" + month + "-" + day + " " + time)
            else:
                publish_time = publish_time[:16]
            self.publish_time.append(publish_time)
            print(u"微博发布时间: " + publish_time)
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    # 获取微博发布工具
    def get_publish_tool(self, info):
        try:
            str_time = info.xpath("div/span[@class='ct']")
            str_time = str_time[0].xpath("string(.)").encode(
                sys.stdout.encoding, "ignore").decode(sys.stdout.encoding)
            if len(str_time.split(u'来自')) > 1:
                publish_tool = str_time.split(u'来自')[1]
            else:
                publish_tool = u"无"
            self.publish_tool.append(publish_tool)
            print(u"微博发布工具: " + publish_tool)
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    # 获取用户微博信息
    def get_weibo_info(self):
        try:
            url = "https://weibo.cn/u/%d?page=1" % (
                self.user_id)
            html = requests.get(url, cookies=self.cookie).content
            selector = etree.HTML(html)
            if selector.xpath("//input[@name='mp']") == []:
                page_num = 1
            else:
                page_num = (int)(selector.xpath(
                    "//input[@name='mp']")[0].attrib["value"])
            pattern = r"\d+\.?\d*"
            for page in tqdm(range(1, page_num + 1), desc=u"进度"):
                url2 = "https://weibo.cn/u/%d?page=%d" % (self.user_id, page)
                html2 = requests.get(url2, cookies=self.cookie).content
                selector2 = etree.HTML(html2)
                info = selector2.xpath("//div[@class='c']")
                is_empty = info[0].xpath("div/span[@class='ctt']")
                if is_empty:
                    for i in range(0, len(info) - 2):
                        is_retweet = info[i].xpath("div/span[@class='cmt']")
                        if (not self.filter) or (not is_retweet):

                            # 微博内容
                            self.get_weibo_content(info[i])

                            # 微博位置
                            self.get_weibo_place(info[i])

                            # 微博发布时间
                            self.get_publish_time(info[i])

                            # 微博发布工具
                            self.get_publish_tool(info[i])

                            str_footer = info[i].xpath("div")[-1]
                            str_footer = str_footer.xpath("string(.)").encode(
                                sys.stdout.encoding, "ignore").decode(sys.stdout.encoding)
                            str_footer = str_footer[str_footer.rfind(u'赞'):]
                            guid = re.findall(pattern, str_footer, re.M)

                            # 点赞数
                            up_num = int(guid[0])
                            self.up_num.append(up_num)
                            print(u"点赞数: " + str(up_num))

                            # 转发数
                            retweet_num = int(guid[1])
                            self.retweet_num.append(retweet_num)
                            print(u"转发数: " + str(retweet_num))

                            # 评论数
                            comment_num = int(guid[2])
                            self.comment_num.append(comment_num)
                            print(u"评论数: " + str(comment_num))

                            self.weibo_num2 += 1
                            print(
                                "===========================================================================")

            if not self.filter:
                print(u"共" + str(self.weibo_num2) + u"条微博")
            else:
                print(u"共" + str(self.weibo_num) + u"条微博，其中" +
                      str(self.weibo_num2) + u"条为原创微博"
                      )
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()
            
    # 获取微博认证资料
    def get_certification(self):
        try:
            url = "https://weibo.cn/u/%d" % self.user_id
            html = requests.get(url, cookies=self.cookie).content
            selector = etree.HTML(html)
            str_cer = selector.xpath("//div[@class='ut']//span[@class='ctt']/text()")
            
            self.certification = []
            if str_cer : # 名字及认证信息非空
                self.certification = str_cer[0]
                for p in str_cer:
                    self.certification = self.certification + p
            return self.certification
        
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()
            
    # 获取微博大V标志
    def get_big_V(self):
        try:
            url = "https://weibo.cn/u/%d" % self.user_id
            html = requests.get(url, cookies=self.cookie).content
            selector = etree.HTML(html)
            big_v_symbol = selector.xpath("//span[@class='ctt']/img[@alt='V']")
            self.big_V = True
            if not big_v_symbol:
                self.big_V = False
            return self.big_V
        
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    # 获取用户微博关注列表
    def get_following_list(self):
        try:
            url = "https://weibo.cn/%d/follow?page=" % (self.user_id)
            url_init = url + "1"
            html = requests.get(url_init, cookies=self.cookie).content
            selector = etree.HTML(html)
            try:
                pageNum = (int)(selector.xpath('//input[@name="mp"]')[0].attrib['value']) # 获取关注人页数
            except:
                pageNum = 1 # 只有1页
            
            for i in range(1,pageNum+1):
                url_new = url + (str)(i)
                html = requests.get(url_new, cookies=self.cookie).content # cookie登录
                selector = etree.HTML(html)

                following_info = selector.xpath("//td[@style='width: 52px']/a/@href")
                followers_info = selector.xpath("//td[@valign='top']/text()")

                for j in range(len(following_info)):
                    guid = re.findall(r"/\d+\.?\d*", following_info[j], re.M)
                    # 获取关注者id
                    if guid:
                        fid1 = re.findall(r"\d+\.?\d*", following_info[j], re.M)
                        self.following_id.append(int(fid1[0]))
                        fid2 = re.findall(r"\d+\.?\d*", followers_info[j], re.M)
                        self.following_num.append(int(fid2[0]))
                        
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()
            
    
    # 将爬取的信息写入文件
    def write_txt(self):
        try:
            if self.filter:
                result_header = u"\n\n原创微博内容: \n"
            else:
                result_header = u"\n\n微博内容: \n"
            result = (u"用户信息\n用户昵称：" + self.username +
                      u"\n用户id: " + str(self.user_id) +
                      u"\n微博数: " + str(self.weibo_num) +
                      u"\n关注数: " + str(self.following) +
                      u"\n粉丝数: " + str(self.followers) +
                      result_header
                      )
            for i in range(1, self.weibo_num2 + 1):
                text = (str(i) + ":" + self.weibo_content[i - 1] + "\n" +
                        u"微博位置: " + self.weibo_place[i - 1] + "\n" +
                        u"发布时间: " + self.publish_time[i - 1] + "\n" +
                        u"点赞数: " + str(self.up_num[i - 1]) +
                        u"	 转发数: " + str(self.retweet_num[i - 1]) +
                        u"	 评论数: " + str(self.comment_num[i - 1]) + "\n" +
                        u"发布工具: " + self.publish_tool[i - 1] + "\n\n"
                        )
                result = result + text
            file_dir = os.path.split(os.path.realpath(__file__))[0] + os.sep + "weibo"
            if not os.path.isdir(file_dir):
                os.mkdir(file_dir)
            file_path = file_dir + os.sep + "%d" % self.user_id + ".txt"
            f = open(file_path, "wb")
            f.write(result.encode(sys.stdout.encoding))
            f.close()
            print(u"微博写入文件完毕，保存路径:")
            print(file_path)
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    # 将爬取的信息写入csv
    def write_csv(self):
        try:
            # 写入头文件
#            file_dir = os.path.split(os.path.realpath(__file__))[0] + os.sep + "weibo"
#            if not os.path.isdir(file_dir):
#                os.mkdir(file_dir)
#            file_path = file_dir + os.sep + "weibo_info.csv"
#            with open(file_path, mode='a') as csv_file:
#                csv_file = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
#                csv_file.writerow([self.user_id, self.username, self.weibo_num, self.following, self.followers])
#            print(u"信息写入csv完毕，保存路径:")
#            print(file_path)
            
            # 写入微博内容
            self.weibo_content = [w.replace('，', ' ') for w in self.weibo_content]
            self.weibo_content = [w.replace(',', ' ') for w in self.weibo_content]            
            file_dir = os.path.split(os.path.realpath(__file__))[0] + os.sep + "weibo"
            if not os.path.isdir(file_dir):
                os.mkdir(file_dir)
            file_path = file_dir + os.sep + "%d" % self.user_id + ".csv"            
            with open(file_path, mode='w') as csv_file:
                csv_file = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_file.writerow(['内容', '位置', '发布时间', '获得点赞数', '获得转发数', '获得评论数', '发布工具'])
                for i in range(1, self.weibo_num2 + 1):
                    csv_file.writerow([self.weibo_content[i-1], self.weibo_place[i-1], self.publish_time[i-1], \
                                       self.up_num[i-1], self.retweet_num[i-1], self.comment_num[i-1], \
                                       self.publish_tool[i-1]])                    
            print(u"微博写入csv完毕，保存路径:")
            print(file_path)
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    # 运行爬虫
    def start(self):
        try:
            self.get_username()
            self.get_user_info()
            self.get_weibo_info()
            self.write_txt()
            self.write_csv()
            print(u"信息抓取完毕")
            print(
                "===========================================================================")
        except Exception as e:
            print("Error: ", e)