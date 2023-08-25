import sys
sys.path.insert(0, '/home/data-engineer/GAAS_Data_System')
from datetime import date, datetime
import csv
import pandas as pd
from DB_Config.credential import connection

# Last process time
CHECKPOINT_FILE_PATH = "/home/data-engineer/GAAS_Data_System/ETL/checkpoint/checkpoint.txt"
def get_last_processed_timestamp():
    try:
        with open(CHECKPOINT_FILE_PATH, "r") as file:
            last_processed_timestamp = file.read()
            return int(last_processed_timestamp)
    except FileNotFoundError:
        return None
        
def update_last_processed_timestamp(last_processed_timestamp):
    with open(CHECKPOINT_FILE_PATH, "w") as file:
        file.write(str(last_processed_timestamp))

# Cache failed process to run in backup
def cache_process(greater_time, less_than_time, collection):    
    csv_columns = ["greater", "less", "collection", "status"]
    cache_process_path = "/home/data-engineer/GAAS_Data_System/ETL/cache_process/{}".format(date.today().strftime('%Y%m%d'))

    cache_df = pd.read_csv(cache_process_path)
    for i in range(0, len(cache_df)):
        if cache_df["greater"][i] == greater_time and cache_df["collection"][i] == collection:
            return False

    with open(cache_process_path, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        # Check if the file is empty
        is_empty = csvfile.tell() == 0
        if is_empty:
            writer.writeheader()  # Write the header row only if the file is empty
            
        writer.writerow({
            "greater": greater_time,
            "less": less_than_time,
            "collection": collection,
            "status": "pending"
        })

# Partition id
PARTITION_FILE_PATH = "/home/data-engineer/GAAS_Data_System/ETL/checkpoint/current_partition.txt"
date_format = "%Y-%m-%d"
def get_partition_table():
    # Get partition table from mysql
    select_query = """
            SELECT *
            FROM partition_df
        """
    partition_df = pd.read_sql(select_query, con=connection)
    return partition_df
        
def update_partition_table(partition_date):
    cursor = connection.cursor()

    # Get min partition date
    select_query = """
            SELECT MIN(partition_date)
            FROM partition_df
        """
        
    cursor.execute(select_query)
    min_partition_date = cursor.fetchone()[0]

    # update partition date
    update_query = """
            UPDATE partition_df
            SET partition_date = %s
            WHERE partition_date = %s
        """
    cursor.execute(update_query, (partition_date,min_partition_date))
    connection.commit()