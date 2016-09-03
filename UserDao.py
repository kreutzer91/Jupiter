class UserDao(object):
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
    self.cursor = self.connection.cursor(cursors.DictCursor)

  def storeUserInfo(self, user_name, pass_word):
    query_cmd = 'SELECT * FROM UserTable WHERE user_name = %s'
    self.cursor.execute(query_cmd, user_name )
    data = self.cursor.fetchall()
    if len(data) != 0:
      # user_name exist
      return False
    
    query_cmd = 'INSERT INTO UserTable (user_name, pass_word) VALUES (%s, %s)'
    self.cursor.execute(query_cmd, (user_name, pass_word) )
    return True


  def getRandomName(self, user_name):
    query_cmd = 'SELECT user_name FROM UserTable'
    self.cursor.execute(query_cmd)
    
    userDict = self.cursor.fetchall()
    userList = [u['user_name'] for u in userDict ]
    userList.remove(user_name)
    random_name = random.choice(userList)
    
    return random_name