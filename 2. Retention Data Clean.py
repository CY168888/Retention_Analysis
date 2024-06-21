#This file cleans up the given dataset by removing OID duplicates and standardizing dates for signup, conversion, and cancellation. We back fill missing MRR here and also add additional features such as geography and a free trial indicator

import pandas as pd
import pycountry
from dateutil.relativedelta import relativedelta
from datetime import datetime

file_path = 'C:/Users/chris.young/Downloads/dummy_customer_file.csv'
df = pd.read_csv(file_path, encoding='utf-8', low_memory=False)

# Data cleaning
# Remove leading/trailing spaces from column names and data
df.columns = df.columns.str.strip()
df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

# Format all date columns to be consistent
df['signup_date'] = pd.to_datetime(df['signup_date'], errors='coerce')
df['conversion_date'] = pd.to_datetime(df['conversion_date'], errors='coerce')
df['cancellation_date'] = pd.to_datetime(df['cancellation_date'], errors='coerce')
df['cancellation_date'] = df['cancellation_date'].dt.date

# Remove rows if both conversion_date AND cancellation_date are missing
df = df[~(df['conversion_date'].isna() & df['cancellation_date'].isna())]

# Standardize country names via pycountry and custom mappings for easier readability
custom_mappings = {
    'United Kingdom of Great Britain and Northern Ireland': 'United Kingdom',
    'United States of America': 'United States',
    'Korea (Republic of)': 'South Korea',
    'Korea, Republic of': 'South Korea',
    'Russian Federation': 'Russia',
    'Türkiye': 'Turkey',
    'Venezuela, Bolivarian Republic of': 'Venezuela',
    'Venezuela (Bolivarian Republic of)': 'Venezuela',
    'Bolivia (Plurinational State of)': 'Bolivia',
    'Bolivia, Plurinational State of': 'Bolivia',
    'Macedonia (FYROM)': 'North Macedonia',
    'Iran, Islamic Republic of': 'Iran',
    'Lao People\'s Democratic Republic': 'Laos',
    'Syrian Arab Republic': 'Syria',
    'United Republic of Tanzania': 'Tanzania',
    'Taiwan, Province of China': 'Taiwan',
    'Eswatini': 'Swaziland',
    "Côte d'Ivoire": 'Ivory Coast',
    'Bahamas': 'The Bahamas',
    'Moldova (Republic of)': 'Moldova',
    'Congo (Democratic Republic of the)': 'Congo',
    'Viet Nam': 'Vietnam'
}
def standardize_country_name(country_name):
    try:
        standardized_name = pycountry.countries.lookup(country_name).name
    except LookupError:
        standardized_name = country_name
    return custom_mappings.get(standardized_name, standardized_name)

df['personal_person_geo_country'] = df['personal_person_geo_country'].apply(standardize_country_name)

