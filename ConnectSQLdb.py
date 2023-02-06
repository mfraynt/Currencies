import mysql.connector
from mysql.connector import errorcode

config = {'user': 'mfraynt',
          'password': '18989828',
          'host': '127.0.0.1',
          'database': 'db',
          'raise_on_warnings': True,
          'use_pure': False}

cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()


def record(SQLscript, data):
    try:
        cursor.execute(SQLscript, data)
    except mysql.connector.Error as err:
        if err.errno == 1062:
            print('DUPLICATE VALUE ' + data[0].strftime('%d %b %Y'))
