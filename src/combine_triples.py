import sys

import data_preparation as prep


def usage():
    print('Not all parameters specified. Correct usage:')
    print('python combine.py path/to/dataset path/to/metadata path/to/output')


try:
    # file_paths to the data, metadata and output
    file_path_data = sys.argv[1]
    file_path_metadata = sys.argv[2]
    file_path_output = sys.argv[3]
except IndexError:
    usage()
    exit(1)

# transform the csv files to two dataframes
df_data = prep.dataset_to_triples(file_path=file_path_data, year=2017)
df_metadata = prep.csv_to_dataframe(
    file_path=file_path_metadata, key='metadata')

print("[files transformed to dataframes]")

# combine these dataframes in one dataframe and save this to a csv
df_all_data = prep.combine_dataframes(df_data, df_metadata)[['variabele', 'gebiedcode15', 'waarde','label', 'definitie']]
print("[saving data to csv...]")
df_all_data.to_csv(file_path_output)
print("[saved!]")
