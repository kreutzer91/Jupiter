import pymysql.cursors
import numpy as np

connection = pymysql.connect(host='localhost',
                            user='phoebeybc7',
                            password='Yingbich1991',
                            cursorclass=pymysql.cursors.DictCursor)

cursor = connection.cursor()


sql = 'CREATE DATABASE IF NOT EXISTS StormBorn'
cursor.execute(sql)
sql = 'USE StormBorn'
cursor.execute(sql)

sql = 'DROP TABLE IF EXISTS ImageTableWithPath'
cursor.execute(sql)

sql = '''CREATE TABLE ImageTableWithPath (
       `user_name` VARCHAR( 200 ) NOT NULL,
       `event_key` VARCHAR( 200 ) NOT NULL,
       `images1` VARCHAR( 200 ),
       `select_number1` INT,
       `images2` VARCHAR( 200 ),
       `select_number2` INT,
       `images3` VARCHAR( 200 ),
       `select_number3` INT,
       `total_number` INT,
       `ready_status` BOOL,
       PRIMARY KEY ( `user_name`,`event_key` )
      ) ENGINE=MyISAM DEFAULT CHARSET=latin1
      '''
cursor.execute(sql)