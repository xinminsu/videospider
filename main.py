# -*- coding:utf-8 -*-

import spider

if __name__ == '__main__':
    word = input("Input key word: ")
    url = 'https://www.baidu.com/sf/vsearch?wd=' + word + '&pd=video'
    spider = spider.spider()
    urls = spider.parseHtml(spider.getHtml(url))
    spider.dowmloadVideos(urls)