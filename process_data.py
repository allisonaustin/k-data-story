import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

def process_data(data, rack, start, end, datatype):
    racks = data[(data['rack'] == rack)]
    racks = racks.loc[start:end]
    cols = [col for col in racks.columns if ('check_time' in col or datatype in col and 'iosb' not in col and 'pol' not in col)]
    processed = racks.loc[:,cols]
    return processed

if __name__ == "__main__":
    file_name = 'rack_env_all.20190528(1).csv'

    rack_err = 'l07'
    rack_norm = 'm05'
    # 2019-05-28 14:00:01 - 2019-05-28 18:00:01
    start, end = 145130, 187465

    out_paths = [
        f'vue-project/data/temp-data-{rack_err}.csv',
        f'vue-project/data/temp-data-{rack_norm}.csv',
        f'vue-project/data/vol-data-{rack_err}.csv',
        f'vue-project/data/vol-data-{rack_norm}.csv'
    ]

    cols_df = pd.read_csv('data/col_names.csv', header=None)
    types_df = pd.read_csv('data/col_types.csv', header=None)

    keys = cols_df[0].tolist()
    
    k_data = pd.read_csv(f'data/{file_name}', names=keys, usecols=keys, header=None)
    k_data.check_time = pd.to_datetime(k_data.check_time)

    # temp data
    temp_data_err = process_data(k_data, rack_err, start, end, 'temp')
    temp_data_norm = process_data(k_data, rack_norm, start, end, 'temp')
    temp_data_err.to_csv(out_paths[0], index=False)
    temp_data_norm.to_csv(out_paths[1], index=False)

    # voltage data
    vol_data_err = process_data(k_data, rack_err, start, end, 'vol')
    vol_data_norm = process_data(k_data, rack_norm, start, end, 'vol')
    vol_data_err.to_csv(out_paths[2], index=False)
    vol_data_norm.to_csv(out_paths[3], index=False)