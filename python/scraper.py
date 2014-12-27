# coding: utf-8

import sys, os
import csv
import codecs
import urllib2
import datetime
from bs4 import BeautifulSoup
from selenium import webdriver

url_home = 'http://guba.eastmoney.com/'
url_bar = url_home + 'list,%d,f_%d.html'
header = {
    'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11',
    'Accept-Charset': 'GBK,utf-8;q=0.7,*;q=0.3'
}

class Driver:
    def __init__(self):
        self.driver = webdriver.PhantomJS()
        self.driver.set_window_size(1024, 768)

    def get_html(self, url):
        self.driver.get(url);
        return self.driver.page_source

    def quit(self):
        self.driver.quit()

def make_dir(fn):
    if not os.path.exists(fn):
        os.mkdir(fn)

def process(link, p_mark, csvfile):
    # process topic content
    #html = urllib2.urlopen(link).read()
    html = a_driver.get_html(link)
    soup = BeautifulSoup(html, "lxml")

    p_content = soup.find(id='zwcontent')
    if not p_content:
        return
    p_info = soup.find(id='zwcontt')
    p_name = p_info.find(id='zwconttbn').strong.text.strip()
    p_datetime = p_info.find(class_='zwfbtime').text[4:] # erase leading chinese

    p_body = soup.find(class_='zwcontentmain')
    p_title = p_body.find(id='zwconttbt').text.strip()
    p_content = p_body.find(id='zwconbody').text.strip()
    zf = p_body.find(id='zwconbtnsi_zf')
    p_zf = zf.span.text.strip() if zf.span else str(0)
    zan = p_body.find(id='zwpraise')
    p_zan = zan.span.text.strip() if zan.span else str(0)

    p_item = (p_mark if p_mark else '', p_name, p_datetime, p_title, p_content, p_zf, p_zan)

    # process each comment after topic
    url_topic = link[:-5] + "_%d.html"
    rows = [p_item]
    n = int(soup.find(class_='zwhpager').span.text.strip())
    for page in range(1, n + 1):
        if page > 1:
            url = url_topic % (page)
            #html = urllib2.urlopen(url).read()
            html = a_driver.get_html(url)
            soup = BeautifulSoup(html, "lxml")
        cmts = soup("div", class_="zwli")
        if len(cmts) == 0:
            break
        #print 'lens of comments', len(cmts)
        for cmt in cmts:
            c_name = cmt.find(class_='zwlianame').strong.text.strip()
            c_datetime = cmt.find(class_='zwlitime').text[4:].strip()
            c_content = cmt.find(class_='zwlitext')
            c_text = c_content.text.strip()
            for img in c_content.find_all('img'):
                c_text = c_text + '[' + img['title'].strip() + ']'
            czan = cmt.find(class_='replylikelink')
            c_zan = czan.span.text.strip() if czan and czan.span else str(0)

            c_item = (c_name, c_datetime, c_text, c_zan)
            rows.append(c_item)
            #print '\t', c_name, c_datetime, c_content, '\n'

    writer = csv.writer(csvfile)
    writer.writerows(rows)
    writer.writerow([])

def scrape(bid, crawl_date):
    # preparing to write
    make_dir('data')
    make_dir('data/' + str(bid))
    uri_file = 'data/%d/%s.csv' % (bid, crawl_date)
    if os.path.exists(uri_file):
        return
    csvfile = file(uri_file, 'wb')
    csvfile.write(codecs.BOM_UTF8)

    page = 1
    finish = False
    while (not finish):
        url = url_bar % (bid, page)
        print '\turl:', url
        html_bar = a_driver.get_html(url)
        #req = urllib2.Request(url, headers = header)
        #html_bar = urllib2.urlopen(req).read()
        #print html_bar
        soup = BeautifulSoup(html_bar, "lxml")

        arts = soup("div", class_="articleh")
        print '\t%d articles found.' % len(arts)
        if len(arts) == 0:
            break

        for topic in arts:
            date = topic.find("span", class_="l6").text.strip()
            title = topic.find("span", class_="l3")
            mark = title.em.string if title.em else None

            # eliminate top topics
            if mark and 'settop' in title.em['class']:
                continue

            # process only topics posted after a certain day
            if date < crawl_date and not mark:
                finish = True
                break
            if not date == crawl_date:
                continue

            # process each topic and comments
            link = url_home + title.a['href']
            print '\tproccessing topic:', date, title.text.strip()
            process(link, mark, csvfile)
        page += 1
        
    csvfile.close()

# pre-work
reload(sys)
sys.setdefaultencoding('utf-8')

# main
a_driver = Driver()

yesterday = datetime.date.today() - datetime.timedelta(days = 1)
crawl_date = yesterday.strftime('%m-%d')

for i in range(4000):
    bid = i + 600000
    print 'crawling:', str(bid), crawl_date
    scrape(bid, crawl_date)
#scrape(600101, '12-25')

# final
a_driver.quit()

