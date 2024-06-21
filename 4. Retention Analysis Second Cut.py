#This script takes our original analysiss on customer/revenue retention and cuts it by geography, provider and free trial

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load cleaned dataset
file_path = 'C:/Users/chris.young/Downloads/cleaned_customer_file.csv'
df = pd.read_csv(file_path, encoding='utf-8', low_memory=False)

# Last minute data formatting
df['signup_date'] = pd.to_datetime(df['signup_date'], errors='coerce')
df['cancellation_date'] = pd.to_datetime(df['cancellation_date'], errors='coerce')
df['month_diff'] = pd.to_numeric(df['month_diff'], errors='coerce').astype('Int64')
df['alltime_MRR'] = pd.to_numeric(df['alltime_MRR'], errors='coerce')
df['alltime_monthdiff'] = pd.to_numeric(df['alltime_monthdiff'], errors='coerce').astype('Int64')
df['cohort_month'] = df['signup_date'].dt.to_period('M')

## Cut by region
# Filter out the 'Other' category from country regions and define regions
df = df[df['country_region'] != 'Other']
regions = df['country_region'].unique()

# Analysis structure set up
max_months = 21
aggregated_lost_revenue_per_bucket = {region: np.zeros(max_months) for region in regions}
aggregated_total_initial_revenue = {region: 0 for region in regions}
aggregated_total_users = {region: 0 for region in regions}
aggregated_lost_counts = {region: np.zeros(max_months, dtype=int) for region in regions}

# Aggregate data for each region
for region in regions:
    df_region = df[df['country_region'] == region]

    total_initial_revenue = df_region['alltime_MRR'].sum()
    aggregated_total_initial_revenue[region] = total_initial_revenue

    for index, row in df_region.iterrows():
        month_diff = row['month_diff']
        alltime_MRR = row['alltime_MRR']

        if pd.notna(month_diff) and pd.notna(alltime_MRR):
            if month_diff <= max_months:
                aggregated_lost_revenue_per_bucket[region][month_diff - 1] += alltime_MRR

    aggregated_total_users[region] = df_region.shape[0]

# Revenue Retention Analysis
fig, ax = plt.subplots(figsize=(10, 6))

for region in regions:
    total_initial_revenue = aggregated_total_initial_revenue[region]
    lost_revenue_per_bucket = aggregated_lost_revenue_per_bucket[region]
    remaining_revenue_per_bucket = np.zeros(max_months)
    retention_rate_per_bucket = np.zeros(max_months)
    cumulative_lost_revenue = 0

    for month in range(max_months):
        cumulative_lost_revenue += lost_revenue_per_bucket[month]
        remaining_revenue = total_initial_revenue - cumulative_lost_revenue
        remaining_revenue_per_bucket[month] = remaining_revenue
        retention_rate_per_bucket[month] = (remaining_revenue / total_initial_revenue) * 100

    ax.plot(range(1, max_months + 1), retention_rate_per_bucket, marker='o', linestyle='-', label=region)

ax.set_title('Revenue Retention Curve by Region')
ax.set_xlabel('Months Since Signup')
ax.set_ylabel('Revenue Retention Rate (%)')
ax.set_xticks(range(1, max_months + 1, 1))
ax.set_ylim(0, 100)
ax.grid(True)
ax.legend(loc='best')
plt.show()

# Customer Retention Analysis
fig, ax = plt.subplots(figsize=(10, 6))

for region in regions:
    total_users = aggregated_total_users[region]
    cumulative_lost_users = 0
    retained_counts = []
    retention_rates = []
    lost_counts = aggregated_lost_counts[region]

    for month in range(1, max_months + 1):
        lost_users_this_month = df[(df['country_region'] == region) & (df['month_diff'] == month)].shape[0]
        lost_counts[month - 1] = lost_users_this_month
        cumulative_lost_users += lost_users_this_month
        retained_users = total_users - cumulative_lost_users
        retention_rate = (retained_users / total_users) * 100

        retained_counts.append(retained_users)
        retention_rates.append(retention_rate)

    ax.plot(range(1, max_months + 1), retention_rates, marker='o', linestyle='-', label=region)

