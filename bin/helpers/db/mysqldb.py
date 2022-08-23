import json
import os
from flask_mysqldb import MySQL
from dotenv import load_dotenv
load_dotenv('.env')

class MYSQLDB :
    def __init__(self, app) :
        app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST')
        app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER')
        app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD')
        app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB')
        self.mysql = MySQL(app)

    def query(self, raw_query) :
        cur = self.mysql.connection.cursor() 
        cur.execute(raw_query) 
        row_headers=[x[0] for x in cur.description]
        rv = cur.fetchall()
        json_data = []
        for result in rv:
            json_data.append(dict(zip(row_headers, result)))       
        cur.close()
        return json_data

    def command(self, raw_query) :
        cur = self.mysql.connection.cursor() 
        cur.execute(raw_query)
        self.mysql.connection.commit()
        rv = cur.fetchall()
        cur.close()
        return str(rv)