from nameko.extensions import DependencyProvider
import mysql.connector
from mysql.connector import Error
import mysql.connector.pooling


class DatabaseWrapper:

    connection = None

    def __init__(self, connection):
        self.connection = connection

    def get_files_by_news_id(self, news_id):
        cursor = self.connection.cursor(dictionary=True)
        sql = f"""SELECT * FROM files WHERE news_id = {news_id}"""
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        return result

    def add_new_file(self, news_id, file_name, file_path):
        cursor = self.connection.cursor(dictionary=True)
        sql = f"""INSERT INTO files (news_id, filename, filepath) VALUES ({news_id}, '{file_name}', '{file_path}')"""
        cursor.execute(sql)
        self.connection.commit()
        cursor.close()

    def delete_all_files_from_news_id(self, news_id):
        cursor = self.connection.cursor(dictionary=True)
        sql = f"DELETE FROM files WHERE news_id = {news_id}"
        cursor.execute(sql)
        self.connection.commit()
        cursor.close()


class DatabaseProvider(DependencyProvider):

    connection_pool = None

    def setup(self):
        try:
            self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="files_pool",
                pool_size=32,
                pool_reset_session=True,
                host='127.0.0.1',
                database='files',
                user='root',
                password=''
            )
        except Error as e:
            print("Error while connecting to MySQL using Connection pool ", e)

    def get_dependency(self, worker_ctx):
        return DatabaseWrapper(self.connection_pool.get_connection())