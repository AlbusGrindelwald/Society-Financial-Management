import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='sai2005',  # your password here
        database='society_db'
    )
