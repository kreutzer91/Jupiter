#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from scipy.misc import imsave
import random
import json
import io
import os
from sshtunnel import SSHTunnelForwarder
#import array
from scipy.misc import imread

from handler import *
from database_class import *

# import socket
PORT_NUMBER = 8082

# class HTTPServerV6(HTTPServer):
#   address_family = socket.AF_INET6
  
try:
  myHandler.mdb = MySqlDatabase(host='localhost', user = 'phoebeybc7', password='Yingbich1991')
  myHandler.mdb.connectToDB()
  print("Connected to database")
  #Create a web server and define the handler to manage the
  #incoming request
  server = HTTPServer(('', PORT_NUMBER), myHandler)
  print 'Started httpserver on port ' , PORT_NUMBER

  #Wait forever for incoming htto requests
  server.serve_forever()

except KeyboardInterrupt:
  print '^C received, shutting down the web server'
  server.socket.close()