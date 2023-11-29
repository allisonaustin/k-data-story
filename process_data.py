import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

def preprocess_data(data):
    # start, end = '2019-05-28 12:00:01', '2019-05-28 15:00:01'
    start, end = 145130, 156359
    rack_err = 'l07'
    rack_norm = 'm05'
    cols = ['rack', 'check_time']

    # filtering data to only include one normal rack and the error rack
    racks = data[(data['rack'] == rack_err) | (data['rack'] == rack_norm)]
    racks = racks.loc[start:end]
    all_cols = [col for col in racks.columns if (col in cols or 'temp' in col or 'vol' in col)]
    preprocessed = racks.loc[:,all_cols]
    return preprocessed

if __name__ == "__main__":
    file_name = 'rack_env_all.20190528(1).csv'
    out_path = 'vue-project/data/k_data_processed.csv'

    cols_df = pd.read_csv('data/col_names.csv', header=None)
    types_df = pd.read_csv('data/col_types.csv', header=None)

    keys = cols_df[0].tolist()
    
    k_data = pd.read_csv(f'data/{file_name}', names=keys, usecols=keys, header=None)
    k_data.check_time = pd.to_datetime(k_data.check_time)

    preprocessed_df = preprocess_data(k_data)
    preprocessed_df.to_csv(out_path, index=False)