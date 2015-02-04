# coding: utf-8

import sys, os, re
import time, datetime
from threading import Thread
from Queue import Queue
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0

## encoding setting ##
reload(sys)
sys.setdefaultencoding('utf-8')

## constants ##
MAX_THREADS = 4
url_home = 'http://guba.eastmoney.com/'
url_bar = 'http://guba.eastmoney.com/list,%s,f_%d.html'
HOME = 'contents'

## helper functions ##
def process(link):
  p = webdriver.PhantomJS()
  p.get(link)
  try:
    e = WebDriverWait(p, 10).until(EC.presence_of_element_located((By.ID, "mainbody")))
  finally:
    p.quit()

def extract_and_record(id_bar):
  dir_dest = '%s/%d' % (HOME, id_bar)
  with open('%s/post_links.txt' % dir_dest, 'r') as f:
    while True:
      link = f.readline() 
      if len(link) == 0:
        break
      link = link[:-1] # erase trailing '\n'
      process(link)

extract_and_record(600000)
