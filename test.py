# -*- coding:utf-8 -*-
import spider
import time
import os,sys
import subprocess

if __name__ == '__main__':
    url = input("Input URL: ")

    spider = spider.spider()
    if url.find("baidu") >= 0:
        video_name = time.strftime('%Y%m%d-%H%M%S', time.localtime(time.time())) + ".mp4"
        spider.down_from_url(spider.getVideoUrl(spider.getHtml(url)), video_name)
    elif url.find("iqiyi") >= 0:
        currentVideoPath = os.path.join(sys.path[0], 'video')
        if not os.path.exists(currentVideoPath):
            os.makedirs(currentVideoPath)

        scenedetect_cmd = ["python", "you-get.py", url, "-o", "video"]

        process = subprocess.Popen(scenedetect_cmd,
                                   stderr=subprocess.STDOUT,
                                   stdout=subprocess.PIPE,
                                   shell=True)

        while True:
            output = process.stdout.readline().strip()
            print(output)
            if process.poll() is not None:
                break
    elif url.find("bilibili") >= 0:
        spider.dowmloadVideos([url])
