from datetime import datetime
import pandas as pd  
from ETL.verify_func import update_partition_table, get_partition_table
date_string = "2023-08-25"
date_format = "%Y-%m-%d"

# new_min_date = pd.to_datetime("2023-11-22")

# update_partition_table(new_min_date)

print(datetime.now())