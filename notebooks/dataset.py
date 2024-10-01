import pandas as pd
from datetime import datetime
import requests

##########################################################################################################
##########################################################################################################

ts_format = '%Y-%m-%d %H:%M:%S'

def timestamp_to_unix(timestamp_str):
    dt = datetime.strptime(timestamp_str, ts_format)
    unix_timestamp = int(dt.timestamp())
    return unix_timestamp

##########################################################################################################
##########################################################################################################

def ts_batches(_from, _end, batch_size):
    total_start = timestamp_to_unix(_from)
    total_end = timestamp_to_unix(_end)
    
    assert total_end > total_start, 'TIMESTAMPS IN WRONG ORDER'
    assert batch_size >= 1, 'BATCH SIZE MUST BE >1'

    move_by = (60*60*24) * batch_size
    temp_start = total_start

    container = []

    while temp_start < total_end:

        temp_end = temp_start+move_by
        if temp_end > total_end: temp_end = total_end

        container.append([temp_start, temp_end])
        
        temp_start = temp_end
    
    return container

##########################################################################################################
##########################################################################################################

def fetch(query):
    response = requests.get(query)
    data = response.json()
    print(f'STATUS: {response.status_code}')
    print(f'NUM_ROWS: {len(data)}')
    return data

##########################################################################################################
##########################################################################################################

def create_dataset(_start: str, _end: str, interval: str, batch_size: int):
    container = pd.DataFrame(columns=['timestamp', 'open', 'close', 'high', 'low', 'volume'])
    container.set_index('timestamp', inplace=True)

    # EXPECTED LENGTH
    expected_length = len(pd.date_range(start=_start, end=_end, freq='min'))
    
    # GENERATE TIMESTAMP BATCHES
    timestamps = ts_batches(_start, _end, batch_size)

    for ts in timestamps:
        start_time, end_time = ts
        
        # FETCH THE NEXT DATA BATCH
        query_string = f'https://eodhd.com/api/intraday/EURUSD.FOREX?api_token={API_TOKEN}&fmt=json&from={start_time}&to={end_time}&interval={interval}'
        data = fetch(query_string)

        # CONVERT TO DATAFRAME
        to_df = pd.DataFrame(data)

        # DROP GARBAGE & RENAME COLS
        to_df.drop('gmtoffset', axis=1, inplace=True)
        to_df.drop('timestamp', axis=1, inplace=True)
        to_df.rename(columns={'datetime': 'timestamp'}, inplace=True)
        to_df.set_index('timestamp', inplace=True)

        # COMBINE NEW DF WITH CONTAINER DF
        if len(container) == 0:
            container = to_df
        else:
            container = pd.concat([container, to_df])

    # SORT THE FINAL OUTCOME
    container.sort_index(inplace=True)

    # REMOVE ROWS THAT ARE NOT WITHIN RANGE
    # IDK WHY THE API RETUNS INCORRECT VALUES
    container = container[container.index >= _start]
    container = container[container.index <= _end]

    print()
    print(f'EXPECTED LENGTH: {expected_length}')
    print(f'TRUE LENGTH: {len(container)} ({len(container) / expected_length}%)')
    
    return container

##########################################################################################################
##########################################################################################################

# df = create_dataset('2019-01-01 00:00:00', '2024-01-01 00:00:00', '1m', 100)
# df.to_csv('EODHD_EURUSD_HISTORICAL_2019_2024_1min.csv')

# df = create_dataset('2024-01-01 00:00:00', '2024-10-01 00:00:00', '1m', 100)
# df.to_csv('EODHD_EURUSD_FRESH_2024_2025_1min.csv')