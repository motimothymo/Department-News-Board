from nameko.exceptions import DependencyProvider
import mysql.connector
from mysql.connector import Error
import mysql.connector.pooling
from requests import delete

class DatabaseWrapper:
    connection = None
    
    def __init__(self,connection):
        self.connection = connection
        
    def add_news(self, news_title, news_content, news_date, news_reporter):
        cursor = self.connection.cursor(dictionary=True)
        sql = f"INSERT INTO news (news_title, news_content, news_date, news_reporter) VALUES ('{news_title}', '{news_content}', '{news_date}', '{news_reporter}')"
        cursor.execute(sql)
        self.connection.commit()
        last_id = cursor.lastrowid
        cursor.close()
        return last_id
        
    def edit_news(self, news_id, news_title, news_content, news_date, news_reporter):
        cursor = self.connection.cursor(dictionary=True)
        sql = f"UPDATE news SET (news_title='{news_title}', news_content='{news_content}', news_date='{news_date}', news_reporter='{news_reporter}) WHERE id = '{news_id}'"
        cursor.execute(sql)
        self.connection.commit()
        cursor.close()
        
    def delete_news(self, news_id):
        cursor = self.connection.cursor(dictionary=True)
        sql = "DELETE FROM room WHERE room_number = '{news_id}'"
        cursor.execute(sql)
        self.connection.commit()
        cursor.close()
        
    def get_news_by_id(self, id):
        cursor = self.connection.cursor(dictionary=True)
        result = []
        sql = f"SELECT * FROM news WHERE id = {id}"
        cursor.execute(sql)
        result = cursor.fetchone()
        cursor.close()
        return result
    
    def get_all_news(self):
        cursor = self.connection.cursor(dictionary=True)
        result = []
        sql = f"SELECT * FROM news"
        cursor.execute(sql)
        result = cursor.fetchone()
        cursor.close()
        return result
    
    def get_news_reporter(self, news_id):
        cursor = self.connection.cursor(dictionary=True)
        result = ""
        sql = f"SELECT news_reporter FROM news WHERE id = {news_id}"
        cursor.execute(sql)
        result = cursor.fetchone()
        cursor.close()
        return result
        

class DatabaseProvider(DependencyProvider):
    connection_pool = None
    
    def setup(self):
        try:
            self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="news_pool",
                pool_size=32,
                pool_reset_session=True,
                host='127.0.0.1',
                database='news',
                user='root',
                password=''
            )
        except Error as e:
            print("Error while connecting to MySQL using Connection pool ", e)

    def get_dependency(self, worker_ctx):
        return DatabaseWrapper(self.connection_pool.get_connection())