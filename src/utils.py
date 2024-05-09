import pandas as pd
import os


# fetch data from google drive reusable function
# TODO - make is reusable further by having the entire path as a parameter
def fetch_data(data_folder_name, file_name, clean_data=False, google_colab=False):
    if clean_data:
        final_path = f'{data_folder_name}/clean/{file_name}.csv'
    else:
        final_path = f'{data_folder_name}/{file_name}.csv'

    if google_colab:
        mount_drive()
        # Fetch data from google drive
        df = pd.read_csv(f"/content/drive/My Drive/10Academy/week3/data/{final_path}")
    else:
        # Fetch data from local
        df = pd.read_csv(f"../data/{final_path}")
    return df


# prompt: fetch data from google drive
def mount_drive():
    from google.colab import drive
    drive.mount('/content/drive', force_remount=True)


def fetch_chart_data(data_folder_name, clean_data=False):
    return fetch_data(data_folder_name, 'Chart data', clean_data)


def generate_dataframes(value_columns, clean_data=False):
    dataframes = {}
    for name in value_columns.keys():
        dataframes[name] = fetch_chart_data(name, clean_data)
    return dataframes


def save_preprocessed_data(df: pd.DataFrame, file_path: str) -> None:
    # Extract directory from file path
    dir_path = os.path.dirname(file_path)

    # Create the directory if it does not exist
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    # Save the DataFrame to a CSV file
    df.to_csv(file_path, index=False)


def reshape_data(dataframes, value_columns):
    reshaped_dataframes = {}
    for name, value_column in value_columns.items():
        # Pivot the data
        pivot_df = dataframes[name].pivot(index='Date', columns=name, values=value_column)

        # Reset the index
        pivot_df.reset_index(inplace=True)

        reshaped_dataframes[name] = pivot_df

    return reshaped_dataframes


def save_reshaped_data(reshaped_dataframes, value_columns):
    for name in value_columns.keys():
        # Save the reshaped data to a csv file
        save_preprocessed_data(reshaped_dataframes[name], f'../data/{name}/clean/Chart data.csv')


def preprocess_data(value_columns):
    dataframes = generate_dataframes(value_columns)
    reshaped_dataframes = reshape_data(dataframes, value_columns)
    save_reshaped_data(reshaped_dataframes, value_columns)
