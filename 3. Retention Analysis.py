#This file contains the main script that generates our heat maps, retention curves, and associated tables for the overarching customer/revenue retention analysis
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

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

# Revenue Retention Curve and Table
# Calculate the total revenue to use as denominator in revenue retention calculation
total_initial_revenue = df['alltime_MRR'].sum()

# Generating revenue retention and populating charts
max_months = 21
lost_revenue_per_bucket = np.zeros(max_months)

# Calculate each month's lost revenue
for index, row in df.iterrows():
    month_diff = row['month_diff']
    alltime_MRR = row['alltime_MRR']

    if pd.notna(month_diff) and pd.notna(alltime_MRR):
        if month_diff <= max_months:
            lost_revenue_per_bucket[month_diff - 1] += alltime_MRR

# Calculate revenue retention
remaining_revenue_per_bucket = np.zeros(max_months)
retention_rate_per_bucket = np.zeros(max_months)
cumulative_lost_revenue = 0

for month in range(max_months):
    cumulative_lost_revenue += lost_revenue_per_bucket[month]
    remaining_revenue = total_initial_revenue - cumulative_lost_revenue
    remaining_revenue_per_bucket[month] = remaining_revenue
    retention_rate_per_bucket[month] = (remaining_revenue / total_initial_revenue) * 100

lost_revenue_per_bucket = np.round(lost_revenue_per_bucket).astype(int)
remaining_revenue_per_bucket = np.round(remaining_revenue_per_bucket).astype(int)
retention_rate_per_bucket = np.round(retention_rate_per_bucket).astype(int)

# Create a DataFrame to display the data as a table
retention_table = pd.DataFrame({
    'Month': range(1, max_months + 1),
    'Lost Revenue': lost_revenue_per_bucket,
    'Remaining Revenue': remaining_revenue_per_bucket,
    'Retention Rate (%)': [f"{rate}%" for rate in retention_rate_per_bucket]
})

# Create table
fig, ax = plt.subplots(figsize=(10, 6))
ax.axis('tight')
ax.axis('off')
table_data = retention_table.values
column_labels = retention_table.columns
table = ax.table(cellText=table_data, colLabels=column_labels, cellLoc='center', loc='center')
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.2, 1.2)
plt.title('Revenue Retention Table')
plt.show()

# Plot revenue retention curve
plt.figure(figsize=(12, 6))
plt.plot(range(1, max_months + 1), retention_rate_per_bucket, marker='o', linestyle='-', color='b', label='Revenue Retention Rate')
plt.title('Revenue Retention Curve')
plt.xlabel('Months Since Signup')
plt.ylabel('Revenue Retention Rate (%)')
plt.xticks(range(1, max_months + 1, 1))
plt.ylim(0, 100)
plt.grid(True)
plt.legend(loc='best')
plt.show()

## Revenue Retention Heat Map and Lost Revenue by Cohort
max_months = 21
cohorts = df['cohort_month'].unique()
revenue_data = {cohort: {'total_revenue': np.zeros(max_months), 'lost_revenue': np.zeros(max_months)} for cohort in cohorts}

for index, row in df.iterrows():
    alltime_monthdiff = row['alltime_monthdiff']
    alltime_MRR = row['alltime_MRR']
    cohort = row['cohort_month']

    if pd.notna(alltime_monthdiff) and pd.notna(alltime_MRR) and pd.notna(cohort):
        for month in range(1, min(alltime_monthdiff + 1, max_months + 1)):
            revenue_data[cohort]['total_revenue'][month - 1] += alltime_MRR

for index, row in df.iterrows():
    month_diff = row['month_diff']
    alltime_MRR = row['alltime_MRR']
    cohort = row['cohort_month']

    if pd.notna(month_diff) and pd.notna(alltime_MRR) and pd.notna(cohort):
        if month_diff <= max_months:
            revenue_data[cohort]['lost_revenue'][month_diff - 1] += alltime_MRR

# Calculating retention rate
retention_data = {cohort: np.zeros(max_months) for cohort in cohorts}

for cohort in cohorts:
    total_revenue_per_bucket = revenue_data[cohort]['total_revenue']
    lost_revenue_per_bucket = revenue_data[cohort]['lost_revenue']
    remaining_revenue_per_bucket = total_revenue_per_bucket - lost_revenue_per_bucket

    for month in range(max_months):
        if total_revenue_per_bucket[month] != 0:
            retention_data[cohort][month] = (remaining_revenue_per_bucket[month] / total_revenue_per_bucket[month]) * 100

# Creating revenue retention heat map
retention_heatmap_data = pd.DataFrame(retention_data).T
retention_heatmap_data.columns = range(1, max_months + 1)
plt.figure(figsize=(16, 10))
sns.heatmap(retention_heatmap_data, annot=True, cmap="Blues", cbar=True, linewidths=.5, fmt=".2f")
plt.title('Revenue Retention Heatmap by Cohort')
plt.xlabel('Months Since Signup')
plt.ylabel('Cohort Month')
plt.show()

