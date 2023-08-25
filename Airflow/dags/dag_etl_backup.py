import sys
sys.path.insert(0, '/home/data-engineer/GAAS_Data_System')
import logging
import mysql
from datetime import datetime, timedelta, date
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from ETL.extract import extract
from ETL.transform import transform_events, transform_items, transform_users
from ETL.verify_func import get_last_processed_timestamp, update_last_processed_timestamp, cache_process
from ETL.load import load

def etl_user_items(greater, less):
    start = datetime.now()

    logging.info('Extracting user...')
    user_df = extract("user",greater,less)
    user_ex_time = datetime.now() 
    logging.info(f'Complete extract user: {user_ex_time - start}')

    logging.info('Extracting resource...')
    resource_df = extract("rs",greater,less)
    rs_ex_time = datetime.now() 
    logging.info(f'Complete extract resource: {rs_ex_time - user_ex_time}')

    logging.info('Transforming user...')
    user = transform_users(user_df,resource_df)
    user_trs_time = datetime.now() 
    user_trs_time - rs_ex_time
    logging.info(f'Complete transform user: {user_trs_time - rs_ex_time}')


    logging.info('transform space_ships...')
    sl = transform_items(user_df,'sl')
    sl_trs_time = datetime.now() 
    logging.info(f'Complete transform space_ships: {sl_trs_time - user_trs_time}')


    logging.info('transform drones...')
    dl = transform_items(user_df,'dl')
    dl_trs_time = datetime.now() 
    logging.info(f'Complete transform drones: {dl_trs_time - sl_trs_time}')

    logging.info('transform pilots...')
    pl = transform_items(user_df,'pl')
    pl_trs_time = datetime.now() 
    logging.info(f'Complete transform pilots: {pl_trs_time - dl_trs_time}')

    logging.info('transform talents...')
    tl = transform_items(user_df,'tl')
    tl_trs_time = datetime.now() 
    logging.info(f'Complete transform talents: {tl_trs_time - pl_trs_time}')

    logging.info('transform expert_items...')
    xl = transform_items(user_df,'xl')
    xl_trs_time = datetime.now() 
    logging.info(f'Complete transform expert_items: {xl_trs_time - tl_trs_time}')

    logging.info('Loading user...')
    load(user,'users',2500)
    user_load_time = datetime.now() 
    logging.info(f'Complete load user: {user_load_time - xl_trs_time}')

    logging.info('Loading space_ships...')
    load(sl,'space_ships',2500)
    sl_load_time = datetime.now() 
    logging.info(f'Complete load space_ships: {sl_load_time - user_load_time}')

    logging.info('Loading drones...')
    load(dl,'drones',2500)
    dl_load_time = datetime.now() 
    logging.info(f'Complete load drones: {dl_load_time - sl_load_time}')

    logging.info('Loading pilots...')
    load(pl,'pilots',2500)
    pl_load_time = datetime.now() 
    logging.info(f'Complete load drones: {pl_load_time - dl_load_time}')

    logging.info('Loading talents...')
    load(tl,'talents',2500)
    tl_load_time = datetime.now() 
    logging.info(f'Complete load drones: {tl_load_time - pl_load_time}')

    logging.info('Loading expert_items...')
    load(xl,'expert_items',2500)
    xl_load_time = datetime.now() 
    logging.info(f'Complete load drones: {xl_load_time - tl_load_time}')

    logging.info(f'Complete ETL Users in : {datetime.now() - start}')

def etl_event(greater,less):
    start = datetime.now()

    logging.info('Extracting event...')
    event_data = extract("log", greater,less)
    event_extract_time = datetime.now() 
    logging.info(f'Complete extract event: {event_extract_time - start}')
    
    logging.info('Transforming action...')
    df_action = transform_events(event_data,'action')
    action_trs_time = datetime.now() 
    logging.info(f'Complete transform action: {action_trs_time - event_extract_time}')

    logging.info('Transforming transaction...')
    df_transaction = transform_events(event_data,'transaction')
    transaction_trs_time = datetime.now() 
    logging.info(f'Complete transform transaction: {transaction_trs_time - action_trs_time}')

    logging.info('Loading action...')
    load(df_action, "actions", 2500)
    action_load_time = datetime.now() 
    logging.info(f'Complete load action: {action_load_time - transaction_trs_time}')

    logging.info('Loading transaction...')
    load(df_transaction, "transactions", 2500)
    transaction_load_time = datetime.now() 
    logging.info(f'Complete load transaction: {transaction_load_time - action_load_time}')

    logging.info(f'Complete ETL Users in : {datetime.now() - start}')

def run_backup_etl():
    today = date.today()
    previous_day = today - timedelta(days=1)
    csv_file_path = '/home/data-engineer/GAAS_Data_System/ETL/cache_process/{}'.format(previous_day.strftime('%Y%m%d')) 
    print(csv_file_path)
    try: 
        df = pd.read_csv(csv_file_path)
        for index in range(0,len(df)):
            greater = int(df['greater'][index])
            less = int(df['less'][index])
            if df['status'][index] != 'success':
                if df['collection'][index] == 'user':
                    etl_user_items(greater,less)
                    df['status'][index] = 'success'
                    df.to_csv(csv_file_path, index=False)
                elif df['collection'][index] == 'event':
                    etl_event(greater,less)
                    df['status'][index] = 'success'
                    df.to_csv(csv_file_path, index=False)
    except Exception as e:
        logging.error(f"An Error Occur {e}")


# _____________________________DAG_______________________________

# Define default arguments for the DAG
default_args = {
    'owner': 'hungnm',
    'email': ['hungnm15012002@gmail.com'],
    'depends_on_past': False,
    'start_date': datetime(2023, 8, 26, 2, 0, 0),  # Define the appropriate start date
    'retries': 0,
    'email_on_failure': True,
    'email_on_retry': False,
    'catchup': False,  # Set to False to prevent backfilling for past dates
}


# Create the DAG
dag = DAG(
    'gaas_etl_backup',
    description='An ETL Backup to retry failed process in previous day',
    default_args=default_args, 
    schedule_interval=timedelta(days=1)
)

run_backup_etl_task = PythonOperator(
    task_id='run_backup_etl',
    python_callable= run_backup_etl,
    provide_context=True,
    dag=dag
)

# Set task dependencies
run_backup_etl_task