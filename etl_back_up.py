from ETL.extract import extract
from ETL.transform import transform_events,transform_items,transform_users
from verify_func import get_last_processed_timestamp,update_last_processed_timestamp
from ETL.load import load
from datetime import date, datetime, timedelta
import pandas as pd
import logging

# Set up log file path
log_file_path = "/home/data-engineer/GAAS_Data_System/ETL/log/etl_log_{date}.log".format(date=date.today().strftime('%Y%m%d'))
# Set up logging configuration
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

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

def etl_event(greater,less):
    start_event = datetime.now()

    logging.info('Extracting event...')
    event_data = extract("log", greater,less)
    event_extract_time = datetime.now() 
    logging.info(f'Complete extract event: {event_extract_time - start_event}')
    
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

if __name__ == "__main__":
    today = date.today()
    previous_day = today - timedelta(days=1)
    csv_file_path = '/home/data-engineer/GAAS_Data_System/ETL/cache_process/{}'.format(previous_day.strftime('%Y%m%d')) 
    print(csv_file_path)
    # try: 
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
    # except:
    #    print('No data to back up')