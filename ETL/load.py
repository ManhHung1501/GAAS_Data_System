import messages
import pandas as pd
import json
from DB_Config.credential import connection
import load_stmt
import mysql
import sys
import logging
sys.path.insert(0, '/home/data-engineer/GAAS_Data_System/ETL')
from verify_func import cache_process

def load(df, table, batch_size):
    cursor = connection.cursor()

    if table == "actions":
        insert_query = load_stmt.action
    elif table == "transactions":
        insert_query = load_stmt.transaction
    elif table == "users":
        insert_query = load_stmt.user
    elif table == "space_ships":
        insert_query = load_stmt.sl
    elif table == "drones":
        insert_query = load_stmt.dl
    elif table == "pilots":
        insert_query = load_stmt.pl
    elif table == "talents":
        insert_query = load_stmt.tl
    elif table == "expert_items":
        insert_query = load_stmt.xl

    for i in range(0, len(df), batch_size):
        insert_data = df[i:i + batch_size].itertuples(index=False)
        cursor.executemany(insert_query, list(insert_data))
