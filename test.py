from datetime import datetime, timedelta
import pandas as pd  
from ETL.verify_func import update_partition_table, get_partition_table
date_string = "2023-08-25"
date_format = "%Y-%m-%d"

# new_min_date = pd.to_datetime("2023-11-22")

partition_df = get_partition_table()

# Convert date columns to datetime
partition_df['partition_date'] = pd.to_datetime(partition_df['partition_date'])


# Get min partition date
min_partition_date = partition_df['partition_date'].max()
id_min_date = partition_df.loc[partition_df['partition_date'] == min_partition_date]['partition_id'].iloc[0]

max_partition_date = partition_df['partition_date'].max()
partition_update_date = (max_partition_date + timedelta(days=1)).date()


print(partition_update_date)