from credential import connection
import pandas as pd

def create_partition_table_mysql():
    start_date = pd.to_datetime("2023-08-26")
    cursor = connection.cursor()
    partition_dates = pd.date_range(start_date, periods=90)
    
    # Create the partition table
    create_table_query = """
        CREATE TABLE partition_df (
            partition_id INT PRIMARY KEY,
            partition_date DATE
        )
            """
    cursor.execute(create_table_query)

    # Insert data to partition table
    insert_query = """
            INSERT INTO partition_df (partition_id, partition_date)
            VALUES (%s, %s)
        """

    partition_id = 0
    for date in partition_dates:
        partition_id += 1
        cursor.execute(insert_query, (partition_id,date))

    
    cursor
    connection.commit()
    print("Partition table created successfully.")
    connection.close()

create_partition_table_mysql()
