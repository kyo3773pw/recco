import mysql.connector
from mysql.connector import Error

class Database:
    def __init__(self, host="192.168.0.100", user="root", password="root", database="recco"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def get_connection(self):
        try:
            conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return conn
        except Error as e:
            print(f"Error connecting to MySQL database: {e}")
            return None

    def execute_query(self, query, params=()):
        conn = self.get_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)  # Retorna resultados como diccionarios
                cursor.execute(query, params)
                conn.commit()
                return cursor
            except Error as e:
                print(f"Error executing MySQL query: {e}")
                conn.rollback()  # Hacer rollback en caso de error
                return None
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()

    def fetch_all(self, query, params=()):
        """Método auxiliar para consultas SELECT"""
        conn = self.get_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query, params)
                result = cursor.fetchall()
                return result
            except Error as e:
                print(f"Error fetching data from MySQL: {e}")
                return None
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()

    def fetch_one(self, query, params=()):
        """Método auxiliar para obtener un solo registro"""
        conn = self.get_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query, params)
                result = cursor.fetchone()
                return result
            except Error as e:
                print(f"Error fetching data from MySQL: {e}")
                return None
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()