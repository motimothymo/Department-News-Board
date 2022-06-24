from nameko.exceptions import DependencyProvider

import mysql.connector
from mysql.connector import Error
import mysql.connector.pooling

class DatabaseWrapper:
    connection = None
    
    def __init__(self,connection):
        self.connection = connection
        
    def get_user(self,username):
        cursor = self.connection.cursor(dictionary=True)
        result = []
        sql = f"SELECT * FROM users WHERE username = '{username}'"
        cursor.execute(sql)
        result = cursor.fetchone()
        cursor.close()
        return result
    
    def create_user(self, username, password):
        cursor = self.connection.cursor(dictionary=True)
        sql = f"INSERT INTO users (username, password) VALUES ('{username}', '{password}')"
        cursor.execute(sql)
        self.connection.commit()
        cursor.close()
        

class DatabaseProvider(DependencyProvider):
    connection_pool = None
    
    def setup(self):
        try:
            self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="user_pool",
                pool_size=32,
                pool_reset_session=True,
                host='127.0.0.1',
                database='news_readers',
                user='root',
                password=''
            )
        except Error as e:
            print("Error while connecting to MySQL using Connection pool ", e)

    def get_dependency(self, worker_ctx):
        return DatabaseWrapper(self.connection_pool.get_connection())