import sys

from data_preparation import (
    join_dataframes, csv_to_dataframe, get_most_recent_variable_instance)


def usage():
    print('Not all parameters specified. Correct usage:')
    print('python combine.py path/to/dataset path/to/metadata path/to/output')


try:
    file_path_data = sys.argv[1]  # data csv
    file_path_metadata = sys.argv[2]  # metadata csv
    file_path_metadata_2 = sys.argv[3]  # locations csv
    file_path_output = sys.argv[4]  # out csv
except IndexError:
    usage()
    exit(1)


df_data = get_most_recent_variable_instance(
    csv_to_dataframe(file_path_data, ';'),
    ['gebiedcode15', 'variabele'],
    'jaar')

df_metadata = csv_to_dataframe(file_path_metadata, ',')
df_locations = csv_to_dataframe(file_path_metadata_2, ',')

df_locations = df_locations.loc[:, ['gebiedcode15', 'gebiednaam', 'sdnaam']]

print("[files transformed to dataframes]")

output_fields = ['variabele', 'gebiedcode15', 'waarde', 'label', 'definitie']
# combine these dataframes in one dataframe and save this to a csv
combined_df = join_dataframes(
    df_data, df_metadata, 'variabele')[output_fields]
combined_df = join_dataframes(combined_df, df_locations, 'gebiedcode15')

print("[saving data to csv...]")
combined_df.to_csv(file_path_output)
print("[saved!]")
