#!/usr/bin/python

import pymysql.cursors

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='',
                             cursorclass=pymysql.cursors.DictCursor)

cursor = connection.cursor()

sql = 'CREATE DATABASE IF NOT EXISTS Jupiter'
cursor.execute(sql)
sql = 'USE Jupiter'
cursor.execute(sql)

sql = 'DROP TABLE IF EXISTS ImageTable'
cursor.execute(sql)

sql = '''CREATE TABLE ImageTable (
        `user_name` VARCHAR( 200 ) NOT NULL,
        `event_key` VARCHAR( 200 ) NOT NULL,
        `images1` LONGBLOB,
        `select_number1` INT,
        `images2` LONGBLOB,
        `select_number2` INT,
        `images3` LONGBLOB,
        `select_number3` INT,
        `total_number` INT,
        `ready_status` BOOL,
        PRIMARY KEY ( `user_name`,`event_key` )
       ) ENGINE=MyISAM DEFAULT CHARSET=latin1
       '''
cursor.execute(sql)