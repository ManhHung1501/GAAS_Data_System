import sys
sys.path.insert(0, '/home/data-engineer/GAAS_Data_System')
import logging
import mysql
from datetime import datetime, timedelta, date
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from ETL.verify_func import update_partition_table


# Define default arguments for the DAG
default_args = {
    'owner': 'hungnm',
    'email': ['hungnm15012002@gmail.com',],
    'depends_on_past': False,
    'start_date': datetime(2023, 11, 22, 23, 0, 0),  # Define the appropriate start date
    'retries': 0,
    'email_on_failure': True,
    'email_on_retry': False,
    'catchup': False,  # Set to False to prevent backfilling for past dates
}


# Create the DAG
dag = DAG(
    'gaas_update_partition_tbl',
    description='An ETL Backup to update partition table',
    default_args=default_args, 
    schedule_interval=timedelta(days=1)
)

update_partition_table_task = PythonOperator(
    task_id='run_backup_etl',
    python_callable= update_partition_table,
    provide_context=True,
    dag=dag
)

# Set task dependencies
update_partition_table_task



    