ax.set_title('Customer Retention Curve by Region')
ax.set_xlabel('Months Since Signup')
ax.set_ylabel('Customer Retention Rate (%)')
ax.set_xticks(range(1, max_months + 1, 1))
ax.set_ylim(0, 100)
ax.grid(True)
ax.legend(loc='best')
plt.show()

# Create Aggregated Revenue Retention Table
revenue_retention_data = {'Month': range(1, max_months + 1)}

for region in regions:
    lost_revenue_per_bucket = aggregated_lost_revenue_per_bucket[region]
    total_initial_revenue = aggregated_total_initial_revenue[region]
    remaining_revenue_per_bucket = np.zeros(max_months)
    retention_rate_per_bucket = np.zeros(max_months)
    cumulative_lost_revenue = 0

    for month in range(max_months):
        cumulative_lost_revenue += lost_revenue_per_bucket[month]
        remaining_revenue = total_initial_revenue - cumulative_lost_revenue
        remaining_revenue_per_bucket[month] = remaining_revenue
        retention_rate_per_bucket[month] = (remaining_revenue / total_initial_revenue) * 100

    retention_rate_per_bucket = np.round(retention_rate_per_bucket).astype(int)
    revenue_retention_data[f'{region} Retention Rate (%)'] = [f"{rate}%" for rate in retention_rate_per_bucket]

revenue_retention_table = pd.DataFrame(revenue_retention_data)

fig, ax = plt.subplots(figsize=(14, 8))
ax.axis('tight')
ax.axis('off')
table_data = revenue_retention_table.values
column_labels = revenue_retention_table.columns
table = ax.table(cellText=table_data, colLabels=column_labels, cellLoc='center', loc='center')
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.2, 1.2)
plt.title('Aggregated Revenue Retention Table by Region')
plt.show()

# Create Aggregated Customer Retention Table
customer_retention_data = {'Month': range(1, max_months + 1)}

for region in regions:
    total_users = aggregated_total_users[region]
    cumulative_lost_users = 0
    retained_counts = []
    retention_rates = []
    lost_counts = aggregated_lost_counts[region]

    for month in range(1, max_months + 1):
        lost_users_this_month = df[(df['country_region'] == region) & (df['month_diff'] == month)].shape[0]
        lost_counts[month - 1] = lost_users_this_month
        cumulative_lost_users += lost_users_this_month
        retained_users = total_users - cumulative_lost_users
        retention_rate = f"{round((retained_users / total_users) * 100)}%"

        retained_counts.append(retained_users)
        retention_rates.append(retention_rate)

    customer_retention_data[f'{region} Retention Rate (%)'] = retention_rates

customer_retention_table = pd.DataFrame(customer_retention_data)

fig, ax = plt.subplots(figsize=(14, 8))
ax.axis('tight')
ax.axis('off')
table_data = customer_retention_table.values
column_labels = customer_retention_table.columns
table = ax.table(cellText=table_data, colLabels=column_labels, cellLoc='center', loc='center')
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.2, 1.2)
plt.title('Aggregated Customer Retention Table by Region')
plt.show()

## Cut by provider

# Define providers
providers = df['provider'].unique()

# Analysis structure set up
max_months = 21
aggregated_lost_revenue_per_bucket = {provider: np.zeros(max_months) for provider in providers}
aggregated_total_initial_revenue = {provider: 0 for provider in providers}
aggregated_total_users = {provider: 0 for provider in providers}
aggregated_lost_counts = {provider: np.zeros(max_months, dtype=int) for provider in providers}

