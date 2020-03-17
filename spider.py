# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup
import bilibili as bili
from requests import RequestException
from tqdm import tqdm
import requests, time, re
import os, sys, threading
import subprocess

class spider():
    def __init__(self):
        self.getHtmlHeaders={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q = 0.9'
        }

    def getHtml(self,url):
        try:
            response = requests.get(url=url, headers= self.getHtmlHeaders)
            print(response.status_code)
            if response.status_code == 200:
                return response.text
        except RequestException:
            print('请求Html错误:')

    def parseHtml(self,html):
        bs = BeautifulSoup(html, "html.parser")  # 缩进格式

        video_urls = []

        for div in bs.find_all('div', class_='video_small_intro'):
            for item in div.find_all("a"):
                video_urls.append(item.get("href"))

        print(video_urls)

        return video_urls

    def getVideoUrl(self,html):
        bs = BeautifulSoup(html, "html.parser")

        video_url =''
        for item in bs.find_all("video"):
            video_url = item.get("src")
            break
        return video_url

    def dowmloadVideos0(self,urls):
        currentVideoPath = os.path.join(sys.path[0], 'video')
        if not os.path.exists(currentVideoPath):
            os.makedirs(currentVideoPath)
        for url in urls:
            if url.find("baidu") >= 0:
                video_name = time.strftime('%Y%m%d-%H%M%S', time.localtime(time.time())) + ".mp4"
                self.down_from_url(self.getVideoUrl(self.getHtml(url)), video_name)
            else:
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

    def dowmloadVideos(self,urls):
        currentVideoPath = os.path.join(sys.path[0], 'video')
        if not os.path.exists(currentVideoPath):
            os.makedirs(currentVideoPath)
        for url in urls:
            print('url:' + url)
            if url.find("baidu") >= 0:
                video_name = time.strftime('%Y%m%d-%H%M%S', time.localtime(time.time())) + ".mp4"
                self.down_from_url(self.getVideoUrl(self.getHtml(url)), video_name)
            elif url.find("bilibili") >= 0:
                bilibili = bili.bilibili()
                # 用户输入av号或者视频链接地址
                start = url
                if start.isdigit() == True:  # 如果输入的是av号
                    # 获取cid的api, 传入aid即可
                    start_url = 'https://api.bilibili.com/x/web-interface/view?aid=' + start
                else:
                    # https://www.bilibili.com/video/av46958874/?spm_id_from=333.334.b_63686965665f7265636f6d6d656e64.16
                    start_url = 'https://api.bilibili.com/x/web-interface/view?aid=' + re.search(r'/av(\d+)/*',
                                                                                                 start).group(1)

                # 视频质量
                # <accept_format><![CDATA[flv,flv720,flv480,flv360]]></accept_format>
                # <accept_description><![CDATA[高清 1080P,高清 720P,清晰 480P,流畅 360P]]></accept_description>
                # <accept_quality><![CDATA[80,64,32,16]]></accept_quality>
                # quality = input('请输入您要下载视频的清晰度(1080p:80;720p:64;480p:32;360p:16)(填写80或64或32或16):')
                quality = 80
                # 获取视频的cid,title
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
                }
                html = requests.get(start_url, headers=headers).json()
                data = html['data']
                cid_list = []
                if '?p=' in start:
                    # 单独下载分P视频中的一集
                    p = re.search(r'\?p=(\d+)', start).group(1)
                    cid_list.append(data['pages'][int(p) - 1])
                else:
                    # 如果p不存在就是全集下载
                    cid_list = data['pages']
                # print(cid_list)
                # 创建线程池
                threadpool = []
                title_list = []
                for item in cid_list:
                    cid = str(item['cid'])
                    title = item['part']
                    title = re.sub(r'[\/\\:*?"<>|]', '', title)  # 替换为空的
                    print('[下载视频的cid]:' + cid)
                    print('[下载视频的标题]:' + title)
                    title_list.append(title)
                    page = str(item['page'])
                    start_url = start_url + "/?p=" + page
                    video_list = bilibili.get_play_list(start_url, cid, quality)
                    start_time = time.time()
                    # down_video(video_list, title, start_url, page)
                    # 定义线程
                    th = threading.Thread(target=bilibili.down_video, args=(video_list, title, start_url, page))
                    # 将线程加入线程池
                    threadpool.append(th)

                # 开始线程
                for th in threadpool:
                    th.start()
                # 等待所有线程运行完毕
                for th in threadpool:
                    th.join()

                # 最后合并视频
                print(title_list)
                bilibili.combine_video(title_list)

                end_time = time.time()  # 结束时间
                print('下载总耗时%.2f秒,约%.2f分钟' % (end_time - bilibili.start_time, int(end_time - bilibili.start_time) / 60))
                # 如果是windows系统，下载完成后打开下载目录
                currentVideoPath = os.path.join(sys.path[0], 'video')  # 当前目录作为下载目录
                if (sys.platform.startswith('win')):
                    os.startfile(currentVideoPath)
            else:
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

    def down_from_url(self, url, dst):
        response = requests.get(url, stream=True)  # (1)
        file_size = int(response.headers['content-length'])  # (2)
        if os.path.exists(dst):
            first_byte = os.path.getsize(dst)  # (3)
        else:
            first_byte = 0
        if first_byte >= file_size:  # (4)
            return file_size

        header = {"Range": f"bytes={first_byte}-{file_size}"}

        pbar = tqdm(total=file_size, initial=first_byte, unit='B', unit_scale=True, desc=dst)
        req = requests.get(url, headers=header, stream=True)

        with open(os.path.join(sys.path[0], 'video', dst), 'ab') as f:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    pbar.update(1024)
        pbar.close()
        return file_size