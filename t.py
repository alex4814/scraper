# coding: utf-8

import sys, os, re
import time, datetime
import csv, codecs
from threading import Thread
from Queue import Queue
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0

## encoding setting ##
reload(sys)
sys.setdefaultencoding('utf-8')


## constants ##
MAX_THREADS = 4
MAX_ATTEMPTS = 3
url_home = 'http://guba.eastmoney.com/'
url_bar = 'http://guba.eastmoney.com/list,%s,f_%d.html'
HOME = 'contents'
DATA = 'data'

# regular expression rules
re_dt = re.compile(r'[^0-9 :-]') # matching only datetime format


## helper functions ##
def create_directory(path):
  if not os.path.exists(path):
    os.mkdir(path)

def extract_post(pst):
  item = []
  # author information of the post 
  name = pst.find(id='zwconttbn').strong.text.strip()
  item.append(name) # author name

  # author's influence
  star, year = '0', '0'
  p_inf = pst.find(class_='influence')
  if p_inf:
    s1 = p_inf.span
    star = s1['class'][1]
    s2 = s1.find_next_sibling('span')
    year = s2.text if s2 else '0'
  item.append(star) # stars, stars45 means 4.5 of 5 stars
  item.append(year) # years active in this bar

  # post information
  p_title = pst.find(id='zwconttbt').text.strip()
  item.append(p_title) # post title

  p_datetime = pst.find(class_='zwfbtime').text
  p_datetime = re_dt.sub('', p_datetime).strip() 
  item.append(p_datetime) # post datetime

  p_content = pst.find(id='zwconbody').text.strip()
  item.append(p_content) # post content

  zf = pst.find(id='zwconbtnsi_zf')
  p_zf = zf.span.text.strip() if zf.span else str(0)
  item.append(p_zf) # number of forwards of this post

  zan = pst.find(id='zwpraise')
  p_zan = zan.span.text.strip() if zan.span else str(0)
  item.append(p_zan) # number of likes of this post

  # format of the post TUPLE is define below:
  # (author name, author stars, author years,
  #  post title, post datetime, post content,
  #  post forwards, post likes)
  return tuple(item)

def extract_comment(cmt):
  item = []
  # comment author's information
  c_name = cmt.find(class_='zwlianame').strong.text.strip()
  item.append(c_name) # comment author's name

  # comment author's influence
  star, year = '0', '0'
  c_inf = cmt.find(class_='influence')
  if c_inf:
    s1 = c_inf.span
    star = s1['class'][1]
    s2 = s1.find_next_sibling('span')
    year = s2.text if s2 else '0'
  item.append(star) # stars, stars45 means 4.5 of 5 stars
  item.append(year) # years active in this bar

  # comment information
  c_datetime = cmt.find(class_='zwlitime').text
  c_datetime = re_dt.sub('', c_datetime).strip() 
  item.append(c_datetime) # comment datetime

  c_content = cmt.find(class_='zwlitext')
  c_text = [ c_content.text.strip() ]
  for img in c_content.find_all('img'):
    c_text.append('[%s]' % img['title'].strip()) # transform each images to texts
  item.append(''.join(c_text)) # comment content

  zan = cmt.find(class_='zwlibtns').a
  c_zan = zan.span.text.strip() if zan.span else str(0)
  item.append(c_zan) # number of likes of this comment

  # format of the comment TUPLE is define below:
  # (comment author name, comment author stars, comment author years,
  #  comment datetime, comment content, comment likes)
  return tuple(item)

def extract_comments(link, cnt):
  if cnt == 0:
    return
  p = webdriver.PhantomJS()
  p.get(link)
  print 'accessing comment link:', link
  time.sleep(0.2) # let the page load
  try:
    ele_pre = 'zwlist'
    e = WebDriverWait(p, 10).until(EC.presence_of_element_located((By.ID, ele_pre)))
    # process each comment
    items = []
    soup = BeautifulSoup(p.page_source)
    comments = soup(class_='zwli')
    if len(comments) == 0:
      print 'no comments found on this page:', link
      return items
    for c in comments:
      try:
        t_comment = extract_comment(c)
        items.append(t_comment)
      except Exception as e:
        print e
    return items
  except Exception as e:
    print e
    print 'excption catched in function extract_comments'
    extract_comments(link, cnt - 1)
  finally:
    p.quit()

def write_post_and_comments_to_file(id_bar, date, items):
  dir_dest = '%s/%s' % (DATA, id_bar)
  create_directory(dir_dest)
  file_dest = '%s/%s.csv' % (dir_dest, date)
  with open(file_dest, 'ab') as csvfile:
    csvfile.write(codecs.BOM_UTF8)
    writer = csv.writer(csvfile)
    writer.writerows(items)
    writer.writerow([]) # append a new line after one post

def extract(link, html):
  soup = BeautifulSoup(html, 'lxml')
  items = []

  # post information
  zwcontent = soup.find(id='zwcontent')
  t_post = extract_post(zwcontent)
  date = t_post[4].split(' ')[0] # post date as the file name
  items.append(t_post) # post content inserted to the list
  print 'post extraction succeeded'

  # comment information below that post
  n_page = soup.find(class_='zwhpager').span.text
  print '%s pages of comments.' % n_page
  url_comment = ''.join( [ link[:-5], '_%d.html' ] )
  for i in range(int(n_page)):
    url = url_comment % (i + 1)
    comments = extract_comments(url, MAX_ATTEMPTS)
    print 'comments extraction in page %d succeeded' % (i + 1)
    items = items + comments

  # write post and comments to file
  id_bar = link.split(',')[1] # extract the id between two ',' in the link
  write_post_and_comments_to_file(id_bar, date, items)

def process(link, cnt):
  if cnt == 0:
    return False
  p = webdriver.PhantomJS(executable_path='/usr/local/bin/phantomjs')
  p.get(link)
  print 'accesing post link:', link
  time.sleep(0.2) # let the page load
  try:
    ele_pre = 'mainbody'
    e = WebDriverWait(p, 10).until(EC.presence_of_element_located((By.ID, ele_pre)))
    extract(link, p.page_source)
  except Exception as e:
    print e
    print 'excption catched in function process'
    process(link, cnt - 1)
  finally:
    p.quit()
  return True

def extract_and_record(id_bar):
  dir_dest = '%s/%d' % (HOME, id_bar)
  with open('%s/post_links.txt' % dir_dest, 'r') as f:
    while True:
      link = f.readline() 
      if len(link) == 0:
        break
      link = link[:-1] # erase trailing '\n'

      # prevent from crashing when can't connect to GhostDriver
      cnt = MAX_ATTEMPTS
      suc = False
      while cnt > 0 and not suc:
        try:
          suc = process(link, MAX_ATTEMPTS)
        except Exception as e:
          print e
          print 'Error may be the Driver'
          cnt = cnt - 1

## main logic ##
create_directory('%s/' % DATA)

"""
def worker():
  while True:
    item = q.get()
    extract_and_record(item)
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
"""

## function process testing ##
"""
l = 'http://guba.eastmoney.com/news,szzs,141515442.html'
l2 = 'http://guba.eastmoney.com/news,600001,136130294.html'
process(l, MAX_ATTEMPTS)
"""

## function extract_and_record testing ##
extract_and_record(600001)
