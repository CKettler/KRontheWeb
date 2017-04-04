import pandas as pd


def csv_to_dataframe(file_path, key):
    if key == 'data':
        dataframe = pd.read_csv(file_path, delimiter=';')
    else:
        dataframe = pd.read_csv(file_path, delimiter=',')
    dataframe.columns = [x.lower() for x in dataframe.columns]
    return(dataframe)


def combine_dataframes(df_data, df_metadata):
    df_all = pd.merge(df_data, df_metadata, on='variabele', how='inner')
    return df_all
