import pymysql
from pymysql import connect, err, sys, cursors

class MySqlDatabase(object):
  '''"172.20.10.7"'''
  def __init__(self, host='10.0.0.3', user='xqs', password='password', db='StormBorn'):
    self.host = host
    self.user = user
    self.password = password
    self.db = db
    self.port = 3306
    self.image_table_name = 'ImageTableWithPath'
  
  def connectToDB(self):
#     with SSHTunnelForwarder(
#                (self.host, self.port),
#                ssh_password=self.password,
#                ssh_username=self.user,
#                remote_bind_address=(self.host, self.port)) as server:
    self.connection = pymysql.connect(host=self.host, port=self.port,
                                      user=self.user, password=self.password, db=self.db)
    # Setting cursors and defining type of returns we need from Database,
    # here it's gonna be returning as dictionary data
    self.cursor = self.connection.cursor(cursors.DictCursor);
    
  def GetTableInfo(self, user_name, event_key):
    query_cmd = 'SELECT * FROM %s ' % self.image_table_name
    query_cmd += 'WHERE user_name=%s AND event_key=%s'
    self.cursor.execute(query_cmd, (user_name, event_key) ) 
    data = self.cursor.fetchall()
    return json.dumps(data[0], encoding='latin-1') if len(data)==1 else None
    
  def StoreImages(self, image_array, user_name, uuid_string):
    '''
       image_array is a array of binary data
    '''
    cwd = os.getcwd()
    image_path = os.path.join(cwd, 'images')
    num_image = len(image_array)
    
    # generating the query command
    query_cmd='INSERT INTO %s (user_name,' % self.image_table_name
    for i in range(num_image):
      query_cmd = query_cmd + 'images' + str(i+1) + ','
    
    for i in range(num_image):
      query_cmd = query_cmd + 'select_number' + str(i+1) + ','
      
    query_cmd = query_cmd[0:-1] + ',event_key, ready_status) VALUES (%s,'
    
    for i in range(num_image):
      query_cmd = query_cmd + '%s,'
    for i in range(num_image):
      query_cmd = query_cmd + '%s,'
    # extra two for event_key and ready_status
    query_cmd = query_cmd + '%s,'
    query_cmd = query_cmd + '%s'
    query_cmd = query_cmd + ')'
    
    # print(query_cmd)
    query_data = []
    for i in range(num_image):
      query_data.append(os.path.join(image_path,(uuid_string + str(i)+'.jpeg')))
    query_data.insert(0,user_name)
    
    for i in range(num_image):
      query_data.append(0)
    query_data.append(uuid_string)
    query_data.append(False)
    # print(query_cmd)
    self.cursor.execute(query_cmd, tuple(query_data) )
    
  def StoreImagesAndChoice(self, user_name, event_key, choice_num):
    '''
      store selected image result
    '''
    query_cmd = 'UPDATE %s SET select_number' % self.image_table_name
    query_cmd += str(choice_num) 
    query_cmd = query_cmd + '=select_number' + str(choice_num)+'+1, ' # select one +1
    query_cmd = query_cmd + 'total_number=total_number+1 '    #total + 1
    query_cmd = query_cmd + 'where user_name=%s and event_key=%s'

    self.cursor.execute(query_cmd, (user_name, event_key) )  
  
  def FetchImage(self, user_name, event_key):
    '''
      fetch image
    '''
    query_cmd = 'SELECT * FROM %s ' % self.image_table_name
    query_cmd += 'WHERE user_name=%s AND event_key=%s'
    self.cursor.execute(query_cmd, (user_name, event_key) ) 
    data = self.cursor.fetchall()
    if len(data)!=1:
      print("wrong key to get none data")
      print("event_key: ", event_key)
      print("data: ", data)
      
      return json.dumps("", encoding='latin-1')
    data = data[0]
    for i in range(3):
      if data['images'+str(i+1)] != None:
        path = data['images'+str(i+1)]
        tmp_image = Image.open(path)
        imgByteArr = io.BytesIO()
        tmp_image.save(imgByteArr, format='JPEG')
        data['images'+str(i+1)] = imgByteArr.getvalue()
        
      
    data_string=json.dumps(data, encoding='latin-1')
    #print(data_string)
    return data_string
  
  def CheckReady(self, user_name, event_key):
    query_cmd = 'SELECT ready_status FROM %s ' % self.image_table_name
    query_cmd += 'WHERE user_name=%s AND event_key=%s'
    self.cursor.execute(query_cmd, (user_name, event_key) ) 
    data = self.cursor.fetchall()
    if len(data)!=1:
      print("wrong key to get none data")
      print("event_key: ", event_key)
      print("data: ", data)
      
      return 0, 0
    return data[0]['ready_status'], 1
    
    
  def StoreUserInfo(self, user_name, pass_word):
    query_cmd = 'Select * FROM UserTable  Where user_name = %s'
    self.cursor.execute(query_cmd, user_name )
    data = self.cursor.fetchall()
    if len(data) != 0:
      # user_name exist
      return False
    
    query_cmd = 'Insert INTO UserTable (user_name, pass_word) VALUES (%s, %s)'
    self.cursor.execute(query_cmd, (user_name, pass_word) )
    return True
    
  
  def GetRandomName(self, user_name):
    query_cmd = 'SELECT user_name FROM UserTable'
    self.cursor.execute(query_cmd)
    
    userDict = self.cursor.fetchall()
    userList = [u['user_name'] for u in userDict ]
    #     print("user list:", userList)
    userList.remove(user_name)
    #     print("user list (after remove):",  userList)
    random_name = random.choice(userList)
    #     print("return user name:",  random_name)
    
    return random_name
    
  def GetRandomEventUUID(self, user_name):
    query_cmd = 'SELECT event_key FROM %s' % self.image_table_name
    query_cmd += ' WHERE user_name=%s'
    self.cursor.execute(query_cmd, user_name)
    
    keyDict = self.cursor.fetchall()
    keyList = [k['event_key'] for k in keyDict] 
    #     print("key list:", keyList)
    random_key = random.choice(keyList)
    #     print("return key:",  random_key)
    
    return random_key