import os
from PIL import Image

def store_image_local(data_, name, path='./images' ):
  name = name + '.jpeg'
  post_data_bin = np.fromstring(data_, dtype=np.uint8)
  # print("post_data_bin: ", post_data_bin)
  # print(len(post_data_bin))
  post_image = Image.open(io.BytesIO(post_data_bin))
  post_image.save(os.path.join(path,name), format='JPEG')    

      
      
# This class will handles any incoming request from
# the browser 
class myHandler(BaseHTTPRequestHandler):
  
  mdb = None # MySqlDatabase
  
  # Handler for the GET requests
  def do_GET(self):
    mode = self.headers['mode']
    if mode == 'fetch_selection':
      user_name = self.headers['user_name']
      event_key = self.headers['event_key']
      data = self.mdb.FetchImage(user_name, event_key)
      self.send_response(200)
      self.send_header('Content-type','text/html')
      self.end_headers()
      self.wfile.write(data)
      
    elif mode == 'fetch_non_self_image':
      user_name = self.headers['owner_ID']
      random_name = self.mdb.GetRandomName(user_name)
      random_uuid = self.mdb.GetRandomEventUUID(random_name)
      self.send_response(200)
      self.send_header('Content-type','text')
      self.send_header('random_name',random_name)
      self.send_header('random_uuid',random_uuid)
      self.end_headers()
      data = self.mdb.GetTableInfo(random_name, random_uuid)
      self.wfile.write(data)
      
    elif mode == 'check_ready':
      user_name = self.headers['user_name']
      event_key = self.headers['event_key']
      is_ready, is_exist = self.mdb.CheckReady(user_name, event_key)
      self.send_response(200)
      self.send_header('is_ready', is_ready)
      self.send_header('is_exist', is_exist)
      self.end_headers()
      
    elif mode == 'fetch_one_image':
      path = self.headers['path']
      try:
        tmp_image = Image.open(path)
      except:
        print ('wrong when open the image')
        self.send_response(404)
        self.send_header('status', 'Not Found Image')
        
      imgByteArr = io.BytesIO()
      tmp_image.save(imgByteArr, format='JPEG')
      data = {}
      data['image'] = imgByteArr.getvalue()
      # print len(data['image'])
      data_string=json.dumps(data, encoding='latin-1')
      self.send_response(200)
      self.send_header('status', 'Found Image')
      self.end_headers()
      self.wfile.write(data_string)
      
    
    return
  
  def do_POST(self):
    mode = self.headers['mode']
    if mode == 'send_image_for_selection':
      num_image = int(self.headers['num_images'])
      each_size_str = self.headers['each_size']
      owner_ID = self.headers['owner_ID']
      uuid_string = self.headers['event_key']
      image_array = []
      for i in range(num_image):
        length = int(each_size_str.split(',')[i])
        name = 'Image'+str(i)
        try:
          print ('the sender length: %d' % length)
          ####test###############
#           post_data = self.rfile.read()
#           print ('the length get: %d' % len(post_data))
          #####test
          post_data = self.rfile.read(length)
          
          print('pass the read')
          store_image_local(post_data, name=uuid_string+str(i))
          image_array.append(post_data)
        except:
          print ('length error')
        
      self.mdb.StoreImages(image_array, owner_ID, uuid_string)
      self.send_response(200)
      self.send_header('status', 'Image Post Done')
      
    elif mode == 'send_selection':
      user_name = self.headers['user_name']
      event_key = self.headers['event_key']
      self_name = self.headers['self_name']
      
      choice_num = self.headers['choice_num']
      with open('voter_record.pickle', 'rb') as f:
        x_ = pickle.load(f)
      if event_key in x_:
        if self_name in x_[event_key]:
          #already vote:
          self.send_response(200)
          self.send_header('status', 'Already Voted')
          return
        else:
          x_[event_key].append(self_name)
      else:
        x_[event_key] = [self_name]
        
      with open('voter_record.pickle', 'wb') as f:
        pickle.dump(x_, f, pickle.HIGHEST_PROTOCOL)
      self.mdb.StoreImagesAndChoice(user_name, event_key, choice_num)
      self.send_response(200)
      self.send_header('status', 'Selection Post Done')
          
      
    elif mode == 'create_user':
      user_name = self.headers['user_name']
      password = self.headers['password']
      status = self.mdb.StoreUserInfo(user_name, password)
      self.send_response(200)
      status_string = 'create useer success: %s' % status
      self.send_header('status', status_string)