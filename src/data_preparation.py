import pandas as pd
import numpy as np

def csv_to_dataframe(file_path, key):
    if key == 'data':
        dataframe = pd.read_csv(file_path, delimiter=';')
    else:
        dataframe = pd.read_csv(file_path, delimiter=',')
    dataframe.columns = [x.lower() for x in dataframe.columns]
    return dataframe


def combine_dataframes(df_data, df_metadata, key):
    if key == 1:
        df_all = pd.merge(df_data, df_metadata, on='variabele', how='inner')
    else:
        df_all = pd.merge(df_data, df_metadata, on='gebiedcode15', how='inner')
    return df_all

def last_value_variable(df):
    groups = df.groupby(['gebiedcode15', 'variabele'], as_index = False)
    count = 0
    thousands = 0
    for name, group in groups:
        group = group.sort_values(by='jaar', ascending=False)
        latest_year_index = group['jaar'].argmax()
        if count == 0:
            df_new = group.loc[[latest_year_index],:]
        else:
            df_new = pd.concat([df_new, group.loc[[latest_year_index],:]])
        if count%1000 == 0:
            thousands += 1000
            print('[processed %s groups...]' % thousands)
        count += 1
    return df_new

def dataset_to_triples(file_path, year):
    dataframe = pd.read_csv(file_path, delimiter=';')
    dataframe.columns = [x.lower() for x in dataframe.columns]
    return dataframe.loc[dataframe['jaar'] == year]\
        .groupby(['variabele'], as_index=False)\
        .agg({'gebiedcode15': areas_to_city, 'waarde': 'sum'})
