#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from scipy.misc import imsave
import random
import json
import io

import ImageDao
import UserDao

#This class handles any incoming request 
class myHandler(BaseHTTPRequestHandler):
  
  def __init__(self):
    self.ImageDao = ImageDao.ImageDao
    self.UserDao = UserDao.UserDao
  
  #Handler for the GET requests
  def do_GET(self):
    self.send_response(200)
    self.send_header('Content-type','text/html')
    self.end_headers()
    self.wfile.write("Hello World!")
    return
  
  def do_POST(self):
    self.send_response(200)
    return



PORT_NUMBER = 8082
try:
  server = HTTPServer(('', PORT_NUMBER), myHandler)
  print 'Started http server on port', PORT_NUMBER

  #Wait forever for incoming htto requests
  server.serve_forever()

except KeyboardInterrupt:
  print '^C received, shutting down the web server'
  server.socket.close()
