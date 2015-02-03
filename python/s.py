# coding: utf-8

import sys, os, re
import time, datetime
import requests
from threading import Thread
from Queue import Queue
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding('utf-8')


## constants ##
MAX_THREADS = 4
url_home = 'http://guba.eastmoney.com/'
url_bar = 'http://guba.eastmoney.com/list,%s,f_%d.html'
HOME = 'contents'

# regular expression rules
re_td = re.compile(r'[^0-9 :-]') # matching only datetime format


## helper functions ##
def get_post_date(url):
  response = requests.get(url)
  soup = BeautifulSoup(response.text, 'lxml')
  post_date_time = soup.find(class_='zwfbtime').text
  post_date_time = re_td.sub('', post_date_time).strip()
  # first 10 chars represent date, ignoring the time
  return post_date_time[:10] 

def create_directory(path):
  if not os.path.exists(path):
    os.mkdir(path)
  
def write_links_to_file(id_bar, links):
  dir_dest = '%s/%d' % (HOME, id_bar)
  create_directory(dir_dest)
  with open('%s/post_links.txt' % dir_dest, 'w+') as f:
    f.writelines(set(links))

def record_valid_posts(id_bar, date_begin, date_end):
  links = []
  n = 1
  finished = False
  while not finished:
    url = url_bar % (str(id_bar), n)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    posts = soup(class_='articleh')
    print '%d posts found in page %d.' % (len(posts), n)
    if len(posts) == 0:
      break
    for post in posts:
      title = post.find(class_='l3')
      link = ''.join( [url_home, title.a['href']] )
      post_date = get_post_date(link)
      if post_date >= date_end:
        continue
      if post_date < date_begin and not title.em:
        finished = True
        break
      print '\tlink: %s' % link
      print '\tpost date: %s' % post_date
      links.append(link + '\n') # valid link to process
    n = n + 1
  write_links_to_file(id_bar, links)

## main logic ##
# input parameters
date_begin = '2014-07-01'
date_end = '2015-02-01' # [date_begin, date_end)
id_bar = -1

# prework
create_directory('%s/' % HOME)

# threading using Queue
def worker():
  while True:
    item = q.get()
    record_valid_posts(item, date_begin, date_end)
    q.task_done()

q = Queue()
for i in range(MAX_THREADS):
  t = Thread(target = worker)
  t.daemon = True
  t.start()

for i in range(500):
  item = i + 600000
  q.put(item)

q.join()
