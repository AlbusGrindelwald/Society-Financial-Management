import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host='bdthbxisi1zcaul2cibq-mysql.services.clever-cloud.com',
        user='umj1xkpz0tv3emmq',
        password='ZxVRbzEMzceJfA4G9vYF',  # your password here
        database='bdthbxisi1zcaul2cibq',
        port=3306
    )
