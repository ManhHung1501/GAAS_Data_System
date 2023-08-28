import sys
sys.path.insert(0, '/home/data-engineer/GAAS_Data_System/ETL')
import messages
import pandas as pd
import json
import numpy as np
from datetime import datetime, timedelta
from verify_func import get_partition_table

# UDF function
def list_to_json(lst):
    if lst is None:
        return None
    return json.dumps({index + 1: value for index, value in enumerate(lst)})

def to_datetime(row):
    row['ts'] = pd.to_datetime(row['ts'], unit='ms')
    row['tu'] = pd.to_datetime(row['tu'], unit='ms', errors='coerce')
    row['t'] = pd.to_datetime(row['t'], unit='ms', errors='coerce')
    if pd.isna(row['tu']):  # Check if 'tu' is NaT
        row['tu'] = row['t']
    return row['ts'], row['tu'], row['t']

def modify_keys(v_dict):
    if "xsu" in v_dict:
        v_dict["ssr"] = v_dict.pop("xsu")  # Rename 'xsu' to 'ssr'
    for key in list(v_dict.keys()):
        if key.startswith("x"):
            v_dict["am"] = v_dict.pop(key)  # Rename keys starting with 'x' to 'am'
    return v_dict

# ------------------ TRANSFORM USER ----------------------
inserted_time = datetime.now() + timedelta(hours=7)
# Transform event
def transform_events(event_df, event_type):
    # Return empty df if have no data to transform
    if len(event_df) == 0:
        return pd.DataFrame([])

    # Category messages to action and transaction
    if event_type == "action":
        value_df = event_df[event_df['m'].isin(messages.action)]
    elif event_type == "transaction":
        value_df = event_df[event_df['m'].isin(messages.transaction)]

        # Rename Unix transaction key
        value_df["v"] = value_df["v"].apply(lambda x: modify_keys(x) if isinstance(x, dict) else x)

        # transform source, amount to columns
        value_df["source"] = value_df["v"].apply(lambda x: x["ssr"] if isinstance(x, dict) and "ssr" in x else None)
        value_df["amount"] = value_df["v"].apply(lambda x: x["am"] if isinstance(x, dict) and "am" in x else 0)

    # Convert event params 
    value_df["binding_token"] = value_df["v"].apply(lambda x: x['bt'] if isinstance(x, dict) and "bt" in x else None)
    value_df["v"] = value_df["v"].apply(lambda x: json.dumps(x) if isinstance(x, dict) else x)
    
    # Convert timestamp to datetime
    time_columns = ['ts', 'tu', 't']
    value_df[time_columns] = value_df[time_columns].apply(lambda x: to_datetime(x), axis=1, result_type='expand')
    value_df['date'] = value_df['ts'].dt.date
    
    # SET PARTITION ID
    partition_df = get_partition_table()

    # Convert date columns to datetime
    partition_df['partition_date'] = pd.to_datetime(partition_df['partition_date'])
    value_df['date'] = pd.to_datetime(value_df['date'])

    # Get min partition date and relative partition id
    min_partition_date = partition_df['partition_date'].min()
    id_min_date = partition_df.loc[partition_df['partition_date'] == min_partition_date]['partition_id'].iloc[0]

    # Merge the value_df with partition_df to get the corresponding partition_id
    value_df = value_df.merge(partition_df, how='left', left_on='date', right_on='partition_date')
    value_df['partition_id'] = value_df['partition_id'].fillna(id_min_date)

    # SELECT COLUMNS TO INSERT
    if event_type == "action":
        value_df = value_df[['_id', 'partition_id', 'u', 'binding_token', 'm', 'date',
                            't', 'tu', 'ts', 'v', 'cs', 'ss', 'cv', 'c', 'rb']]
    elif event_type == "transaction":
        value_df = value_df[['_id', 'partition_id', 'u', 'binding_token', 'source','m', 'date',
                            'amount', 't', 'tu', 'ts', 'v', 'cs', 'ss', 'cv', 'c', 'rb']]

    value_df = value_df.replace({np.nan: None})

    return value_df


