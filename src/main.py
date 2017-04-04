import data_preparation as prep
import pandas as pd

# file_paths to the data and metadata
file_path_data = "../data/areas_data.csv"
file_path_meta_data = "../data/areas_metadata.csv"

# transform the csv files to two dataframes
df_data = prep.csv_to_dataframe(file_path=file_path_data, key='data')
df_metadata = prep.csv_to_dataframe(file_path=file_path_meta_data, key='metadata')
print("[files transformed to dataframes]")

# combine these dataframes in one dataframe and save this to a csv
df_all_data = prep.combine_dataframes(df_data, df_metadata)
print("[saving data to csv...]")
df_all_data.to_csv("../data/areas_all_data.csv")
print("[saved!]")

