import sys
sys.path.insert(0, '/home/data-engineer/GAAS_Data_System')
from datetime import date, datetime, timedelta
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
    try:
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
    except Exception as e:
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
        
def update_partition_table():
    cursor = connection.cursor()
    partition_df = get_partition_table()

    # Convert date columns to datetime
    partition_df['partition_date'] = pd.to_datetime(partition_df['partition_date'])

    # Get min partition date and relative partition id
    min_partition_date = partition_df['partition_date'].min()
    id_min_date = partition_df.loc[partition_df['partition_date'] == min_partition_date]['partition_id'].iloc[0]

    max_partition_date = partition_df['partition_date'].max()
    partition_update_date = (max_partition_date + timedelta(days=1)).date()
    
    # update partition date
    update_query = """
            UPDATE partition_df
            SET partition_date = %s
            WHERE partition_date = %s
        """
    cursor.execute(update_query, (partition_update_date, min_partition_date) )

    # Delete data of min date partition
    delete_query = """
            DELETE FROM actions
            WHERE partition_id = %s;
            DELETE FROM transactions
            WHERE partition_id = %s;
    """
    cursor.execute(delete_query, (id_min_date, id_min_date) )

    connection.commit()