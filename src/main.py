import sys

import data_preparation as prep


def usage():
    print('Not all parameters specified. Correct usage:')
    print('python main.py path/to/dataset path/to/metadata path/to/output')


# file_paths to the data, metadata and output
file_path_data = sys.argv[1]
file_path_metadata = sys.argv[2]
file_path_output = sys.argv[3]

if not (file_path_data and file_path_metadata and file_path_output):
    usage()
    exit(1)

# transform the csv files to two dataframes
df_data = prep.csv_to_dataframe(file_path=file_path_data, key='data')
df_metadata = prep.csv_to_dataframe(
    file_path=file_path_metadata, key='metadata')

print("[files transformed to dataframes]")

# combine these dataframes in one dataframe and save this to a csv
df_all_data = prep.combine_dataframes(df_data, df_metadata)
print("[saving data to csv...]")
df_all_data.to_csv(file_path_output)
print("[saved!]")