# Map countries to new feature, regions
country_to_region = {
    'United States': 'North America',
    'Canada': 'North America',
    'Mexico': 'North America',
    'Brazil': 'Latin America',
    'Argentina': 'Latin America',
    'Colombia': 'Latin America',
    'Chile': 'Latin America',
    'Peru': 'Latin America',
    'United Kingdom': 'Europe',
    'Germany': 'Europe',
    'France': 'Europe',
    'Italy': 'Europe',
    'Spain': 'Europe',
    'Netherlands': 'Europe',
    'Belgium': 'Europe',
    'Switzerland': 'Europe',
    'Sweden': 'Europe',
    'Norway': 'Europe',
    'Denmark': 'Europe',
    'Finland': 'Europe',
    'Ireland': 'Europe',
    'Poland': 'Europe',
    'Czechia': 'Europe',
    'Austria': 'Europe',
    'Hungary': 'Europe',
    'Portugal': 'Europe',
    'Greece': 'Europe',
    'Ukraine': 'Europe',
    'Russia': 'Europe',
    'Turkey': 'Europe',
    'Israel': 'Middle East',
    'Saudi Arabia': 'Middle East',
    'United Arab Emirates': 'Middle East',
    'Qatar': 'Middle East',
    'Kuwait': 'Middle East',
    'Oman': 'Middle East',
    'Jordan': 'Middle East',
    'Lebanon': 'Middle East',
    'Egypt': 'Middle East',
    'South Korea': 'Asia Pacific',
    'Japan': 'Asia Pacific',
    'China': 'Asia Pacific',
    'India': 'Asia Pacific',
    'Australia': 'Asia Pacific',
    'New Zealand': 'Asia Pacific',
    'Taiwan': 'Asia Pacific',
    'Hong Kong': 'Asia Pacific',
    'Singapore': 'Asia Pacific',
    'Malaysia': 'Asia Pacific',
    'Thailand': 'Asia Pacific',
    'Indonesia': 'Asia Pacific',
    'Philippines': 'Asia Pacific',
    'Vietnam': 'Asia Pacific',
    'South Africa': 'Africa',
    'Nigeria': 'Africa',
    'Kenya': 'Africa',
    'Morocco': 'Africa',
    'Algeria': 'Africa',
    'Tunisia': 'Africa',
    'Ghana': 'Africa',
    'Uganda': 'Africa',
    'Tanzania': 'Africa',
    'Ethiopia': 'Africa',
    'Ivory Coast': 'Africa',
    'Cameroon': 'Africa',
    'Zambia': 'Africa',
    'Zimbabwe': 'Africa',
    'Mozambique': 'Africa',
    'Luxembourg': 'Europe',
    'Malta': 'Europe',
    'Iceland': 'Europe',
    'Slovenia': 'Europe',
    'Lithuania': 'Europe',
    'Slovakia': 'Europe',
    'Belarus': 'Europe',
    'Trinidad and Tobago': 'Latin America',
    'Romania': 'Europe',
    'Uruguay': 'Latin America',
    'Croatia': 'Europe',
    'Estonia': 'Europe',
    'Dominican Republic': 'Latin America',
    'Kyrgyzstan': 'Asia Pacific',
    'Bulgaria': 'Europe',
    'Cambodia': 'Asia Pacific',
    'Mongolia': 'Asia Pacific',
    'Latvia': 'Europe',
    'Costa Rica': 'Latin America',
    'Georgia': 'Europe',
    'Pakistan': 'Asia Pacific',
    'Sri Lanka': 'Asia Pacific',
    'Bahrain': 'Middle East',
    'Albania': 'Europe',
    'Bosnia and Herzegovina': 'Europe',
    'Armenia': 'Asia Pacific',
    'Uzbekistan': 'Asia Pacific',
    'Ecuador': 'Latin America',
    'Maldives': 'Asia Pacific',
    'Cyprus': 'Europe',
    'North Macedonia': 'Europe',
    'El Salvador': 'Latin America',
    'Kazakhstan': 'Asia Pacific',
    'Azerbaijan': 'Asia Pacific',
    'Myanmar': 'Asia Pacific',
    'Guatemala': 'Latin America',
    'Paraguay': 'Latin America',
    'Panama': 'Latin America',
    'Honduras': 'Latin America',
    'Montenegro': 'Europe',
    'Brunei Darussalam': 'Asia Pacific',
    'Jamaica': 'Latin America',
    'Senegal': 'Africa',
    'Papua New Guinea': 'Asia Pacific',
    'Anguilla': 'Latin America',
    'Moldova': 'Europe',
    'Bolivia': 'Latin America',
    'Congo': 'Africa',
    'Serbia': 'Europe',
    'Macao': 'Asia Pacific',
    'Tanzania, United Republic of': 'Africa'
    # Add more countries as needed
}

def map_country_to_region(country_name):
    return country_to_region.get(country_name, 'Other')

df['country_region'] = df['personal_person_geo_country'].apply(map_country_to_region)

# Add and determine if a customer had a free trial, we are assuming if conversion date != start date, customer had a free trial
df['free_trial'] = ~((df['signup_date'] == df['conversion_date']) | df['conversion_date'].isna())

# Add and calculate how many months were between start date and cancellation date
def calculate_month_diff(row):
    if pd.isna(row['cancellation_date']):
        return ''
    return relativedelta(row['cancellation_date'], row['signup_date']).months + \
           relativedelta(row['cancellation_date'], row['signup_date']).years * 12

df['month_diff'] = df.apply(calculate_month_diff, axis=1)

# Calculate month difference for customers who have not cancelled
def calculate_alltime_monthdiff(row):
    if row['month_diff'] != '':
        return row['month_diff']
    else:
        end_date = datetime(2023, 1, 30)
        return relativedelta(end_date, row['signup_date']).months + \
               relativedelta(end_date, row['signup_date']).years * 12

df['alltime_monthdiff'] = df.apply(calculate_alltime_monthdiff, axis=1)

# Calculate MRR for customers who have cancelled and backfilling accordingly
def calculate_alltime_MRR(row):
    if row['current_mrr'] != 0:
        return row['current_mrr']
    else:
        if row['alltime_monthdiff'] != 0:
            return row['total_charges'] / row['alltime_monthdiff']
        else:
            return 0

df['alltime_MRR'] = df.apply(calculate_alltime_MRR, axis=1)

# Remove duplicate entries by looking at OID
df = df.groupby('oid').filter(lambda x: len(x) == 1)

# Export to local CSV
cleaned_file_path = 'C:/Users/chris.young/Downloads/cleaned_customer_file.csv'
df.to_csv(cleaned_file_path, index=False)



