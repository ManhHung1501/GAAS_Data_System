import mysql.connector

# MySQL
mysql_dw = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'abidata999',
    'database': 'GAAS_Data_Warehouse',
    'autocommit': True
}

#connect to sql database
connection = mysql.connector.connect(**mysql_dw)