# Creating revenue lost heat map
lost_revenue_heatmap_data = pd.DataFrame({cohort: np.round(revenue_data[cohort]['lost_revenue']).astype(int) for cohort in cohorts}).T
lost_revenue_heatmap_data.columns = range(1, max_months + 1)
plt.figure(figsize=(16, 10))
sns.heatmap(lost_revenue_heatmap_data, annot=True, cmap="Reds", cbar=True, linewidths=.5, fmt="d", annot_kws={"size": 8})
plt.title('Lost Revenue Heatmap by Cohort')
plt.xlabel('Months Since Signup')
plt.ylabel('Cohort Month')
plt.show()

## Customer Retention Analysis Curve and Table
total_users = df.shape[0]
retained_counts = []
retention_rates = []
lost_counts = []

# Calculating lost and retained customers at the monthly level
max_months = 21
cumulative_lost_users = 0

for month in range(1, max_months + 1):

    lost_users_this_month = df[df['month_diff'] == month].shape[0]
    cumulative_lost_users += lost_users_this_month
    retained_users = total_users - cumulative_lost_users
    retention_rate = f"{round(retained_users / total_users * 100)}%"

    lost_counts.append(lost_users_this_month)
    retained_counts.append(retained_users)
    retention_rates.append(retention_rate)

# Plotting our results
retention_table = pd.DataFrame({
    'Month': range(1, max_months + 1),
    'Users Lost': lost_counts,
    'Users Retained': retained_counts,
    'Retention Rate (%)': retention_rates
})

fig, ax = plt.subplots(figsize=(10, 6))
ax.axis('tight')
ax.axis('off')
table_data = retention_table.values
column_labels = retention_table.columns
table = ax.table(cellText=table_data, colLabels=column_labels, cellLoc='center', loc='center')
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.2, 1.2)
plt.title('Customer Retention Table')
plt.show()

plt.figure(figsize=(12, 6))
plt.plot(range(1, max_months + 1), [int(rate.strip('%')) for rate in retention_rates], marker='o', linestyle='-', color='b', label='Retention Rate')
plt.title('Customer Retention Curve')
plt.xlabel('Months Since Signup')
plt.ylabel('Retention Rate (%)')
plt.xticks(range(1, max_months + 1, 1))
plt.ylim(0, 100)
plt.grid(True)
plt.legend(loc='best')
plt.show()

## Customer Retention and Customer Loss Heat Map
# Grouping month cohorts
cohort_sizes = df.groupby('cohort_month').size().reset_index(name='total_users')
cohort_data = df.groupby(['cohort_month', 'month_diff']).size().reset_index(name='n_users')
cohort_data = cohort_data.merge(cohort_sizes, on='cohort_month')

# Calculating customer retention rate per monthly cohort
adjusted_total_users = cohort_sizes.set_index('cohort_month')['total_users'].to_dict()

def calculate_adjusted_retention(row):
    cohort = row['cohort_month']
    month_diff = row['month_diff']
    if month_diff == 0:
        return 0
    previous_total_users = adjusted_total_users[cohort]
    current_total_users = previous_total_users - row['n_users']
    adjusted_total_users[cohort] = current_total_users
    return (1 - (row['n_users'] / previous_total_users)) * 100

cohort_data['retention_rate'] = cohort_data.apply(calculate_adjusted_retention, axis=1)

first_cohort = df['cohort_month'].min()
first_cohort_data = cohort_data[cohort_data['cohort_month'] == first_cohort]
initial_total_users = cohort_sizes[cohort_sizes['cohort_month'] == first_cohort]['total_users'].values[0]
total_users_tracker = [initial_total_users]

for month_diff in range(1, 22):
    if month_diff in first_cohort_data['month_diff'].values:
        n_users_removed = first_cohort_data[first_cohort_data['month_diff'] == month_diff]['n_users'].values[0]
        initial_total_users -= n_users_removed
    total_users_tracker.append(initial_total_users)

# Plotting graphs
retention_matrix = cohort_data.pivot_table(index='cohort_month', columns='month_diff', values='retention_rate')

if 0 in retention_matrix.columns:
    retention_matrix = retention_matrix.drop(columns=0)

retention_matrix = retention_matrix.fillna(0)
retention_display = retention_matrix.copy()
retention_display = retention_display.applymap(lambda x: f"{x:.2f}%" if pd.notnull(x) else "")

plt.figure(figsize=(16, 10))
sns.heatmap(retention_matrix, annot=True, fmt=".2f", cmap="Blues", linewidths=0.5)
plt.title('Customer Retention Rate Heatmap by Cohort')
plt.xlabel('Months Since Signup')
plt.ylabel('Cohort Month')
plt.show()

entries_matrix = cohort_data.pivot_table(index='cohort_month', columns='month_diff', values='n_users')

if 0 in entries_matrix.columns:
    entries_matrix = entries_matrix.drop(columns=0)

entries_matrix = entries_matrix.fillna(0)

plt.figure(figsize=(16, 10))
sns.heatmap(entries_matrix, annot=True, fmt=".0f", cmap="Reds", linewidths=0.5)
plt.title('Number of Users Lost per Month')
plt.xlabel('Months Since Signup')
plt.ylabel('Cohort Month')
plt.show()