# Aggregate data for each provider
for provider in providers:
    df_provider = df[df['provider'] == provider]

    total_initial_revenue = df_provider['alltime_MRR'].sum()
    aggregated_total_initial_revenue[provider] = total_initial_revenue

    for index, row in df_provider.iterrows():
        month_diff = row['month_diff']
        alltime_MRR = row['alltime_MRR']

        if pd.notna(month_diff) and pd.notna(alltime_MRR):
            if month_diff <= max_months:
                aggregated_lost_revenue_per_bucket[provider][month_diff - 1] += alltime_MRR

    aggregated_total_users[provider] = df_provider.shape[0]

# Revenue Retention Analysis
fig, ax = plt.subplots(figsize=(10, 6))

for provider in providers:
    total_initial_revenue = aggregated_total_initial_revenue[provider]
    lost_revenue_per_bucket = aggregated_lost_revenue_per_bucket[provider]
    remaining_revenue_per_bucket = np.zeros(max_months)
    retention_rate_per_bucket = np.zeros(max_months)
    cumulative_lost_revenue = 0

    for month in range(max_months):
        cumulative_lost_revenue += lost_revenue_per_bucket[month]
        remaining_revenue = total_initial_revenue - cumulative_lost_revenue
        remaining_revenue_per_bucket[month] = remaining_revenue
        retention_rate_per_bucket[month] = (remaining_revenue / total_initial_revenue) * 100

    ax.plot(range(1, max_months + 1), retention_rate_per_bucket, marker='o', linestyle='-', label=provider)

ax.set_title('Revenue Retention Curve by Provider')
ax.set_xlabel('Months Since Signup')
ax.set_ylabel('Revenue Retention Rate (%)')
ax.set_xticks(range(1, max_months + 1, 1))
ax.set_ylim(0, 100)
ax.grid(True)
ax.legend(loc='best')
plt.show()

# Customer Retention Analysis
fig, ax = plt.subplots(figsize=(10, 6))

for provider in providers:
    total_users = aggregated_total_users[provider]
    cumulative_lost_users = 0
    retained_counts = []
    retention_rates = []
    lost_counts = aggregated_lost_counts[provider]

    for month in range(1, max_months + 1):
        lost_users_this_month = df[(df['provider'] == provider) & (df['month_diff'] == month)].shape[0]
        lost_counts[month - 1] = lost_users_this_month
        cumulative_lost_users += lost_users_this_month
        retained_users = total_users - cumulative_lost_users
        retention_rate = (retained_users / total_users) * 100

        retained_counts.append(retained_users)
        retention_rates.append(retention_rate)

    ax.plot(range(1, max_months + 1), retention_rates, marker='o', linestyle='-', label=provider)

ax.set_title('Customer Retention Curve by Provider')
ax.set_xlabel('Months Since Signup')
ax.set_ylabel('Customer Retention Rate (%)')
ax.set_xticks(range(1, max_months + 1, 1))
ax.set_ylim(0, 100)
ax.grid(True)
ax.legend(loc='best')
plt.show()

# Create Aggregated Revenue Retention Table
revenue_retention_data = {'Month': range(1, max_months + 1)}

for provider in providers:
    lost_revenue_per_bucket = aggregated_lost_revenue_per_bucket[provider]
    total_initial_revenue = aggregated_total_initial_revenue[provider]
    remaining_revenue_per_bucket = np.zeros(max_months)
    retention_rate_per_bucket = np.zeros(max_months)
    cumulative_lost_revenue = 0

    for month in range(max_months):
        cumulative_lost_revenue += lost_revenue_per_bucket[month]
        remaining_revenue = total_initial_revenue - cumulative_lost_revenue
        remaining_revenue_per_bucket[month] = remaining_revenue
        retention_rate_per_bucket[month] = (remaining_revenue / total_initial_revenue) * 100

    retention_rate_per_bucket = np.round(retention_rate_per_bucket).astype(int)
    revenue_retention_data[f'{provider} Retention Rate (%)'] = [f"{rate}%" for rate in retention_rate_per_bucket]

revenue_retention_table = pd.DataFrame(revenue_retention_data)

