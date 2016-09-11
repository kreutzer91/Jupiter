
# coding: utf-8

# In[153]:

from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import io
import sys
import http.client
import json
import base64
import uuid
import pymysql.cursors

get_ipython().magic(u'matplotlib inline')


# In[41]:

def CreateUser(http_server, user_name, pass_word):
    headers = {"user_name": user_name,
               "password": pass_word,
               "mode": "create_user",
              }
    conn = http.client.HTTPConnection(http_server)
    conn.request("POST","","", headers)
    rsp = conn.getresponse()
    is_success=rsp.getheader('status')
    conn.close()
    return is_success,user_name


# In[191]:

class _db_select_struct():
  # for one image
  def __init__(self, Image):
    self.select = 0 #real --- how many users select
    self.clients = [] # array ---- selected user-IDs
    self.image = Image.copy() # raw image


class ImageSelectRequestStruct():
  '''
  Send Request of scoring my images
  '''
  
  ResultReadyNumber = 20 
  MAX_IMAGES = 5
  
  def __init__(self, ownerID):
    '''
    ImageArray ------ list of numpy.ndarray
    userID ---------- the user ID of the requesting user,
                      unique string type
    
    '''
    
    # Image is a dictionary which map the name to struct
    self.Image = {}
    self.ownerID = ownerID
    self.NumImage = 0
    # the bool 'Ready' is the flag to indicate whether the result
    # is ready to send back to owner
    self.Ready = False
    
  def _add_one_image(self,image):
    if self.NumImage == 3:
      return 2; # get to maximum
    print(str(self.NumImage))
    self.Image['Image' + str(self.NumImage)] = image.copy()
    self.NumImage = self.NumImage + 1
    if self.NumImage == 1:
      return 0;
    if self.NumImage > 1 and self.NumImage < 4:
      return 1;  
    
  def print_all_images(self):
    if self.NumImage == 0:
      print ("No Image is readed")
      return 
    for i in range(self.NumImage):
      plt.imshow(self.Image['Image' + str(i)])
      plt.show()
    
