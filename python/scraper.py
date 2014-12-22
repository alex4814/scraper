import sys
import urllib2
from bs4 import BeautifulSoup
from ghost import Ghost

url_home = 'http://guba.eastmoney.com/'
url_bar = url_home + 'list,%d,f_%d.html'

bid = 600112
today = '12-14'

def process(link):
    # process topic content
    html = urllib2.urlopen(link).read()
    soup = BeautifulSoup(html, "lxml")

    p_info = soup.find(id='zwcontt')
    p_name = p_info.find(id='zwconttbn').text.strip()
    p_datetime = p_info.find(class_='zwfbtime').text[4:] # erase leading chinese

    p_body = soup.find(class_='zwcontentmain')
    p_title = p_body.find(id='zwconttbt').text.strip()
    p_content = p_body.find(id='zwconbody').text.strip()
    print p_name, p_title, p_content

    # process each comment after topic
    url_topic = link[:-5] + "_%d.html"
    page = 1
    while True:
        if page > 1:
            url = url_topic % (page)
            html = urllib2.urlopen(url).read()
            soup = BeautifulSoup(html, "lxml")
        cmts = soup("div", class_="zwli")
        if len(cmts) == 0:
            break
        for cmt in cmts:
            c_name = cmt.find(class_='zwlianame').text.strip()
            c_datetime = cmt.find(class_='zwlitime').text[4:].strip()
            c_content = cmt.find(class_='zwlitext').text.strip()
            print '\t', c_name, c_datetime, c_content, '\n'
        page += 1

def scrape():
    page = 1
    finish = False
    while (not finish):
        url = url_bar % (bid, page)
        html_bar = urllib2.urlopen(url).read()
        soup = BeautifulSoup(html_bar, "lxml")

        arts = soup("div", class_="articleh")
        for topic in arts:
            date = topic.find("span", class_="l6").string
            title = topic.find("span", class_="l3")
            mark = title.em.string if title.em else None

            # eliminate top topics
            if mark and 'settop' in title.em['class']:
                continue

            # process only topics posted after a certain day
            if date < today and not mark:
                finish = True
                break

            # process each topic and comments
            link = url_home + title.a['href']
            process(link)
        page += 1

#link = 'http://guba.eastmoney.com/news,600112,135768083.html';
#process(link)
#process('http://guba.eastmoney.com/news,600010,135749798.html')
reload(sys)
sys.setdefaultencoding('utf-8')
scrape()
