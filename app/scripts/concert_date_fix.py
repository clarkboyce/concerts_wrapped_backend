import pandas as pd
from datetime import datetime

# Read both CSV files
reference_df = pd.read_csv('../data/reference_event_data.csv')
concerts_df = pd.read_csv('../data/cleaned_concerts.csv')

def convert_date(date_str):
    # Convert from DD-MM-YYYY to YYYY-MM-DD
    date_obj = datetime.strptime(date_str, '%d-%m-%Y')
    return date_obj.strftime('%Y-%m-%d')

# Convert dates from reference file
new_dates = reference_df['Date'].apply(convert_date)

# Simply replace the dates in concerts file with the converted dates
concerts_df['Date'] = new_dates

# Write back to CSV
concerts_df.to_csv('../data/cleaned_concerts_2.csv', index=False)