fig, ax = plt.subplots(figsize=(14, 8))
ax.axis('tight')
ax.axis('off')
table_data = revenue_retention_table.values
column_labels = revenue_retention_table.columns
table = ax.table(cellText=table_data, colLabels=column_labels, cellLoc='center', loc='center')
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.2, 1.2)
plt.title('Aggregated Revenue Retention Table by Provider')
plt.show()

# Create Aggregated Customer Retention Table
customer_retention_data = {'Month': range(1, max_months + 1)}

for provider in providers:
    total_users = aggregated_total_users[provider]
    cumulative_lost_users = 0
    retained_counts = []
    retention_rates = []
    lost_counts = aggregated_lost_counts[provider]

    for month in range(1, max_months + 1):
        lost_users_this_month = df[(df['provider'] == provider) & (df['month_diff'] == month)].shape[0]
        lost_counts[month - 1] = lost_users_this_month
        cumulative_lost_users += lost_users_this_month
        retained_users = total_users - cumulative_lost_users
        retention_rate = f"{round((retained_users / total_users) * 100)}%"

        retained_counts.append(retained_users)
        retention_rates.append(retention_rate)

    customer_retention_data[f'{provider} Retention Rate (%)'] = retention_rates

customer_retention_table = pd.DataFrame(customer_retention_data)

fig, ax = plt.subplots(figsize=(14, 8))
ax.axis('tight')
ax.axis('off')
table_data = customer_retention_table.values
column_labels = customer_retention_table.columns
table = ax.table(cellText=table_data, colLabels=column_labels, cellLoc='center', loc='center')
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.2, 1.2)
plt.title('Aggregated Customer Retention Table by Provider')
plt.show()

## Cut by free trial

# Define free_trial categories
free_trial_categories = df['free_trial'].unique()

# Analysis structure set up
max_months = 21
aggregated_lost_revenue_per_bucket = {category: np.zeros(max_months) for category in free_trial_categories}
aggregated_total_initial_revenue = {category: 0 for category in free_trial_categories}
aggregated_total_users = {category: 0 for category in free_trial_categories}
aggregated_lost_counts = {category: np.zeros(max_months, dtype=int) for category in free_trial_categories}

# Aggregate data for each free_trial category
for category in free_trial_categories:
    df_category = df[df['free_trial'] == category]

    total_initial_revenue = df_category['alltime_MRR'].sum()
    aggregated_total_initial_revenue[category] = total_initial_revenue

    for index, row in df_category.iterrows():
        month_diff = row['month_diff']
        alltime_MRR = row['alltime_MRR']

        if pd.notna(month_diff) and pd.notna(alltime_MRR):
            if month_diff <= max_months:
                aggregated_lost_revenue_per_bucket[category][month_diff - 1] += alltime_MRR

    aggregated_total_users[category] = df_category.shape[0]

# Revenue Retention Analysis
fig, ax = plt.subplots(figsize=(10, 6))

for category in free_trial_categories:
    total_initial_revenue = aggregated_total_initial_revenue[category]
    lost_revenue_per_bucket = aggregated_lost_revenue_per_bucket[category]
    remaining_revenue_per_bucket = np.zeros(max_months)
    retention_rate_per_bucket = np.zeros(max_months)
    cumulative_lost_revenue = 0

    for month in range(max_months):
        cumulative_lost_revenue += lost_revenue_per_bucket[month]
        remaining_revenue = total_initial_revenue - cumulative_lost_revenue
        remaining_revenue_per_bucket[month] = remaining_revenue
        retention_rate_per_bucket[month] = (remaining_revenue / total_initial_revenue) * 100

    ax.plot(range(1, max_months + 1), retention_rate_per_bucket, marker='o', linestyle='-', label=str(category))

ax.set_title('Revenue Retention Curve by Free Trial')
ax.set_xlabel('Months Since Signup')
ax.set_ylabel('Revenue Retention Rate (%)')
ax.set_xticks(range(1, max_months + 1, 1))
ax.set_ylim(0, 100)
ax.grid(True)
ax.legend(loc='best')
plt.show()