# --------------- TRANSFORM USER ----------------------
def transform_users(user_df, resource_df):
    # Merge user with resource
    df = user_df.merge(resource_df, how='left', left_on='u', right_on='user_id')

    df['clt'] = df['clt'].apply(lambda x: 'yes' if x==1 else 'no')

    #transform user last online time   
    df['last_online'] = pd.to_datetime(df['last_online'],unit='ms',errors='coerce')
    
    #transform user creation time
    df['creation_time'] = pd.to_datetime(df['ct'],unit='ms',errors='coerce')
    df['creation_date'] = df['creation_time'].dt.date

    #transform hero level star
    df['hero_level_star'] = df['dd'].apply(lambda x: x['h'] if isinstance(x, dict) and 'h' in x else 0)

    #transform miniboss level star
    df['miniboss_level_star'] = df['dd'].apply(lambda x: x['b'] if isinstance(x, dict) and 'b' in x else 0)
    
    #transform campaign star
    df['campaign_star'] = df['dd'].apply(lambda x: list_to_json(x['c']) if isinstance(x, dict) and 'c' in x else None)

    #transform ship level star to format level: star
    df['ship_level_star'] = df['dd'].apply(lambda x: list_to_json(x['s']) if isinstance(x, dict) and 's' in x else None)
    
    #transform ship skin level star to format level: star
    df['ship_skinlv_star'] = df['dd'].apply(lambda x: list_to_json(x['ss']) if isinstance(x, dict) and 'ss' in x else None)
    
    #transform drone level star to format level: star
    df['drone_level_star'] = df['dd'].apply(lambda x: list_to_json(x['d']) if isinstance(x, dict) and 'd' in x else None)

    # Calculate total star from each source
    df['total_camp_star'] = df['dd'].apply(lambda x: sum(x['c']) if isinstance(x, dict) and 'c' in x else 0)
    df['total_ship_star'] = df['dd'].apply(lambda x: sum(x['s']) if isinstance(x, dict) and 's' in x else 0)
    df['total_skinlv_star'] = df['dd'].apply(lambda x: sum(x['ss']) if isinstance(x, dict) and 'ss' in x else 0)
    df['total_drone_star'] = df['dd'].apply(lambda x: sum(x['d']) if isinstance(x, dict) and 'd' in x else 0)
    
    # Transform user resource
    df['gold'] = df['rs'].apply(lambda x: x['1'] if isinstance(x, dict) and '1' in x else 0)
    df['crystal'] = df['rs'].apply(lambda x: x['2'] if isinstance(x, dict) and '2' in x else 0)  
    df['piece'] = df['rs'].apply(lambda x: x['23'] if isinstance(x, dict) and '23' in x else 0)
    df['vip_point'] = df['rs'].apply(lambda x: x['285'] if isinstance(x, dict) and '285' in x else 0)
    df['resource'] = df['rs'].apply(lambda x: json.dumps(x) if isinstance(x, dict) else None)
    
    # Get inserted time
    df['inserted_time'] = inserted_time 

    df = df.replace({np.nan: None})

    df = df[[
        'u',
        'ci', 
        'c', 
        'dt',
        'last_online',
        'gold', 
        'crystal',
        'piece',
        'vip_point',
        'resource',
        'd',
        'total_camp_star',
        'total_ship_star',
        'total_skinlv_star',
        'total_drone_star',
        'hero_level_star',
        'miniboss_level_star',
        'campaign_star',
        'ship_skinlv_star',
        'drone_level_star',
        'ship_level_star',
        'clt',
        'creation_time',
        'creation_date',
        'av',
        'cv',
        'inserted_time']]
    return df

def transform_items(user_df, item_lst):
    if item_lst == "sl":
        sl = user_df.explode("sl")
        sl["ship_index"] = sl.groupby("u").cumcount() + 1
        sl["skin_list"] = sl['sl'].apply(lambda x: list_to_json(x['ss']) if isinstance(x, dict) and 'ss' in x else 0)
        sl['bullet_level'] = sl['sl'].apply(lambda x: x['sb'] if isinstance(x, dict) and 'sb' in x else 0)
        sl['power_level'] = sl['sl'].apply(lambda x: x['sp'] if isinstance(x, dict) and 'sp' in x else 0)
        sl['evolve_level'] = sl['sl'].apply(lambda x: x['se'] if isinstance(x, dict) and 'se' in x else 0)
        sl['experience_point'] = sl['sl'].apply(lambda x: x['xp'] if isinstance(x, dict) and 'xp' in x else 0)
        # Get inserted time
        sl['inserted_time'] = inserted_time 
        sl = sl[['u','ship_index','bullet_level','power_level','evolve_level','experience_point','skin_list', 'inserted_time']]
        df = sl

    elif item_lst == "dl":
        dl = user_df.explode("dl")
        dl["drone_index"] = dl.groupby("u").cumcount() + 1
        dl["skin_list"] = dl['dl'].apply(lambda x: list_to_json(x['ss']) if isinstance(x, dict) and 'ss' in x else 0)
        dl['power_level'] = dl['dl'].apply(lambda x: x['sp'] if isinstance(x, dict) and 'sp' in x else 0)
        # Get inserted time
        dl['inserted_time'] = inserted_time 
        dl = dl[['u','drone_index','power_level','skin_list', 'inserted_time']]
        df = dl
        
    elif item_lst == "pl":
        pl = user_df.explode("pl")
        pl['pilot_id'] = pl['pl'].apply(lambda x: x['pi'] if isinstance(x, dict) and 'pi' in x else 0)
        pl['pilot_level'] = pl['pl'].apply(lambda x: x['lv'] if isinstance(x, dict) and 'lv' in x else 0)
        # Get inserted time
        pl['inserted_time'] = inserted_time 
        pl = pl[['u','pilot_id','pilot_level', 'inserted_time']]
        df = pl
        
    elif item_lst == "tl":
        tl = user_df.explode("tl")
        tl['talent_id'] = tl['tl'].apply(lambda x: x['ti'] if isinstance(x, dict) and 'ti' in x else 0)
        tl['talent_level'] = tl['tl'].apply(lambda x: x['lv'] if isinstance(x, dict) and 'lv' in x else 0)
        # Get inserted time
        tl['inserted_time'] = inserted_time 
        tl = tl[['u','talent_id','talent_level', 'inserted_time']]
        df = tl
    elif item_lst == "xl":
        xl = user_df.explode("xl")
        xl['expert_item_id'] = xl['xl'].apply(lambda x: x['ei'] if isinstance(x, dict) and 'ei' in x else 0)
        xl['expert_item_level'] = xl['xl'].apply(lambda x: x['lv'] if isinstance(x, dict) and 'lv' in x else 0)
        xl['equipping_ship'] = xl['xl'].apply(lambda x: x['sh'] if isinstance(x, dict) and 'sh' in x else 0)
        xl['slot_equipped'] = xl['xl'].apply(lambda x: x['su'] if isinstance(x, dict) and 'su' in x else 0)
        # Get inserted time
        xl['inserted_time'] = inserted_time
        xl = xl[['u','expert_item_id','expert_item_level','equipping_ship','slot_equipped', 'inserted_time']]
        df = xl
    else:
        raise ValueError("Invalid item_lst value.")
    
    return df


