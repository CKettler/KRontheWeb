import pandas as pd


def csv_to_dataframe(file_path, delimiter):
    df = pd.read_csv(file_path, delimiter=delimiter)
    df.columns = [x.lower() for x in df.columns]
    return df


def join_dataframes(df_first, df_second, on):
    return pd.merge(df_first, df_second, on=on, how='inner')


def get_most_recent_variable_instance(df, group_by_fields, year_field):
    groups = df.groupby(group_by_fields, as_index=False)
    count = 0
    thousands = 0
    for name, group in groups:
        group = group.sort_values(by=year_field, ascending=False)
        latest_year_index = group[year_field].argmax()
        if count == 0:
            df_new = group.loc[[latest_year_index], :]
        else:
            df_new = pd.concat([df_new, group.loc[[latest_year_index], :]])
        if count % 1000 == 0:
            thousands += 1000
            print('[processed %s groups...]' % thousands)
        count += 1
    return df_new
