# -*- coding:utf-8 -*-
import spider
import time

if __name__ == '__main__':
    word = input("Input key word: ")
    url = 'https://www.baidu.com/sf/vsearch?wd=' + word + '&pd=video'
    spider = spider.spider()
    if url.find("baidu") >= 0 or url.find("iqiyi") >= 0:
        video_name = time.strftime('%Y%m%d-%H%M%S', time.localtime(time.time())) + ".mp4"
        spider.down_from_url(spider.getVideoUrl(spider.getHtml(url)), video_name)
    elif url.find("bilibili") >= 0:
        spider.dowmloadVideos([url])