class MyClient(ImageSelectRequestStruct):
  def __init__(self, ownerID):
    self.image_select_request = ImageSelectRequestStruct(ownerID)
    self.ownerID = ownerID
    
  def ReadOneImage(self,path):
    xx = Image.open(path)
    status = self.image_select_request._add_one_image(xx)
    return status
    # TODO error handle
    
  def print_images(self):
    self.image_select_request.print_all_images()
    
    
  def conn_to_server(self, http_server="172.20.10.8:8082"):
    self.conn = http.client.HTTPConnection(http_server)

  def disconn_to_server(self):
    self.conn.close()

  def PostImagetoServer(self):
    if self.image_select_request.NumImage == 0:
      print("NO Image to post")
      return 
    
    each_image_size=[]
    for i in range(self.image_select_request.NumImage):
      # convert to byte format
      imgByteArr = io.BytesIO()
      self.image_select_request.Image['Image'+str(i)].save(imgByteArr, format='JPEG')
      imgByteArr = imgByteArr.getvalue()
      
      each_image_size.append(len(imgByteArr))
      # concatenate
      if i==0:
        imgByteAll = imgByteArr
      else:
        imgByteAll = imgByteAll + imgByteArr
  
    key =uuid.uuid1()
    key_str=str(key)
    text_file = open("event_key_"+self.ownerID+".txt", "a")
    text_file.write(key_str+'\n')
    text_file.close()
    headers = {"content_length" : len(imgByteAll),
               "num_images": len(each_image_size),
               "each_size": str(each_image_size)[1:-1],
               "type": "image/jpeg",
               "owner_ID":self.ownerID,
               "mode": "send_image_for_selection",
               "event_key": key_str,
              }
    print(type(imgByteAll))
    self.conn.request("POST", "", imgByteAll, headers)

  def PostSelectiontoServer(self, user_name="ybc",event_key="bb35fb80-6286-11e6-8b7a-985aeb8f7138",choice_number=1):
    '''
      make event_key, user_name to be automatic
    '''
    headers = {"user_name": user_name,
               "event_key": event_key,
               "choice_num": choice_number,
               "mode": "send_selection",
              }
    self.conn.request("POST","","", headers)
    
  # def fetch_image(self):

  def _fetch_image(self, user_name, event_key):
    '''
      make event_key, user_name to be automatic
    '''
    headers = {"user_name": user_name,
               "event_key": event_key, # todo: changing this into better format
               "mode": "fetch_selection",
              }
    self.conn.request("GET","","", headers)
    rsp = self.conn.getresponse()
    data_received = rsp.read()
    print(len(data_received))
    print(type(data_received)
    stringdata=str(data_received,'latin-1')
    #print(stringdata)
    recover = json.loads(stringdata)
    #PrintData([recover])
    return recover
  
  def _checkifokay(self, user_name, event_key):
    '''
      make event_key, user_name to be automatic
    '''
    headers = {"user_name": user_name,
               "event_key": event_key, # todo: changing this into better format
               "mode": "check_ready",
              }
    self.conn.request("GET","","", headers)
    rsp = self.conn.getresponse()
    is_ready=rsp.getheader('is_ready')
    is_exist=rsp.getheader('is_exist')
    return is_ready!='0', is_exist!='0'

  
  def FetchSelfImage(self):
    '''
      make event_key, user_name to be automatic
    '''
    text_file = open("event_key_"+self.ownerID+".txt", "r")
    x=text_file.read()
    xx = x.split("\n")
    is_ready,is_exist=self._checkifokay(self.ownerID, xx[-2])
    print ("type of is_exist:", type(is_exist))
    print ("type of is_ready:", type(is_ready))
    if not is_exist:
      print("Error wrong event_key or user_name")
      return 
    recover = self._fetch_image(self.ownerID,xx[-2])
    #################################################
#     connection = pymysql.connect(host='localhost',
#                              user='xqs',
#                              password='password',
#                              cursorclass=pymysql.cursors.DictCursor,
#                              db = 'StormBorn')

#     cursor = connection.cursor()
#     sql = "SELECT * FROM `ImageTable_New` where user_name=%s AND event_key=%s"
#     print (sql)
#     cursor.execute( sql,(self.ownerID, xx[-2]))
#     recover = cursor.fetchall()
#     recover = recover[0]
    #################################################
    PrintData([recover])
    if is_ready:
      recover = self._fetch_image(self.ownerID,xx[-2])
      PrintData([recover])
    else:
      print("Not Ready Yet")

    
  def FetchNonSelfImage(self):
    '''
      Get randome image assigned by server
    '''
    headers = {"user_name": self.ownerID,
               "mode": "fetch_non_self_image",
              }
    self.conn.request("GET","","", headers)
    rsp = self.conn.getresponse()
    uuid=rsp.getheader('random_uuid')
    name=rsp.getheader('random_name')
    print("uuid ",uuid)
    print("name ",name)
    recover=self._fetch_image(name,uuid)
    PrintData([recover])
    return uuid,name
    


# In[187]:

from matplotlib import gridspec
def PrintData(fetch_data, num_image=3):
  for j in range(len(fetch_data)):
    data=fetch_data[j]
    print("user name: ", data['user_name'], "\tEvent Key:", data['event_key'])
    
    gs = gridspec.GridSpec(1, num_image, width_ratios=np.ones(num_image), height_ratios=[1])
    
    for i in range(num_image):
      if data['images'+str(i+1)] == None:
        continue;
      post_data_bin = np.fromstring(data['images'+str(i+1)], dtype=np.uint8)
      print("post_data_bin: ", post_data_bin)
      print(len(post_data_bin))
      post_image = Image.open(io.BytesIO(post_data_bin))
      plt.subplot(gs[i])
      plt.imshow(post_image)
      plt.axis("off")
    plt.show()
    
    print("select Num:", end="\t" )
    
    for i in range(3):
      print(data['select_number'+str(i+1)], end="\t")
    print ('\n')


# In[188]:

def TestFetchSelfImage():
  username_list=["reallygood","phoebe2","foo","phoebe"]
  for i in range (4):
    c1 = MyClient(username_list[i])
    c1.conn_to_server(http_server="172.20.10.8:8082")
    c1.FetchSelfImage()
    c1.disconn_to_server()
    c1.conn_to_server(http_server="172.20.10.8:8082")
TestFetchSelfImage()



# In[190]:

def TestFetchNonSelfPostSelectiontoServer():
  username_list=["reallygood","phoebe2","foo","phoebe"]
  for i in range (4):
    c1 = MyClient(username_list[i])
    c1.conn_to_server(http_server="172.20.10.8:8082")
    event_key,user_name = c1.FetchNonSelfImage()
    c1.disconn_to_server()
    c1.conn_to_server(http_server="172.20.10.8:8082")
    c1.PostSelectiontoServer(user_name,event_key)
    c1.disconn_to_server()
TestFetchNonSelfPostSelectiontoServer()


# In[179]:

def TestPostImage():
  username_list=["reallygood","phoebe2","foo","phoebe"]
  password_list=["1234","okay","psps","cool"]
  status_history = []
  for i in range (4):
    status, user_name=CreateUser(http_server="172.20.10.8:8082", user_name=username_list[i], pass_word=password_list[i])
    c1 = MyClient(user_name)
    print (c1.image_select_request.ownerID)
    ## read three image
    c1.ReadOneImage("/Users/phoebesu/Desktop/jupitar/images5.jpeg")
    c1.ReadOneImage("/Users/phoebesu/Desktop/jupitar/images4.jpeg")
    c1.ReadOneImage("/Users/phoebesu/Desktop/jupitar/images3.jpeg")
    c1.conn_to_server(http_server="172.20.10.8:8082")
    c1.PostImagetoServer()
    c1.disconn_to_server()
TestPostImage()


# In[50]:

def TestCreateUser():
  username_list=["ybc1","phoebe2","foo","phoebe"]
  password_list=["1234","okay","psps","cool"]
  status_history = []
  for i in range (4):
    status, user_name=CreateUser(http_server="172.20.10.8:8082", user_name=username_list[i], pass_word=password_list[i])
    status_history.append(status)
  print (status_history)
TestCreateUser()


# In[53]:

def run():
  username_list=["ybc","phoebe","foo"]
  password_list=["1234","okay","psps"]
  for i in range (3):
    status, user_name=CreateUser(http_server="172.20.10.8:8082", user_name=username_list[i], pass_word=password_list[i])
    if status:
      c1 = MyClient(user_name)
      print (c1.image_select_request.ownerID)
      ## read three image
      c1.ReadOneImage("/Users/phoebesu/Desktop/jupitar/images5.jpeg")
      c1.ReadOneImage("/Users/phoebesu/Desktop/jupitar/images4.jpeg")
      c1.ReadOneImage("/Users/phoebesu/Desktop/jupitar/images3.jpeg")

      # c1.print_images()
      # TODO check connect whether successful
      c1.conn_to_server(http_server="172.20.10.8:8082")
      # c1.conn_to_server(http_server="10.0.0.5:8082")
      c1.PostImagetoServer()
      c1.disconn_to_server()
      c1.conn_to_server(http_server="172.20.10.8:8082")

  #     c1.PostSelectiontoServer()
  #     # TODO possibly may cause problem (disconnet reconnect)
  #     c1.disconn_to_server()
  #     c1.conn_to_server(http_server="172.20.10.8:8082")

  #     c1.FetchSelfImage()
  #     c1.disconn_to_server()
  #     c1.conn_to_server(http_server="172.20.10.8:8082")

      c1.FetchNonSelfImage()

      c1.disconn_to_server()
      print('done: ',i)
      #return data
run()


# In[6]:

import json
import base64


# In[52]:

print(data)


# In[81]:

#print(data)
stringdata=str(data,'latin-1')
#stringdata="sss"
#stringdata=data.decode("utf-8") 
print(stringdata)


# In[83]:

recover = json.loads(stringdata)


# In[84]:

print(type(recover))


# In[85]:

print(recover['images1'].encode("latin-1"))


# In[86]:

xx = np.fromstring(recover['images1'].encode("latin-1"), dtype = np.uint8)
post_image = Image.open(io.BytesIO(xx))
plt.imshow(post_image)
plt.plot()


# In[87]:

PrintData([recover])


# In[46]:

x=uuid.uuid1()
print(x)
print(type(x))
y=str(x)
print(y)
print(type(y))


# In[ ]:



