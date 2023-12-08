import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

def process_data(data, rack, start, end, datatype):
    racks = data[(data['rack'] == rack)]
    racks = racks.loc[start:end]
    cols = [col for col in racks.columns if ('check_time' in col or datatype in col and 'iosb' not in col and 'out_air' not in col and 'in_air' not in col and 'ibc' not in col)]
    processed = racks.loc[:,cols]
    return processed

def process_rack_data(data, rack_list, start, end, err_x, err_y):
    df = data.loc[start:end]
    df = df[df['rack'].isin(rack_list)]

    temp_cols = [col for col in df.columns if ('temp' in col and 'out_air' not in col and 'in_air' not in col and 'iosb' not in col)]
    vol_cols = [col for col in df.columns if ('vol' in col and 'ibc' not in col and 'iosb' not in col)]
    fan_cols = [col for col in df.columns if ('rpm' in col)]

    a_temp = df.loc[:, [col for col in temp_cols if col[-7] == 'a']]
    b_temp = df.loc[:, [col for col in temp_cols if col[-7] == 'b']]

    a_vol = df.loc[:, [col for col in vol_cols if col[-6] == 'a']]
    b_vol = df.loc[:, [col for col in vol_cols if col[-6] == 'b']]
    c_vol = df.loc[:, [col for col in vol_cols if col[-6] == 'c']]

    a_fans = df.loc[:, [col for col in fan_cols if col[0] == 'a']]
    b_fans = df.loc[:, [col for col in fan_cols if col[0] == 'b']]

    df['pol_a_temp_min'] = a_temp.min(axis=1)
    df['pol_a_temp_max'] = a_temp.max(axis=1)
    df['pol_b_temp_min'] = b_temp.min(axis=1)
    df['pol_b_temp_max'] = b_temp.max(axis=1)
    df['pol_a_vol_min'] = a_vol.min(axis=1)
    df['pol_a_vol_max'] = a_vol.max(axis=1)
    df['pol_b_vol_min'] = b_vol.min(axis=1)
    df['pol_b_vol_max'] = b_vol.max(axis=1)
    df['pol_c_vol_min'] = c_vol.min(axis=1)
    df['pol_c_vol_max'] = c_vol.max(axis=1)
    df['a_rpm_min'] = a_fans.min(axis=1)
    df['a_rpm_max'] = a_fans.max(axis=1)
    df['b_rpm_min'] = a_fans.min(axis=1)
    df['b_rpm_max'] = a_fans.max(axis=1)

    df['distance'] = ((df['x'] - err_x) ** 2 + (df['y'] - err_y) ** 2) ** 0.5

    return df

if __name__ == "__main__":
    file_name = 'rack_env_all.20190528(1).csv'

    rack_err = 'l07'
    rack_norm = 'm05'
    err_x = 18
    err_y = 2
    # 2019-05-28 14:00:01 - 2019-05-28 18:00:01
    start, end = 145130, 187465
    time1 = '14:30:01'
    time2 = '14:55:01'
    time3 = '15:00:01'

    out_paths = [
        f'vue-project/data/temp-data-{rack_err}.csv',
        f'vue-project/data/temp-data-{rack_norm}.csv',
        f'vue-project/data/vol-data-{rack_err}.csv',
        f'vue-project/data/vol-data-{rack_norm}.csv',
        f'vue-project/data/rack-data-{time1}.csv',
        f'vue-project/data/rack-data-{time2}.csv',
        f'vue-project/data/rack-data-{time3}.csv',
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

    # rack data
    rack_list = ['k06', 'k07', 'l06', 'l07', 'm05', 'm06', 'm07']
    rack_data_1 = process_rack_data(k_data, rack_list, 150314, 151177, err_x, err_y)
    rack_data_1.to_csv(out_paths[4], index=False)
    rack_data_2 = process_rack_data(k_data, rack_list, 154634, 155497, err_x, err_y)
    rack_data_2.to_csv(out_paths[5], index=False)
    rack_data_3 = process_rack_data(k_data, rack_list, 155498, 156361, err_x, err_y)
    rack_data_3.to_csv(out_paths[6], index=False)