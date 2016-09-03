class ImageDao(object):
  '''"172.20.10.7"'''
  def __init__(self, host='localhost', user='root', password='', db='Jupiter'):
    self.host = host
    self.user = user
    self.password = password
    self.db = db
    self.connectToDB()
  
  def connectToDB(self):
    self.connection = pymysql.connect(host=self.host, user=self.user, password=self.password, db=self.db)
    # Setting cursors and defining type of returns we need from Database,
    # here it's gonna be returning as dictionary data
    self.cursor = self.connection.cursor(cursors.DictCursor);
    
  def InsertImages(self, image_array, user_name, uuid_string):
    '''
       image_array is a array of binary data
    '''
    num_image = len(image_array)

    if (num_image > 3):
      return
    
    # generating the query command
    query_cmd='INSERT INTO ImageTable (user_name,'
    for i in range(num_image):
      query_cmd = query_cmd + 'images' + str(i+1) + ','
    
    for i in range(num_image):
      query_cmd = query_cmd + 'select_number' + str(i+1) + ','
      
    query_cmd = query_cmd[0:-1] + ',event_key) VALUES (%s,'
    
    for i in range(num_image):
      query_cmd = query_cmd + '%s,'
    for i in range(num_image):
      query_cmd = query_cmd + '%s,'
    query_cmd = query_cmd + '%s'
    query_cmd = query_cmd + ')'
    
    query_data = image_array
    query_data.insert(0,user_name)
    
    for i in range(num_image):
      query_data.append(0)
    query_data.append(uuid_string)
    self.cursor.execute(query_cmd, tuple(query_data) )
    
  def UpdateChoices(self, user_name, event_key, choice_num):
    '''
      store selected image result
    '''
    query_cmd = 'UPDATE ImageTable SET select_number' + str(choice_num)
    query_cmd = query_cmd + '=select_number' + str(choice_num)+'+1, ' # select one +1
    query_cmd = query_cmd + 'total_number=total_number+1 '    #total + 1
    query_cmd = query_cmd + 'where user_name=%s and event_key=%s'

    self.cursor.execute(query_cmd, (user_name, event_key) )  
  
  def SelectImages(self, user_name, event_key):
    '''
      fetch self image
    '''
    query_cmd = 'SELECT * FROM ImageTable WHERE user_name=%s AND event_key=%s'
    self.cursor.execute(query_cmd, (user_name, event_key) ) 
    data = self.cursor.fetchall()
    if len(data)!=1:
      return json.dumps("", encoding='latin-1')
    data = data[0];
    data_string=json.dumps(data, encoding='latin-1')
    return data_string
  
  def CheckReady(self, user_name, event_key):
    query_cmd = 'SELECT Read FROM ImageTable WHERE user_name=%s AND event_key=%s'
    self.cursor.execute(query_cmd, (user_name, event_key) ) 
    data = self.cursor.fetchall()
    return data

  def getRandomEventUUID(self, user_name):
    query_cmd = 'SELECT event_key FROM ImageTable WHERE user_name=%s'
    self.cursor.execute(query_cmd, user_name)
    
    keyDict = self.cursor.fetchall()
    keyList = [k['event_key'] for k in keyDict] 
    random_key = random.choice(keyList)
    
    return random_key