# Customer Retention Analysis
fig, ax = plt.subplots(figsize=(10, 6))

for category in free_trial_categories:
    total_users = aggregated_total_users[category]
    cumulative_lost_users = 0
    retained_counts = []
    retention_rates = []
    lost_counts = aggregated_lost_counts[category]

    for month in range(1, max_months + 1):
        lost_users_this_month = df[(df['free_trial'] == category) & (df['month_diff'] == month)].shape[0]
        lost_counts[month - 1] = lost_users_this_month
        cumulative_lost_users += lost_users_this_month
        retained_users = total_users - cumulative_lost_users
        retention_rate = (retained_users / total_users) * 100

        retained_counts.append(retained_users)
        retention_rates.append(retention_rate)

    ax.plot(range(1, max_months + 1), retention_rates, marker='o', linestyle='-', label=str(category))

ax.set_title('Customer Retention Curve by Free Trial')
ax.set_xlabel('Months Since Signup')
ax.set_ylabel('Customer Retention Rate (%)')
ax.set_xticks(range(1, max_months + 1, 1))
ax.set_ylim(0, 100)
ax.grid(True)
ax.legend(loc='best')
plt.show()

# Create Aggregated Revenue Retention Table
revenue_retention_data = {'Month': range(1, max_months + 1)}

for category in free_trial_categories:
    lost_revenue_per_bucket = aggregated_lost_revenue_per_bucket[category]
    total_initial_revenue = aggregated_total_initial_revenue[category]
    remaining_revenue_per_bucket = np.zeros(max_months)
    retention_rate_per_bucket = np.zeros(max_months)
    cumulative_lost_revenue = 0

    for month in range(max_months):
        cumulative_lost_revenue += lost_revenue_per_bucket[month]
        remaining_revenue = total_initial_revenue - cumulative_lost_revenue
        remaining_revenue_per_bucket[month] = remaining_revenue
        retention_rate_per_bucket[month] = (remaining_revenue / total_initial_revenue) * 100

    retention_rate_per_bucket = np.round(retention_rate_per_bucket).astype(int)
    revenue_retention_data[f'{category} Retention Rate (%)'] = [f"{rate}%" for rate in retention_rate_per_bucket]

revenue_retention_table = pd.DataFrame(revenue_retention_data)

fig, ax = plt.subplots(figsize=(14, 8))
ax.axis('tight')
ax.axis('off')
table_data = revenue_retention_table.values
column_labels = revenue_retention_table.columns
table = ax.table(cellText=table_data, colLabels=column_labels, cellLoc='center', loc='center')
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.2, 1.2)
plt.title('Aggregated Revenue Retention Table by Free Trial')
plt.show()

# Create Aggregated Customer Retention Table
customer_retention_data = {'Month': range(1, max_months + 1)}

for category in free_trial_categories:
    total_users = aggregated_total_users[category]
    cumulative_lost_users = 0
    retained_counts = []
    retention_rates = []
    lost_counts = aggregated_lost_counts[category]

    for month in range(1, max_months + 1):
        lost_users_this_month = df[(df['free_trial'] == category) & (df['month_diff'] == month)].shape[0]
        lost_counts[month - 1] = lost_users_this_month
        cumulative_lost_users += lost_users_this_month
        retained_users = total_users - cumulative_lost_users
        retention_rate = f"{round((retained_users / total_users) * 100)}%"

        retained_counts.append(retained_users)
        retention_rates.append(retention_rate)

    customer_retention_data[f'{category} Retention Rate (%)'] = retention_rates

customer_retention_table = pd.DataFrame(customer_retention_data)

fig, ax = plt.subplots(figsize=(14, 8))
ax.axis('tight')
ax.axis('off')
table_data = customer_retention_table.values
column_labels = customer_retention_table.columns
table = ax.table(cellText=table_data, colLabels=column_labels, cellLoc='center', loc='center')
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.2, 1.2)
plt.title('Aggregated Customer Retention Table by Free Trial')
plt.show()
